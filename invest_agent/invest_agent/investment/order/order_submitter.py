import asyncio
from decimal import Decimal
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain, ParsedReceipt
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.exchange.exchange import Exchange
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
    ):
        self.exchange = exchange
        self.chain = chain
        self.id_generator = id_generator
        self.date_time = date_time
        self.order_repository = order_repository
        self.transaction_repository = transaction_repository
        self.posting_repository = posting_repository

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

        parsed_receipt = await self.__handle_pending_chain_transactions(order)

        if parsed_receipt:
            return

        for _ in range(self.MAX_RETRIES):
            try:
                transactions_data = await self.exchange.build_transactions(
                    order,
                    InvestmentParameters(
                        slippage_tolerance_in_percentage=Decimal("1"),
                    ),
                )

                chain_transactions: list[ChainTransaction] = []
                try_id = self.id_generator.generate_random_id()

                for transaction_data in transactions_data:
                    transaction_hash = await self.chain.sign_send_transaction(
                        amount=transaction_data.amount,
                        gas=transaction_data.gas,
                        to_address=transaction_data.to_address,
                        encoded_input=transaction_data.encoded_input,
                    )

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
                    buy_balance=order.buy_balance,
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
            sell_balance=order.sell_balance,
            buy_balance=order.buy_balance,
            executed_sell_balance=parsed_receipt.executed_sell_balance,
            executed_buy_balance=parsed_receipt.executed_buy_balance,
            type=order.type,
            created_at=created_at,
            fees=order_try.fees,
            transaction_hash=order_try.chain_transactions[-1].hash,
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

            is_chain_transaction_success = await self.chain.wait_transaction(
                chain_transaction.hash
            )

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

        parsed_transaction_receipt = await self.chain.parse_transaction_receipt(
            sell_token=order.sell_balance.asset,
            buy_token=order.buy_balance.asset,
            transaction_hash=send_chain_transaction.hash,
        )

        return parsed_transaction_receipt
