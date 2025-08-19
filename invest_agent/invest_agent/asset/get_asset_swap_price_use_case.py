from decimal import Decimal
from attr import dataclass
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from protocol.basket import Basket
from protocol.token import Token


@dataclass
class AssetSwapPriceInfo:
    sell_asset: Token | Basket
    sell_asset_amount: Decimal
    buy_asset: Token | Basket


@dataclass
class ConvertedBalance:
    sell_balance: BalanceAtomic
    buy_balance: BalanceAtomic


class GetAssetSwapPriceUseCase:
    """Use case for getting the swap price of a pair of assets. Basket against basket is not supported"""

    def __init__(self, exchange: Exchange, chain: Chain):
        self.exchange = exchange
        self.chain = chain

    async def execute(
        self, asset_swap_price_info: AssetSwapPriceInfo
    ) -> ConvertedBalance:
        if isinstance(asset_swap_price_info.sell_asset, Basket) and isinstance(
            asset_swap_price_info.buy_asset, Basket
        ):
            raise CannotSwapBasketForAnotherException

        investment_parameters = InvestmentParameters(
            slippage_tolerance_in_percentage=Decimal("1"),
        )
        pricing_buy_token = asset_swap_price_info.buy_asset.get_pricing_token()
        pricing_sell_token = asset_swap_price_info.sell_asset.get_pricing_token()
        pricing_sell_token_amount = (
            asset_swap_price_info.sell_asset_amount
            * asset_swap_price_info.sell_asset.get_denomination()
        )

        amount_atomic, decimals = await self.chain.convert_amount_to_amount_atomic(
            token=pricing_sell_token,
            amount_readable=pricing_sell_token_amount,
        )
        converted_balance = await self.exchange.convert_balance_to_token(
            balance=BalanceAtomic(
                asset=pricing_sell_token,
                amount=pricing_sell_token_amount,
                amount_atomic=amount_atomic,
                decimals=decimals,
            ),
            token=pricing_buy_token,
            investment_parameters=investment_parameters,
        )

        return ConvertedBalance(
            sell_balance=BalanceAtomic(
                asset=asset_swap_price_info.sell_asset,
                amount=converted_balance.sell_balance.amount
                / pricing_sell_token.get_denomination(),
                amount_atomic=int(
                    converted_balance.sell_balance.amount_atomic
                    / pricing_sell_token.get_denomination()
                ),
                decimals=decimals,
            ),
            buy_balance=BalanceAtomic(
                asset=asset_swap_price_info.buy_asset,
                amount=converted_balance.buy_balance.amount
                / asset_swap_price_info.buy_asset.get_denomination(),
                amount_atomic=int(
                    converted_balance.buy_balance.amount_atomic
                    / asset_swap_price_info.buy_asset.get_denomination()
                ),
                decimals=converted_balance.buy_balance.decimals,
            ),
        )
