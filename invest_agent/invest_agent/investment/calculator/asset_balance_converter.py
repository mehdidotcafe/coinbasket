import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import cast
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.investment.exception.cannot_swap_basket_for_another_exception import (
    CannotSwapBasketForAnotherException,
)
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.portfolio.holding.holding import Holding
from protocol.asset import Asset
from protocol.basket import Basket
from protocol.token import Token
from functools import reduce


@dataclass
class ConvertedBalance:
    sell_balance: BalanceAtomic
    buy_balance: BalanceAtomic


@dataclass
class ConvertedAssetBalance:
    total_balance: ConvertedBalance
    balances: list[ConvertedBalance]


class AssetBalanceConverter:
    def __init__(self, exchange: Exchange, chain: Chain):
        self.exchange = exchange
        self.chain = chain

    async def convert(
        self, sell_balance: BalanceAtomic, buy_asset: Asset, holdings: list[Holding]
    ) -> ConvertedAssetBalance:
        if isinstance(sell_balance.asset, Basket) and isinstance(buy_asset, Token):
            return await self._convert_sell_basket_to_buy_token(
                cast(BalanceAtomic[Basket], sell_balance), buy_asset, holdings
            )
        if isinstance(buy_asset, Basket) and isinstance(sell_balance.asset, Token):
            return await self._convert_buy_basket_to_sell_token(
                cast(BalanceAtomic[Token], sell_balance), buy_asset, holdings
            )
        if isinstance(buy_asset, Token) and isinstance(sell_balance.asset, Token):
            return await self._convert_sell_token_to_buy_token(
                cast(BalanceAtomic[Token], sell_balance),
                buy_asset,
                holdings,
            )

        raise CannotSwapBasketForAnotherException

    async def _convert_sell_basket_to_buy_token(
        self,
        sell_balance: BalanceAtomic[Basket],
        buy_token: Token,
        holdings: list[Holding],
    ) -> ConvertedAssetBalance:
        # Find the holding for the basket
        basket_holding = next(
            (h for h in holdings if h.balance.asset == sell_balance.asset), None
        )
        if not basket_holding or not basket_holding.children:
            return await self._build_empty_balance(sell_balance, buy_token)

        # Calculate the sell ratio (portion of the basket to sell)
        total_basket_amount = basket_holding.balance.amount
        if total_basket_amount == 0:
            return await self._build_empty_balance(sell_balance, buy_token)
        sell_ratio = sell_balance.amount / total_basket_amount

        sell_child_balances = [
            BalanceAtomic(
                asset=child.asset,
                amount=child.amount * sell_ratio,
                amount_atomic=int(child.amount_atomic * sell_ratio),
                decimals=child.decimals,
            )
            for child in basket_holding.children
        ]

        async def convert_one(sell_child_balance: BalanceAtomic[Token]):
            return await self.exchange.convert_balance_to_token(
                balance=sell_child_balance,
                token=buy_token,
                investment_parameters=InvestmentParameters(
                    slippage_tolerance_in_percentage=Decimal("1"),
                ),
            )

        results = await asyncio.gather(
            *(convert_one(scb) for scb in sell_child_balances),
            return_exceptions=False,
        )

        converted_balances = [
            ConvertedBalance(
                sell_balance=result.sell_balance,
                buy_balance=result.buy_balance,
            )
            for result in results
        ]
        return ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=sell_balance,
                buy_balance=reduce(
                    lambda acc, converted_balance: acc + converted_balance.buy_balance,
                    converted_balances,
                    BalanceAtomic.empty(
                        cast(Token, converted_balances[0].buy_balance.asset),
                        converted_balances[0].buy_balance.decimals,
                    ),
                ),
            ),
            balances=converted_balances,
        )

    async def _convert_buy_basket_to_sell_token(
        self,
        sell_balance: BalanceAtomic[Token],
        buy_basket: Basket,
        holdings: list[Holding],
    ) -> ConvertedAssetBalance:
        # Split the sell_balance equally among the buy_basket's tokens
        num_tokens = len(buy_basket.tokens)
        if num_tokens == 0 or sell_balance.amount == 0:
            return await self._build_empty_balance(
                sell_balance=sell_balance,
                buy_asset=buy_basket,
            )

        split_amount = sell_balance.amount / num_tokens
        split_amount_atomic = int(sell_balance.amount_atomic / num_tokens)

        sell_balances = [
            BalanceAtomic(
                asset=sell_balance.asset,
                amount=split_amount,
                amount_atomic=split_amount_atomic,
                decimals=sell_balance.decimals,
            )
            for _ in buy_basket.tokens
        ]

        async def convert_one(sell_child_balance: BalanceAtomic[Token], token: Token):
            return await self.exchange.convert_balance_to_token(
                balance=sell_child_balance,
                token=token,
                investment_parameters=InvestmentParameters(
                    slippage_tolerance_in_percentage=Decimal("1"),
                ),
            )

        pricing_token = buy_basket.get_pricing_token()
        denomination = buy_basket.get_denomination()

        # Prepare all convert_balance_to_token calls (children + pricing_token)
        gather_calls = [
            convert_one(sell_balances[i], buy_basket.tokens[i])
            for i in range(num_tokens)
        ]
        gather_calls.append(
            self.exchange.convert_balance_to_token(
                balance=sell_balance,
                token=pricing_token,
                investment_parameters=InvestmentParameters(
                    slippage_tolerance_in_percentage=Decimal("1"),
                ),
            )
        )

        results = await asyncio.gather(*gather_calls, return_exceptions=False)

        converted_balances = [
            ConvertedBalance(
                sell_balance=sell_balances[i],
                buy_balance=results[i].buy_balance,
            )
            for i in range(num_tokens)
        ]

        pricing_result = results[-1]
        total_buy_balance = BalanceAtomic(
            asset=buy_basket,
            amount=pricing_result.buy_balance.amount / denomination,
            amount_atomic=int(pricing_result.buy_balance.amount_atomic / denomination),
            decimals=pricing_result.buy_balance.decimals,
        )

        return ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=sell_balance,
                buy_balance=total_buy_balance,
            ),
            balances=converted_balances,
        )

    async def _convert_sell_token_to_buy_token(
        self,
        sell_balance: BalanceAtomic[Token],
        buy_token: Token,
        holdings: list[Holding],
    ) -> ConvertedAssetBalance:
        result = await self.exchange.convert_balance_to_token(
            balance=sell_balance,
            token=buy_token,
            investment_parameters=InvestmentParameters(
                slippage_tolerance_in_percentage=Decimal("1"),
            ),
        )
        return ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=result.sell_balance,
                buy_balance=result.buy_balance,
            ),
            balances=[],
        )

    async def _build_empty_balance(
        self, sell_balance: BalanceAtomic, buy_asset: Asset
    ) -> ConvertedAssetBalance:
        buy_token_decimals = await self.chain.get_token_decimals(
            buy_asset.get_pricing_token().address
        )
        return ConvertedAssetBalance(
            total_balance=ConvertedBalance(
                sell_balance=sell_balance,
                buy_balance=BalanceAtomic.empty(
                    asset=buy_asset, decimals=buy_token_decimals
                ),
            ),
            balances=[],
        )
