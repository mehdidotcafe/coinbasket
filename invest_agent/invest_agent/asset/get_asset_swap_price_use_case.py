from decimal import Decimal
from attr import dataclass
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from invest_agent.investment.exchange.exchange import ConvertedBalance, Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from protocol.basket import Basket
from protocol.token import Token


@dataclass
class AssetSwapPriceInfo:
    sell_asset: Token | Basket
    sell_asset_amount: Decimal
    buy_asset: Token | Basket


# TODO: Add to env variables
DEFAULT_USD_TOKEN = Token(
    id="bsc:0x55d398326f99059ff775485246999027b3197955",
    name="Tether USD",
    display_name="Tether USD",
    ticker="USDT",
    address="0x55d398326f99059ff775485246999027b3197955",
)


class GetAssetSwapPriceUseCase:
    """Use case for getting the swap price of a pair of assets. Basket against basket is not supported"""

    def __init__(self, exchange: Exchange, chain: Chain):
        self.exchange = exchange
        self.chain = chain

    async def execute(
        self, asset_swap_price_info: AssetSwapPriceInfo
    ) -> ConvertedBalance:
        investment_parameters = InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        )

        if isinstance(asset_swap_price_info.buy_asset, Basket) and isinstance(
            asset_swap_price_info.sell_asset, Token
        ):
            amount_atomic, decimals = await self.chain.convert_amount_to_amount_atomic(
                token=asset_swap_price_info.sell_asset,
                amount_readable=asset_swap_price_info.sell_asset_amount,
            )
            converted_balance = await self.exchange.convert_balance_to_token(
                balance=BalanceAtomic(
                    asset=asset_swap_price_info.sell_asset,
                    amount=asset_swap_price_info.sell_asset_amount,
                    amount_atomic=amount_atomic,
                    decimals=decimals,
                ),
                token=DEFAULT_USD_TOKEN,
                investment_parameters=investment_parameters,
            )

            (
                sell_amount_atomic,
                sell_decimals,
            ) = await self.chain.convert_amount_to_amount_atomic(
                token=asset_swap_price_info.sell_asset,
                amount_readable=asset_swap_price_info.sell_asset_amount,
            )

            return ConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=asset_swap_price_info.sell_asset,
                    amount=asset_swap_price_info.sell_asset_amount,
                    amount_atomic=sell_amount_atomic,
                    decimals=sell_decimals,
                ),
                buy_balance=BalanceAtomic(
                    asset=asset_swap_price_info.buy_asset,
                    amount=converted_balance.buy_balance.amount
                    / asset_swap_price_info.buy_asset.denomination,
                    amount_atomic=int(
                        converted_balance.buy_balance.amount_atomic
                        / asset_swap_price_info.buy_asset.denomination
                    ),
                    decimals=converted_balance.buy_balance.decimals,
                ),
            )

        if isinstance(asset_swap_price_info.buy_asset, Token) and isinstance(
            asset_swap_price_info.sell_asset, Basket
        ):
            amount = (
                asset_swap_price_info.sell_asset_amount
                * asset_swap_price_info.sell_asset.denomination
            )

            amount_atomic, decimals = await self.chain.convert_amount_to_amount_atomic(
                token=DEFAULT_USD_TOKEN, amount_readable=amount
            )

            converted_balance = await self.exchange.convert_balance_to_token(
                balance=BalanceAtomic(
                    asset=DEFAULT_USD_TOKEN,
                    amount=amount,
                    amount_atomic=amount_atomic,
                    decimals=decimals,
                ),
                token=asset_swap_price_info.buy_asset,
                investment_parameters=investment_parameters,
            )

            (
                sell_amount_atomic,
                sell_decimals,
            ) = await self.chain.convert_amount_to_amount_atomic(
                token=DEFAULT_USD_TOKEN,
                amount_readable=asset_swap_price_info.sell_asset_amount,
            )

            return ConvertedBalance(
                sell_balance=BalanceAtomic(
                    asset=asset_swap_price_info.sell_asset,
                    amount=asset_swap_price_info.sell_asset_amount,
                    amount_atomic=sell_amount_atomic,
                    decimals=sell_decimals,
                ),
                buy_balance=converted_balance.buy_balance,
            )

        if isinstance(asset_swap_price_info.sell_asset, Token) and isinstance(
            asset_swap_price_info.buy_asset, Token
        ):
            amount_atomic, decimals = await self.chain.convert_amount_to_amount_atomic(
                        token=asset_swap_price_info.sell_asset,
                        amount_readable=asset_swap_price_info.sell_asset_amount,
                    )

            converted_balance = await self.exchange.convert_balance_to_token(
                balance=BalanceAtomic(
                    asset=asset_swap_price_info.sell_asset,
                    amount=asset_swap_price_info.sell_asset_amount,
                    amount_atomic=amount_atomic,
                    decimals=decimals,
                ),
                token=asset_swap_price_info.buy_asset,
                investment_parameters=investment_parameters,
            )
            return converted_balance

        raise CannotSwapBasketForAnotherException
