from decimal import Decimal
from api.investment.exchange.exchange import Exchange
from api.investment.confirmed_order import (
    ConfirmedOrder,
)
from api.investment.investment_parameters import InvestmentParameters
from api.investment.signable_order import (
    SignableOrder,
)
from api.shared.id_generator.id_generator import IdGenerator


investment_parameters = InvestmentParameters(
    slippage_tolerance_in_percentage=Decimal("1"),
)


class BuildSignableOrderUseCase:
    def __init__(self, exchange: Exchange, id_generator: IdGenerator):
        self.exchange = exchange
        self.id_generator = id_generator

    async def execute(self, confirmed_order: ConfirmedOrder):
        signed_swap = await self.exchange.get_signable_swap(
            taker=confirmed_order.address,
            sell_balance=confirmed_order.sell_balance,
            buy_balance=confirmed_order.buy_balance,
            investment_parameters=investment_parameters,
        )

        return SignableOrder(
            id=self.id_generator.generate_random_id(),
            address=confirmed_order.address,
            confirmed_order_id=confirmed_order.id,
            buy_balance=signed_swap.buy_balance,
            sell_balance=signed_swap.sell_balance,
            signature_payload=signed_swap.signature_payload,
            transaction=signed_swap.transaction,
            approval_transaction=signed_swap.approval_transaction,
        )
