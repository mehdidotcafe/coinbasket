from typing import Literal
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain, ParsedReceipt
from invest_agent.database.infrastructure.sql_alchemy_session_manager import (
    SqlAlchemySessionManager,
)
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.investment.transaction.transaction_repository import (
    TransactionRepository,
)
from invest_agent.investment.transaction.transaction import Transaction
from invest_agent.portfolio.posting.posting import Posting
from invest_agent.portfolio.posting.posting_repository import PostingRepository
from invest_agent.investment.order.order import Order, Try


class OnOrderSuccessTask:
    def __init__(
        self,
        order_repository: OrderRepository,
        transaction_repository: TransactionRepository,
        posting_repository: PostingRepository,
        chain: Chain,
        date_time: DateTime,
        session_manager: SqlAlchemySessionManager,
    ):
        self.order_repository = order_repository
        self.transaction_repository = transaction_repository
        self.posting_repository = posting_repository
        self.chain = chain
        self.date_time = date_time
        self.session_manager = session_manager

    async def execute(
        self, order: Order, order_try: Try | None, parsed_receipt: ParsedReceipt
    ):
        created_at = self.date_time.now()
        transaction = self.__map_order_to_transaction(
            order, order_try, created_at, parsed_receipt
        )

        async with self.session_manager.session() as session:
            # TODO: Ensure idempotency
            await self.order_repository.set_order_to_success(order.id, session=session)

            await self.transaction_repository.create_transaction(
                transaction, session=session
            )
            if not self.chain.is_native_token(transaction.sell_balance.asset):
                await self.posting_repository.create_posting(
                    self.__map_transaction_to_posting(
                        transaction=transaction,
                        balance=parsed_receipt.executed_sell_balance,
                        created_at=created_at,
                        kind="OUT",
                    ),
                    session=session,
                )
            if not self.chain.is_native_token(transaction.buy_balance.asset):
                await self.posting_repository.create_posting(
                    self.__map_transaction_to_posting(
                        transaction=transaction,
                        balance=parsed_receipt.executed_buy_balance,
                        created_at=created_at,
                        kind="IN",
                    ),
                    session=session,
                )
        return transaction

    def __map_transaction_to_posting(
        self,
        kind: Literal["IN", "OUT"],
        transaction: Transaction,
        balance: BalanceAtomic,
        created_at: int,
    ) -> Posting:
        multiplier = 1 if kind == "IN" else -1

        return Posting(
            id=f"{transaction.id}-{kind}",
            parent_posting_id=f"{transaction.parent_transaction_id}-{kind}"
            if transaction.parent_transaction_id
            else None,
            transaction_id=transaction.id,
            asset_balance=BalanceAtomic(
                asset=balance.asset,
                amount=balance.amount * multiplier,
                amount_atomic=balance.amount_atomic * multiplier,
                decimals=balance.decimals,
            ),
            type=transaction.type,
            asset_type=transaction.asset_type,
            created_at=created_at,
            basket_id=transaction.sell_basket_id
            if kind == "OUT"
            else transaction.buy_basket_id,
        )

    def __map_order_to_transaction(
        self,
        order: Order,
        order_try: Try | None,
        created_at: int,
        parsed_receipt: ParsedReceipt,
    ) -> Transaction:
        return Transaction(
            id=order.id,
            parent_transaction_id=order.parent_order_id,
            sell_balance=order.sell_balance,
            buy_balance=order.buy_balance,
            executed_sell_balance=parsed_receipt.executed_sell_balance,
            executed_buy_balance=parsed_receipt.executed_buy_balance,
            type=order.type,
            asset_type=order.asset_type,
            created_at=created_at,
            fees=order_try.fees if order_try else None,
            transaction_hash=order_try.chain_transactions[-1].hash
            if order_try
            else None,
            order_id=order.id,
            trigger=order.trigger,
            buy_basket_id=order.buy_basket_id,
            sell_basket_id=order.sell_basket_id,
        )
