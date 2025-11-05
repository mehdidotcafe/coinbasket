from decimal import Decimal
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.investment.order.order import ChainTransaction, Order, Try
from invest_agent.investment.order.task.order_on_order_success_task import (
    OnOrderSuccessTask,
)

from unittest import mock
from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.investment.transaction.transaction import Transaction
from invest_agent.investment.transaction.transaction_repository import (
    TransactionRepository,
)
from invest_agent.portfolio.posting.posting import Posting
from invest_agent.portfolio.posting.posting_repository import PostingRepository
from invest_agent.chain.chain import Chain, ParsedReceipt
from invest_agent.datetime.date_time import DateTime
from invest_agent.database.infrastructure.sql_alchemy_session_manager import (
    SqlAlchemySessionManager,
)
from pytest import fixture, mark

from protocol.fixture.token import wbnb_token, sol_token, bnb_token
from protocol.fixture.basket import test_basket


@fixture
def order_repository():
    return mock.Mock(spec=OrderRepository)


@fixture
def transaction_repository():
    return mock.Mock(spec=TransactionRepository)


@fixture
def posting_repository():
    return mock.Mock(spec=PostingRepository)


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def date_time():
    dt = mock.Mock(spec=DateTime)
    dt.now.return_value = 1234567890

    return dt


@fixture
def session_manager():
    sm = mock.Mock(spec=SqlAlchemySessionManager)

    # This is the object returned by "async with ... as session:"
    session = mock.AsyncMock(name="AsyncSession")

    # Make sm.session() return an async context manager
    cm = mock.MagicMock(name="SessionContextManager")
    cm.__aenter__ = mock.AsyncMock(return_value=session)
    cm.__aexit__ = mock.AsyncMock(return_value=None)

    sm.session.return_value = cm
    return sm


@fixture
def task(
    order_repository: OrderRepository,
    transaction_repository: TransactionRepository,
    posting_repository: PostingRepository,
    chain: Chain,
    date_time: DateTime,
    session_manager: SqlAlchemySessionManager,
):
    return OnOrderSuccessTask(
        order_repository=order_repository,
        transaction_repository=transaction_repository,
        posting_repository=posting_repository,
        chain=chain,
        date_time=date_time,
        session_manager=session_manager,
    )


@mark.asyncio
async def test_on_order_success_task_sell_token_buy_token(
    task: OnOrderSuccessTask,
    order_repository: OrderRepository,
    transaction_repository: TransactionRepository,
    posting_repository: PostingRepository,
    chain: Chain,
):
    chain.is_native_token.return_value = False

    order = Order(
        id="order1",
        sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=sol_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**9,
            decimals=9,
        ),
        type="SWAP",
        asset_type="TOKEN",
        tries=[],
        created_at=1234560000,
        status="PENDING",
        trigger="MANUAL",
    )

    order_try = Try(
        id="try1",
        order_id="order1",
        created_at=1234560001,
        chain_transactions=[
            ChainTransaction(
                id="ct1",
                try_id="try1",
                order_id="order1",
                type="SEND",
                amount=1000 * 10**18,
                data="data",
                status="SUCCESS",
                hash="0xhash",
                to_address="0xto",
                gas=None,
            )
        ],
        provider="provider1",
        buy_balance=order.buy_balance,
    )

    parsed_receipt = ParsedReceipt(
        executed_sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        executed_buy_balance=BalanceAtomic(
            asset=sol_token,
            amount=Decimal("499"),
            amount_atomic=499 * 10**9,
            decimals=9,
        ),
        rate=Decimal("0.4999"),
    )

    mapped_transaction = Transaction(
        id=order.id,
        parent_transaction_id=None,
        sell_balance=order.sell_balance,
        buy_balance=order.buy_balance,
        executed_sell_balance=parsed_receipt.executed_sell_balance,
        executed_buy_balance=parsed_receipt.executed_buy_balance,
        type=order.type,
        asset_type=order.asset_type,
        created_at=1234567890,
        fees=order_try.fees,
        transaction_hash=order_try.chain_transactions[0].hash,
        order_id=order.id,
        trigger=order.trigger,
    )

    transaction = await task.execute(order, order_try, parsed_receipt)

    order_repository.set_order_to_success.assert_awaited_once_with(
        order.id,
        session=mock.ANY,
    )

    transaction_repository.create_transaction.assert_awaited_once_with(
        mapped_transaction,
        session=mock.ANY,
    )

    posting_repository.create_posting.assert_has_awaits(
        [
            mock.call(
                Posting(
                    id=f"{transaction.id}-OUT",
                    parent_posting_id=None,
                    transaction_id=transaction.id,
                    asset_balance=BalanceAtomic(
                        asset=transaction.sell_balance.asset,
                        amount=-transaction.executed_sell_balance.amount,
                        amount_atomic=-transaction.executed_sell_balance.amount_atomic,
                        decimals=transaction.sell_balance.decimals,
                    ),
                    type=transaction.type,
                    asset_type="TOKEN",
                    created_at=1234567890,
                    basket_id=None,
                ),
                session=mock.ANY,
            ),
            mock.call(
                Posting(
                    id=f"{transaction.id}-IN",
                    parent_posting_id=None,
                    transaction_id=transaction.id,
                    asset_balance=BalanceAtomic(
                        asset=transaction.buy_balance.asset,
                        amount=transaction.executed_buy_balance.amount,
                        amount_atomic=transaction.executed_buy_balance.amount_atomic,
                        decimals=transaction.buy_balance.decimals,
                    ),
                    type=transaction.type,
                    asset_type="TOKEN",
                    created_at=1234567890,
                    basket_id=None,
                ),
                session=mock.ANY,
            ),
        ],
    )

    assert transaction


