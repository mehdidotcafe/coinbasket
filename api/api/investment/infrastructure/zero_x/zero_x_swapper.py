from decimal import Decimal
from typing import Any, TypedDict
from api.address.address import Address
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
from api.protocol.asset import Asset
from web3 import AsyncWeb3

RETRY_ATTEMPTS = 5


class Configuration(TypedDict):
    bsc_rpc_url: str


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

    def get_name(self):
        return "0X_PROTOCOL"

    async def get_signable_swap(
        self,
        taker: Address,
        sell_balance: Balance[Asset],
        buy_balance: Balance[Asset],
        investment_parameters: InvestmentParameters,
    ) -> ExchangeSignableSwap:
        chain_id = await self.chain.get_chain_id()

        decimals = sell_balance.asset.decimals
        amount_atomic = int(sell_balance.amount * (10**decimals))

        quote_result = await self.api_client.get_quote(
            chain_id=chain_id,
            taker=taker,
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

        sell_decimals = sell_balance.asset.decimals
        sell_amount = Decimal(sell_balance_amount_atomic) / Decimal(10**sell_decimals)

        buy_decimals = buy_balance.asset.decimals
        buy_amount = Decimal(buy_balance_amount_atomic) / Decimal(10**buy_decimals)

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

    async def convert_balance_to_asset(
        self,
        taker: Address,
        balance: BalanceAtomic[Asset],
        asset: Asset,
        investment_parameters: InvestmentParameters,
    ) -> ExchangeConvertedBalance:
        if self.__is_same_token(balance.asset, asset):
            return ExchangeConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=balance.asset,
                    amount=balance.amount,
                    amount_atomic=balance.amount_atomic,
                    decimals=balance.decimals,
                ),
                buy_balance=BalanceAtomic(
                    asset=asset,
                    amount=balance.amount,
                    amount_atomic=balance.amount_atomic,
                    decimals=balance.decimals,
                ),
            )

        decimals = balance.asset.decimals
        amount_atomic = int(balance.amount * (10**decimals))

        try:
            price = await self.api_client.get_price(
                chain_id=await self.chain.get_chain_id(),
                taker=taker,
                sell_token=balance.asset.address,
                buy_token=asset.address,
                amount=amount_atomic,
                investment_parameters=investment_parameters,
            )
        except SwapValidationFailed as e:
            print(e)
            token_decimals = await self.chain.get_token_decimals(asset.address)

            return ExchangeConvertedBalance(
                sell_balance=balance,
                buy_balance=BalanceAtomic(
                    asset=asset,
                    amount=Decimal("0"),
                    amount_atomic=0,
                    decimals=token_decimals,
                ),
            )

        sell_balance_amount_atomic = int(price.sellAmount)
        buy_balance_amount_atomic = int(price.buyAmount)

        sell_decimals = balance.asset.decimals
        sell_amount = Decimal(sell_balance_amount_atomic) / Decimal(10**sell_decimals)

        buy_decimals = asset.decimals
        buy_amount = Decimal(buy_balance_amount_atomic) / Decimal(10**buy_decimals)

        sell_decimals = balance.asset.decimals
        sell_amount = Decimal(sell_balance_amount_atomic) / Decimal(10**sell_decimals)

        buy_decimals = asset.decimals
        buy_amount = Decimal(buy_balance_amount_atomic) / Decimal(10**buy_decimals)

        return ExchangeConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=balance.asset,
                amount=sell_amount,
                amount_atomic=sell_balance_amount_atomic,
                decimals=sell_decimals,
            ),
            buy_balance=BalanceAtomic(
                asset=asset,
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

    def __is_same_token(self, asset1: Asset, asset2: Asset) -> bool:
        return asset1.address.lower() == asset2.address.lower()
