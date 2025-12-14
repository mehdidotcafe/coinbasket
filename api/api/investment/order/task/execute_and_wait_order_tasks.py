from decimal import Decimal
from typing import Literal, TypedDict, cast
from api.chain.balance import BalanceAtomic
from api.chain.chain import Chain, ParsedReceipt
from api.datetime.date_time import DateTime
from api.investment.investment_parameters import InvestmentParameters
from api.investment.order.order_repository import OrderRepository
from shared.id_generator.id_generator import IdGenerator
from api.investment.order.order import ChainTransaction, Try, Order
from api.investment.exchange.exchange import Exchange, TransactionData
from protocol.token import Token
from shared.random_generator.random_generator import RandomGenerator
from api.investment.order.exception.order_without_send_transaction import (
    OrderWithoutSendTransaction,
)


class Configuration(TypedDict):
    environment: Literal["development", "production", "test"]


def is_production(configuration: Configuration) -> bool:
    return configuration["environment"] == "production"


class CreateOrderTryTask:
    def __init__(
        self,
        order_repository: OrderRepository,
        exchange: Exchange,
        chain: Chain,
        id_generator: IdGenerator,
        date_time: DateTime,
        configuration: Configuration,
    ):
        self.order_repository = order_repository
        self.exchange = exchange
        self.chain = chain
        self.id_generator = id_generator
        self.date_time = date_time
        self.configuration = configuration

    async def execute(self, order: Order):
        if is_production(self.configuration):
            transactions_data = await self.exchange.build_transactions(
                order,
                InvestmentParameters(
                    slippage_tolerance_in_percentage=Decimal("1"),
                ),
            )
        else:
            transactions_data = [
                # Dummy TransactionData
                TransactionData(
                    type="SEND",
                    amount=order.sell_balance.amount_atomic,
                    encoded_input="DUMMY_ENCODED_INPUT",
                )
            ]

        try_id = self.id_generator.generate_random_id()

        order_try = Try(
            id=try_id,
            order_id=order.id,
            created_at=self.date_time.now(),
            fees=None,
            chain_transactions=[
                ChainTransaction(
                    id=self.id_generator.generate_random_id(),
                    try_id=try_id,
                    order_id=order.id,
                    type=transaction_data.type,
                    amount=transaction_data.amount,
                    data=transaction_data.encoded_input,
                    status="PENDING",
                    to_address=transaction_data.to_address,
                    gas=transaction_data.gas,
                    hash=None,
                )
                for transaction_data in transactions_data
            ],
            provider=self.exchange.get_name(),
            buy_balance=cast(BalanceAtomic[Token], order.buy_balance),
        )

        await self.order_repository.add_order_try(order.id, order_try)

        return order_try


class ExecuteOrderTryTask:
    def __init__(
        self,
        order_repository: OrderRepository,
        exchange: Exchange,
        chain: Chain,
        id_generator: IdGenerator,
        date_time: DateTime,
        random_generator: RandomGenerator,
        configuration: Configuration,
    ):
        self.order_repository = order_repository
        self.exchange = exchange
        self.chain = chain
        self.id_generator = id_generator
        self.date_time = date_time
        self.random_generator = random_generator
        self.configuration = configuration

    async def execute(self, order_try: Try):
        for chain_transaction in order_try.chain_transactions:
            if is_production(self.configuration):
                transaction_hash = await self.chain.sign_send_transaction(
                    amount=chain_transaction.amount,
                    gas=chain_transaction.gas,
                    to_address=chain_transaction.to_address,
                    encoded_input=chain_transaction.data,
                )
            else:
                transaction_hash = "DUMMY_TRANSACTION_HASH"

            await self.order_repository.set_order_try_chain_transaction_hash(
                chain_transaction.id, transaction_hash
            )
        return True


class WaitOrderTryTask:
    def __init__(
        self,
        order_repository: OrderRepository,
        exchange: Exchange,
        chain: Chain,
        id_generator: IdGenerator,
        date_time: DateTime,
        random_generator: RandomGenerator,
        configuration: Configuration,
    ):
        self.order_repository = order_repository
        self.exchange = exchange
        self.chain = chain
        self.id_generator = id_generator
        self.date_time = date_time
        self.random_generator = random_generator
        self.configuration = configuration

    async def execute(self, order: Order, order_try: Try):
        chain_transactions = order_try.chain_transactions
        send_chain_transaction = None

        for chain_transaction in chain_transactions:
            if chain_transaction.type == "SEND":
                send_chain_transaction = chain_transaction

            if chain_transaction.status == "FAIL":
                return False
            if chain_transaction.status == "SUCCESS":
                continue

            if is_production(self.configuration):
                is_chain_transaction_success = await self.chain.wait_transaction(
                    cast(str, chain_transaction.hash)
                )
            else:
                # Mock a delay for testing
                is_chain_transaction_success = True

            if not is_chain_transaction_success:
                await self.order_repository.set_order_try_chain_transaction_to_fail(
                    chain_transaction.id
                )
                return False
            await self.order_repository.set_order_try_chain_transaction_to_success(
                chain_transaction.id
            )

        if not send_chain_transaction:
            raise OrderWithoutSendTransaction()

        if is_production(self.configuration):
            parsed_transaction_receipt = await self.chain.parse_transaction_receipt(
                sell_token=cast(Token, order.sell_balance.asset),
                buy_token=cast(Token, order.buy_balance.asset),
                transaction_hash=cast(str, send_chain_transaction.hash),
            )
        else:
            parsed_transaction_receipt = self._build_dummy_parsed_receipt(order)

        return parsed_transaction_receipt

    def _build_dummy_parsed_receipt(self, order: Order):
        random_factor = self.random_generator.generate_number(98, 100)
        executed_buy_balance_amount = order.buy_balance.amount * random_factor / 100
        executed_buy_balance_atomic_amount = int(
            order.buy_balance.amount_atomic * random_factor / 100
        )

        return ParsedReceipt(
            executed_sell_balance=cast(BalanceAtomic[Token], order.sell_balance),
            executed_buy_balance=BalanceAtomic[Token](
                asset=cast(Token, order.buy_balance.asset),
                decimals=order.buy_balance.decimals,
                amount=executed_buy_balance_amount,
                amount_atomic=executed_buy_balance_atomic_amount,
            ),
            rate=Decimal(executed_buy_balance_atomic_amount)
            / Decimal(order.sell_balance.amount_atomic),
        )


class FailOrderTryTask:
    def __init__(self, order_repository: OrderRepository, date_time: DateTime):
        self.order_repository = order_repository
        self.date_time = date_time

    async def execute(self, order_try: Try):
        await self.order_repository.set_order_try_chain_transactions_to_fail(
            order_try.id
        )