@mark.asyncio
async def test_on_order_success_task_sell_token_buy_native_token(
    task: OnOrderSuccessTask,
    posting_repository: PostingRepository,
    chain: Chain,
):
    chain.is_native_token.side_effect = [False, True]

    order = Order(
        id="order1",
        sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**9,
            decimals=9,
        ),
        type="SELL",
        asset_type="TOKEN",
        tries=[],
        created_at=1234560000,
        status="PENDING",
        trigger="MANUAL",
    )

    order_try = Try(
        id="try1",
        order_id="order1",
        created_at=1234560001,
        chain_transactions=[
            ChainTransaction(
                id="ct1",
                try_id="try1",
                order_id="order1",
                type="SEND",
                amount=1000 * 10**18,
                data="data",
                status="SUCCESS",
                hash="0xhash",
                to_address="0xto",
                gas=None,
            )
        ],
        provider="provider1",
        buy_balance=order.buy_balance,
    )

    parsed_receipt = ParsedReceipt(
        executed_sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        executed_buy_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("499"),
            amount_atomic=499 * 10**9,
            decimals=9,
        ),
        rate=Decimal("0.4999"),
    )

    transaction = await task.execute(order, order_try, parsed_receipt)

    posting_repository.create_posting.assert_awaited_once_with(
        Posting(
            id=f"{transaction.id}-OUT",
            parent_posting_id=None,
            transaction_id=transaction.id,
            asset_balance=BalanceAtomic(
                asset=transaction.sell_balance.asset,
                amount=-transaction.executed_sell_balance.amount,
                amount_atomic=-transaction.executed_sell_balance.amount_atomic,
                decimals=transaction.sell_balance.decimals,
            ),
            type=transaction.type,
            asset_type="TOKEN",
            created_at=1234567890,
            basket_id=None,
        ),
        session=mock.ANY,
    )

    assert transaction


@mark.asyncio
async def test_on_order_success_task_sell_native_token_buy_token(
    task: OnOrderSuccessTask,
    posting_repository: PostingRepository,
    chain: Chain,
):
    chain.is_native_token.side_effect = [True, False]

    order = Order(
        id="order1",
        sell_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**9,
            decimals=9,
        ),
        type="BUY",
        asset_type="TOKEN",
        tries=[],
        created_at=1234560000,
        status="PENDING",
        trigger="MANUAL",
    )

    order_try = Try(
        id="try1",
        order_id="order1",
        created_at=1234560001,
        chain_transactions=[
            ChainTransaction(
                id="ct1",
                try_id="try1",
                order_id="order1",
                type="SEND",
                amount=1000 * 10**18,
                data="data",
                status="SUCCESS",
                hash="0xhash",
                to_address="0xto",
                gas=None,
            )
        ],
        provider="provider1",
        buy_balance=order.buy_balance,
    )

    parsed_receipt = ParsedReceipt(
        executed_sell_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        executed_buy_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("499"),
            amount_atomic=499 * 10**9,
            decimals=9,
        ),
        rate=Decimal("0.4999"),
    )

    transaction = await task.execute(order, order_try, parsed_receipt)

    posting_repository.create_posting.assert_awaited_once_with(
        Posting(
            id=f"{transaction.id}-IN",
            parent_posting_id=None,
            transaction_id=transaction.id,
            asset_balance=BalanceAtomic(
                asset=transaction.buy_balance.asset,
                amount=transaction.executed_buy_balance.amount,
                amount_atomic=transaction.executed_buy_balance.amount_atomic,
                decimals=transaction.buy_balance.decimals,
            ),
            type=transaction.type,
            asset_type="TOKEN",
            created_at=1234567890,
            basket_id=None,
        ),
        session=mock.ANY,
    )

    assert transaction


