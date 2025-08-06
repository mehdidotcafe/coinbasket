from decimal import Decimal
from attr import dataclass
from invest_agent.chain.asset_balance import BasketBalance
from invest_agent.chain.balance import Balance
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

    def __init__(self, exchange: Exchange):
        self.exchange = exchange

    async def execute(
        self, asset_swap_price_info: AssetSwapPriceInfo
    ) -> ConvertedBalance:
        investment_parameters = InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        )

        if isinstance(asset_swap_price_info.buy_asset, Basket) and isinstance(
            asset_swap_price_info.sell_asset, Token
        ):
            price = await self.exchange.convert_balance_to_token(
                balance=Balance(
                    token=asset_swap_price_info.sell_asset,
                    amount=asset_swap_price_info.sell_asset_amount,
                ),
                token=DEFAULT_USD_TOKEN,
                investment_parameters=investment_parameters,
            )
            return ConvertedBalance(
                sell_balance=Balance(
                    token=asset_swap_price_info.sell_asset,
                    amount=asset_swap_price_info.sell_asset_amount,
                ),
                buy_balance=BasketBalance(
                    basket=asset_swap_price_info.buy_asset,
                    amount=price.buy_balance.amount
                    / asset_swap_price_info.buy_asset.denomination,
                ),
            )

        if isinstance(asset_swap_price_info.buy_asset, Token) and isinstance(
            asset_swap_price_info.sell_asset, Basket
        ):
            price = await self.exchange.convert_balance_to_token(
                balance=Balance(
                    token=DEFAULT_USD_TOKEN,
                    amount=asset_swap_price_info.sell_asset_amount
                    * asset_swap_price_info.sell_asset.denomination,
                ),
                token=asset_swap_price_info.buy_asset,
                investment_parameters=investment_parameters,
            )

            return ConvertedBalance(
                sell_balance=BasketBalance(
                    basket=asset_swap_price_info.sell_asset,
                    amount=asset_swap_price_info.sell_asset_amount,
                ),
                buy_balance=price.buy_balance,
            )

        if isinstance(asset_swap_price_info.sell_asset, Token) and isinstance(
            asset_swap_price_info.buy_asset, Token
        ):
            price = await self.exchange.convert_balance_to_token(
                balance=Balance(
                    token=asset_swap_price_info.sell_asset,
                    amount=asset_swap_price_info.sell_asset_amount,
                ),
                token=asset_swap_price_info.buy_asset,
                investment_parameters=investment_parameters,
            )
            return ConvertedBalance(
                sell_balance=Balance(
                    token=asset_swap_price_info.sell_asset,
                    amount=asset_swap_price_info.sell_asset_amount,
                ),
                buy_balance=price.buy_balance,
            )

        raise CannotSwapBasketForAnotherException
