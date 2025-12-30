from decimal import Decimal
from typing import Any, TypedDict
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain, Gas
from api.chain.contract import Contract

from api.investment.exchange.exchange import (
    ExchangeConvertedBalance,
    Exchange,
    ExchangeSignableSwap,
    SignableTransaction,
)
from api.investment.infrastructure.zero_x.exception.swap_insufficient_liquidity import (
    SwapInsufficientLiquidity,
)
from api.investment.infrastructure.zero_x.exception.swap_validation_failed import (
    SwapValidationFailed,
)
from api.investment.infrastructure.zero_x.quote import (
    InsufficientLiquidityQuote,
    Quote,
)
from api.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from api.investment.investment_parameters import InvestmentParameters

from api.chain.balance import Balance
from api.protocol.token import Token
from web3 import AsyncWeb3

from eth_account.signers.local import LocalAccount

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

    async def get_signable_swap(
        self,
        sell_balance: Balance[Token],
        buy_balance: Balance[Token],
        investment_parameters: InvestmentParameters,
    ) -> ExchangeSignableSwap:
        chain_id = await self.chain.get_chain_id()

        amount_atomic, _decimals = await self.chain.convert_amount_to_amount_atomic(
            token=sell_balance.asset,
            amount_readable=sell_balance.amount,
        )

        quote_result = await self.api_client.get_quote(
            chain_id=chain_id,
            taker=self.account.address,
            sell_token=sell_balance.asset.address,
            buy_token=buy_balance.asset.address,
            amount=amount_atomic,
            slippage_bps=self.__compute_slippage_tolerance_in_bps(
                investment_parameters.slippage_tolerance_in_percentage
            ),
            investment_parameters=investment_parameters,
        )
        quote = quote_result.root

        if isinstance(quote, InsufficientLiquidityQuote):
            raise SwapInsufficientLiquidity()

        signature_payload = self.__get_signature_payload(quote)
        transaction = SignableTransaction(
            type="SEND",
            amount=int(quote.transaction.value) if quote.transaction.value else 0,
            gas=Gas(
                gas=int(quote.transaction.gas) if quote.transaction.gas else None,
                gas_price=int(quote.transaction.gasPrice)
                if quote.transaction.gasPrice
                else None,
            ),
            data=quote.transaction.data,
            to_address=quote.transaction.to,
        )

        sell_balance_amount_atomic = int(quote.sellAmount)
        buy_balance_amount_atomic = int(quote.buyAmount)

        sell_amount, sell_decimals = await self.chain.convert_amount_atomic_to_amount(
            amount_atomic=sell_balance_amount_atomic, token=sell_balance.asset
        )
        buy_amount, buy_decimals = await self.chain.convert_amount_atomic_to_amount(
            amount_atomic=buy_balance_amount_atomic,
            token=buy_balance.asset,
        )

        return ExchangeSignableSwap(
            sell_balance=BalanceAtomic(
                asset=sell_balance.asset,
                amount=sell_amount,
                amount_atomic=sell_balance_amount_atomic,
                decimals=sell_decimals,
            ),
            buy_balance=BalanceAtomic(
                asset=buy_balance.asset,
                amount=buy_amount,
                amount_atomic=buy_balance_amount_atomic,
                decimals=buy_decimals,
            ),
            transaction=transaction,
            signature_payload=signature_payload,
        )

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
            print(e)
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

    def __get_signature_payload(self, quote: Quote) -> dict[str, Any] | None:
        if quote.permit2 is None:
            return None

        return quote.permit2.eip712

    def __compute_slippage_tolerance_in_bps(
        self, slippage_tolerance_in_percentage: Decimal
    ) -> Decimal:
        return slippage_tolerance_in_percentage * 100

    def __is_same_token(self, token1: Token, token2: Token) -> bool:
        return token1.address.lower() == token2.address.lower()