@mark.asyncio
async def test_on_order_success_task_sell_basket_buy_token(
    task: OnOrderSuccessTask,
    posting_repository: PostingRepository,
    chain: Chain,
):
    chain.is_native_token.return_value = False

    order = Order(
        id="order1",
        sell_balance=BalanceAtomic(
            asset=test_basket,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**9,
            decimals=9,
        ),
        type="SWAP",
        asset_type="BASKET",
        tries=[],
        created_at=1234560000,
        status="PENDING",
        trigger="MANUAL",
        sell_basket_id=test_basket.id,
        buy_basket_id=None,
    )

    parsed_receipt = ParsedReceipt(
        executed_sell_balance=BalanceAtomic(
            asset=test_basket,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        executed_buy_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("499"),
            amount_atomic=499 * 10**9,
            decimals=9,
        ),
        rate=Decimal("0.4999"),
    )

    transaction = await task.execute(order, None, parsed_receipt)

    posting_repository.create_posting.assert_awaited_once_with(
        Posting(
            id=f"{transaction.id}-OUT",
            parent_posting_id=None,
            transaction_id=transaction.id,
            asset_balance=BalanceAtomic(
                asset=transaction.sell_balance.asset,
                amount=-transaction.executed_sell_balance.amount,
                amount_atomic=-transaction.executed_sell_balance.amount_atomic,
                decimals=transaction.sell_balance.decimals,
            ),
            type=transaction.type,
            asset_type="BASKET",
            created_at=1234567890,
            basket_id=order.sell_basket_id,
        ),
        session=mock.ANY,
    )

    assert transaction


@mark.asyncio
async def test_on_order_success_task_sell_token_buy_basket(
    task: OnOrderSuccessTask,
    posting_repository: PostingRepository,
    chain: Chain,
):
    chain.is_native_token.return_value = False

    order = Order(
        id="order1",
        sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=test_basket,
            amount=Decimal("500"),
            amount_atomic=500 * 10**9,
            decimals=9,
        ),
        type="SWAP",
        asset_type="BASKET",
        tries=[],
        created_at=1234560000,
        status="PENDING",
        trigger="MANUAL",
        sell_basket_id=None,
        buy_basket_id=test_basket.id,
    )

    parsed_receipt = ParsedReceipt(
        executed_sell_balance=BalanceAtomic(
            asset=wbnb_token,
            amount=Decimal("1000"),
            amount_atomic=1000 * 10**18,
            decimals=18,
        ),
        executed_buy_balance=BalanceAtomic(
            asset=test_basket,
            amount=Decimal("499"),
            amount_atomic=499 * 10**9,
            decimals=9,
        ),
        rate=Decimal("0.4999"),
    )

    transaction = await task.execute(order, None, parsed_receipt)

    posting_repository.create_posting.assert_awaited_once_with(
        Posting(
            id=f"{transaction.id}-IN",
            parent_posting_id=None,
            transaction_id=transaction.id,
            asset_balance=BalanceAtomic(
                asset=transaction.buy_balance.asset,
                amount=transaction.executed_buy_balance.amount,
                amount_atomic=transaction.executed_buy_balance.amount_atomic,
                decimals=transaction.buy_balance.decimals,
            ),
            type=transaction.type,
            asset_type="BASKET",
            created_at=1234567890,
            basket_id=order.buy_basket_id,
        ),
        session=mock.ANY,
    )

    assert transaction
