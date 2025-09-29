import asyncio
from decimal import Decimal
from typing import Literal, TypedDict, cast
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain, ParsedReceipt
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.exchange.exchange import Exchange, TransactionData
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.order.exception.order_without_send_transaction import (
    OrderWithoutSendTransaction,
)
from invest_agent.investment.order.order import ChainTransaction, Order, Try
from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.investment.transaction.transaction import Transaction
from invest_agent.investment.transaction.transaction_repository import (
    TransactionRepository,
)
from invest_agent.portfolio.posting.posting import Posting
from invest_agent.portfolio.posting.posting_repository import PostingRepository
from protocol.token import Token
from shared.id_generator.id_generator import IdGenerator
from shared.random_generator.random_generator import RandomGenerator


class Configuration(TypedDict):
    environment: Literal["development", "production", "test"]


class OrderSubmitter:
    """Submits and check orders."""

    MAX_RETRIES = 5

    def __init__(
        self,
        exchange: Exchange,
        chain: Chain,
        id_generator: IdGenerator,
        date_time: DateTime,
        order_repository: OrderRepository,
        transaction_repository: TransactionRepository,
        posting_repository: PostingRepository,
        random_generator: RandomGenerator,
        configuration: Configuration,
    ):
        self.exchange = exchange
        self.chain = chain
        self.id_generator = id_generator
        self.date_time = date_time
        self.order_repository = order_repository
        self.transaction_repository = transaction_repository
        self.posting_repository = posting_repository
        self.random_generator = random_generator
        self.configuration = configuration

    async def submit_orders(self, orders: list[Order]) -> list[Order]:
        """Submit a list of orders and wait for their execution."""
        for order in orders:
            asyncio.create_task(self.submit_and_wait_order(order))

        # Return the list of orders after submission
        return orders

    async def submit_and_wait_order(self, order: Order):
        """
        Submit an order and wait for its execution.
        If an order has already been tried, it will use the last try's transaction hash.
        """
        await self.order_repository.create_order(order)

        if order.asset_type == "BASKET":
            return

        parsed_receipt = await self.__handle_pending_chain_transactions(order)

        if parsed_receipt:
            return

        for _ in range(self.MAX_RETRIES):
            try:
                if self._is_production():
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

                chain_transactions: list[ChainTransaction] = []
                try_id = self.id_generator.generate_random_id()

                for transaction_data in transactions_data:
                    if self._is_production():
                        transaction_hash = await self.chain.sign_send_transaction(
                            amount=transaction_data.amount,
                            gas=transaction_data.gas,
                            to_address=transaction_data.to_address,
                            encoded_input=transaction_data.encoded_input,
                        )
                    else:
                        transaction_hash = "DUMMY_TRANSACTION_HASH"

                    chain_transaction = ChainTransaction(
                        id=self.id_generator.generate_random_id(),
                        try_id=try_id,
                        order_id=order.id,
                        type=transaction_data.type,
                        data=transaction_data.encoded_input,
                        hash=transaction_hash,
                        status="PENDING",
                    )
                    chain_transactions.append(chain_transaction)

                order_try = Try(
                    id=try_id,
                    order_id=order.id,
                    created_at=self.date_time.now(),
                    fees=None,
                    chain_transactions=chain_transactions,
                    provider=self.exchange.get_name(),
                    buy_balance=cast(BalanceAtomic[Token], order.buy_balance),
                )

                await self.order_repository.add_order_try(order.id, order_try)

                parsed_receipt = await self.__wait_chain_transactions(
                    order, chain_transactions
                )

                if parsed_receipt:
                    created_at = self.date_time.now()
                    transaction = self.__map_order_to_transaction(
                        order, order_try, created_at, parsed_receipt
                    )

                    await self.order_repository.set_order_to_success(order.id)

                    await self.transaction_repository.create_transaction(transaction)
                    if not self.chain.is_native_token(transaction.sell_balance.asset):
                        await self.posting_repository.create_posting(
                            self.__map_transaction_to_posting(
                                transaction=transaction,
                                balance=parsed_receipt.executed_sell_balance,
                                created_at=created_at,
                                multiplier=-1,
                            )
                        )
                    if not self.chain.is_native_token(transaction.buy_balance.asset):
                        await self.posting_repository.create_posting(
                            self.__map_transaction_to_posting(
                                transaction=transaction,
                                balance=parsed_receipt.executed_buy_balance,
                                created_at=created_at,
                                multiplier=1,
                            )
                        )

                    return
            except Exception as e:
                print(f"Error submitting order {order.id}: {e}")

        await self.order_repository.set_order_to_fail(order.id)

    def __map_order_to_transaction(
        self,
        order: Order,
        order_try: Try,
        created_at: int,
        parsed_receipt: ParsedReceipt,
    ) -> Transaction:
        return Transaction(
            id=order.id,
            sell_balance=cast(BalanceAtomic[Token], order.sell_balance),
            buy_balance=cast(BalanceAtomic[Token], order.buy_balance),
            executed_sell_balance=parsed_receipt.executed_sell_balance,
            executed_buy_balance=parsed_receipt.executed_buy_balance,
            type=order.type,
            created_at=created_at,
            fees=order_try.fees,
            transaction_hash=order_try.chain_transactions[-1].hash
            if self._is_production()
            else "DUMMY",
            order_id=order.id,
            trigger=order.trigger,
            basket_id=order.basket_id,
        )

    def __map_transaction_to_posting(
        self,
        transaction: Transaction,
        balance: BalanceAtomic[Token],
        created_at: int,
        multiplier: int,
    ) -> Posting:
        return Posting(
            id=self.id_generator.generate_random_id(),
            transaction_id=transaction.id,
            asset_balance=BalanceAtomic(
                asset=balance.asset,
                amount=balance.amount * multiplier,
                amount_atomic=balance.amount_atomic * multiplier,
                decimals=balance.decimals,
            ),
            type=transaction.type,
            created_at=created_at,
            basket_id=transaction.basket_id,
        )

    async def __handle_pending_chain_transactions(self, order: Order):
        """
        If the order has already been tried, it will use the last try's transactions.
        This is to ensure that if the order was partially executed, we can still track it.
        """
        last_try = order.tries[-1] if order.tries else None

        if last_try is None:
            return False

        parsed_receipt = await self.__wait_chain_transactions(
            order, last_try.chain_transactions
        )

        if parsed_receipt:
            created_at = self.date_time.now()
            transaction = self.__map_order_to_transaction(
                order, last_try, created_at, parsed_receipt
            )

            await self.order_repository.set_order_to_success(order.id)
            await self.transaction_repository.create_transaction(transaction)
            await self.posting_repository.create_posting(
                self.__map_transaction_to_posting(
                    transaction=transaction,
                    balance=parsed_receipt.executed_sell_balance,
                    created_at=created_at,
                    multiplier=-1,
                )
            )
            await self.posting_repository.create_posting(
                self.__map_transaction_to_posting(
                    transaction=transaction,
                    balance=parsed_receipt.executed_buy_balance,
                    created_at=created_at,
                    multiplier=1,
                )
            )

        return parsed_receipt

    async def __wait_chain_transactions(
        self, order: Order, chain_transactions: list[ChainTransaction]
    ):
        send_chain_transaction = None

        if len(chain_transactions) == 0:
            return False

        for chain_transaction in chain_transactions:
            if chain_transaction.type == "SEND":
                send_chain_transaction = chain_transaction

            if chain_transaction.status == "FAIL":
                return False
            if chain_transaction.status == "SUCCESS":
                continue

            if self._is_production():
                is_chain_transaction_success = await self.chain.wait_transaction(
                    chain_transaction.hash
                )
            else:
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

        if self._is_production():
            parsed_transaction_receipt = await self.chain.parse_transaction_receipt(
                sell_token=cast(Token, order.sell_balance.asset),
                buy_token=cast(Token, order.buy_balance.asset),
                transaction_hash=send_chain_transaction.hash,
            )
        else:
            parsed_transaction_receipt = self._build_dummy_parsed_receipt(order)

        return parsed_transaction_receipt

    def _is_production(self):
        return self.configuration["environment"] == "production"

    def _build_dummy_parsed_receipt(self, order: Order):
        random_factor = self.random_generator.generate_number(0, 2)
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
