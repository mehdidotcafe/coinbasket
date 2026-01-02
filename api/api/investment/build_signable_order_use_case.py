from decimal import Decimal
from api.investment.exchange.exchange import Exchange
from api.investment.confirmed_order import (
    ConfirmedOrder,
)
from api.investment.investment_parameters import InvestmentParameters
from api.investment.signable_order import (
    SignableOrder,
)


investment_parameters = InvestmentParameters(
    slippage_tolerance_in_percentage=Decimal("1"),
)


class BuildSignableOrderUseCase:
    def __init__(self, exchange: Exchange):
        self.exchange = exchange

    async def execute(self, confirmed_order: ConfirmedOrder):
        signed_swap = await self.exchange.get_signable_swap(
            sell_balance=confirmed_order.sell_balance,
            buy_balance=confirmed_order.buy_balance,
            investment_parameters=investment_parameters,
        )

        return SignableOrder(
            # id=confirmed_order.id,
            # address=confirmed_order.address,
            buy_balance=signed_swap.buy_balance,
            sell_balance=signed_swap.sell_balance,
            signature_payload=signed_swap.signature_payload,
            transaction=signed_swap.transaction,
        )
