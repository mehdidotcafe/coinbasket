from decimal import Decimal
from typing import TypedDict
from hexbytes import HexBytes
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain, Gas
from invest_agent.chain.contract import Contract

from invest_agent.investment.exchange.exchange import (
    ExchangeConvertedBalance,
    Exchange,
    TransactionData,
)
from invest_agent.investment.infrastructure.zero_x.exception.swap_insufficient_liquidity import (
    SwapInsufficientLiquidity,
)
from invest_agent.investment.infrastructure.zero_x.exception.swap_validation_failed import (
    SwapValidationFailed,
)
from invest_agent.investment.infrastructure.zero_x.price import Price
from invest_agent.investment.infrastructure.zero_x.quote import (
    InsufficientLiquidityQuote,
    Quote,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from invest_agent.investment.investment_parameters import InvestmentParameters

from invest_agent.investment.order.order import Order
from protocol.token import Token
from web3 import AsyncWeb3

from eth_account.signers.local import LocalAccount
from eth_account.datastructures import (
    SignedMessage,
)

RETRY_ATTEMPTS = 5


class Configuration(TypedDict):
    bsc_rpc_url: str
    private_key: str


# LINK: https://0x.org/docs/api#tag/Swap/operation/swap::permit2::getPrice
# LINK: https://0x.org/docs/0x-swap-api/guides/swap-tokens-with-0x-swap-api
class ZeroXSwapper(Exchange):
    def __init__(
        self,
        api_client: ZeroXApiClient,
        chain: Chain,
        contract: Contract,
        configuration: Configuration,
        w3: AsyncWeb3,
    ):
        self.api_client = api_client
        self.chain = chain
        self.contract = contract
        self.bsc_rpc_url = configuration["bsc_rpc_url"]

        self.w3 = w3
        self.account: LocalAccount = self.w3.eth.account.from_key(
            private_key=configuration["private_key"]
        )

    def get_name(self):
        return "0X_PROTOCOL"

    async def build_transactions(
        self,
        order: Order,
        investment_parameters: InvestmentParameters,
    ) -> list[TransactionData]:
        transactions_data: list[TransactionData | None] = []
        chain_id = await self.chain.get_chain_id()

        amount_atomic, _decimals = await self.chain.convert_amount_to_amount_atomic(
            token=order.sell_balance.asset,
            amount_readable=order.sell_balance.amount,
        )

        price = await self.api_client.get_price(
            chain_id=chain_id,
            taker=self.account.address,
            sell_token=order.sell_balance.asset.address,
            amount=amount_atomic,
            buy_token=order.buy_balance.asset.address,
            sell_entire_balance=True,
            slippage_bps=self.__compute_slippage_tolerance_in_bps(
                investment_parameters.slippage_tolerance_in_percentage
            ),
            investment_parameters=investment_parameters,
        )

        transactions_data.append(
            self.__build_approve_allowance(price=price, token=order.sell_balance.asset)
        )

        quote_result = await self.api_client.get_quote(
            chain_id=chain_id,
            taker=self.account.address,
            sell_token=order.sell_balance.asset.address,
            buy_token=order.buy_balance.asset.address,
            amount=amount_atomic,
            slippage_bps=self.__compute_slippage_tolerance_in_bps(
                investment_parameters.slippage_tolerance_in_percentage
            ),
            investment_parameters=investment_parameters,
        )
        quote = quote_result.root

        if isinstance(quote, InsufficientLiquidityQuote):
            raise SwapInsufficientLiquidity()

        transactions_data.append(
            TransactionData(
                type="SEND",
                amount=int(quote.transaction.value) if quote.transaction.value else 0,
                gas=Gas(
                    gas=int(quote.transaction.gas) if quote.transaction.gas else None,
                    gas_price=int(quote.transaction.gasPrice)
                    if quote.transaction.gasPrice
                    else None,
                ),
                to_address=quote.transaction.to,
                encoded_input=self.__make_encoded_input(quote),
            )
        )

        return [
            transaction_data
            for transaction_data in transactions_data
            if transaction_data is not None
        ]

    async def convert_balance_to_token(
        self,
        balance: BalanceAtomic[Token],
        token: Token,
        investment_parameters: InvestmentParameters,
    ):
        if self.__is_same_token(balance.asset, token):
            return ExchangeConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=balance.asset,
                    amount=balance.amount,
                    amount_atomic=balance.amount_atomic,
                    decimals=balance.decimals,
                ),
                buy_balance=BalanceAtomic(
                    asset=token,
                    amount=balance.amount,
                    amount_atomic=balance.amount_atomic,
                    decimals=balance.decimals,
                ),
            )

        amount_atomic, _decimals = await self.chain.convert_amount_to_amount_atomic(
            token=balance.asset,
            amount_readable=balance.amount,
        )

        try:
            price = await self.api_client.get_price(
                chain_id=await self.chain.get_chain_id(),
                taker=self.account.address,
                sell_token=balance.asset.address,
                buy_token=token.address,
                amount=amount_atomic,
                investment_parameters=investment_parameters,
            )
        except SwapValidationFailed as e:
            token_decimals = await self.chain.get_token_decimals(token.address)

            return ExchangeConvertedBalance(
                sell_balance=balance,
                buy_balance=BalanceAtomic(
                    asset=token,
                    amount=Decimal("0"),
                    amount_atomic=0,
                    decimals=token_decimals,
                ),
            )

        sell_balance_amount_atomic = int(price.sellAmount)
        buy_balance_amount_atomic = int(price.buyAmount)

        sell_amount, sell_decimals = await self.chain.convert_amount_atomic_to_amount(
            amount_atomic=sell_balance_amount_atomic, token=balance.asset
        )
        buy_amount, buy_decimals = await self.chain.convert_amount_atomic_to_amount(
            amount_atomic=buy_balance_amount_atomic,
            token=token,
        )

        return ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=balance.asset,
                amount=sell_amount,
                amount_atomic=sell_balance_amount_atomic,
                decimals=sell_decimals,
            ),
            buy_balance=BalanceAtomic(
                asset=token,
                amount=buy_amount,
                amount_atomic=buy_balance_amount_atomic,
                decimals=buy_decimals,
            ),
        )

    def __make_encoded_input(self, quote: Quote):
        if quote.permit2 is None:
            return quote.transaction.data

        signature: SignedMessage = self.w3.eth.account.sign_typed_data(
            full_message=quote.permit2.eip712,
            private_key=self.account.key,
        )

        signature_hex = signature.signature.to_0x_hex()

        signature_length_hex = self.__compute_signature_length_in_hex(
            signature.signature
        )

        transaction_data = quote.transaction.data

        return "0x" + "".join(
            [
                h[2:]
                for h in [
                    transaction_data,
                    signature_length_hex,
                    signature_hex,
                ]
            ]
        )

    def __compute_signature_length_in_hex(self, signature: HexBytes) -> str:
        sig_len = len(signature)

        sig_len_hex = "0x" + sig_len.to_bytes(32, "big").hex()
        return sig_len_hex

    def __build_approve_allowance(self, price: Price, token: Token):
        if self.chain.is_native_token(token) or price.issues.allowance is None:
            return None

        encoded_input = self.contract.make_approve_transaction_input(
            token_address=token.address,
            spender_address=price.issues.allowance.spender,
            amount=Decimal(2**256 - 1),
        )

        return TransactionData(
            type="SIGN",
            amount=0,
            encoded_input=encoded_input,
            to_address=token.address,
        )

    def __compute_slippage_tolerance_in_bps(
        self, slippage_tolerance_in_percentage: Decimal
    ) -> Decimal:
        return slippage_tolerance_in_percentage * 100

    def __is_same_token(self, token1: Token, token2: Token) -> bool:
        return token1.address.lower() == token2.address.lower()
