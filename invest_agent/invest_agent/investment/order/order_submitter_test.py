from decimal import Decimal
from unittest import mock
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain, ParsedReceipt
from invest_agent.investment.exchange.exchange import Exchange, TransactionData
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.order.order import ChainTransaction, Order, Try
from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.investment.transaction.transaction import Transaction

from invest_agent.investment.order.order_submitter import OrderSubmitter

from invest_agent.investment.transaction.transaction_repository import (
    TransactionRepository,
)
from invest_agent.portfolio.posting.posting import Posting
from invest_agent.portfolio.posting.posting_repository import PostingRepository
from pytest import fixture, mark
from shared.id_generator.id_generator import IdGenerator
from protocol.fixture.token import bnb_token, sol_token


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def chain():
    return mock.Mock(spec=Chain)


@fixture
def date_time():
    return mock.Mock(spec=DateTime)


@fixture
def investment_parameters():
    return mock.Mock(spec=InvestmentParameters)


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
def id_generator():
    return mock.Mock(spec=IdGenerator)


@fixture
def order_submitter(
    exchange: Exchange,
    chain: Chain,
    id_generator: IdGenerator,
    date_time: DateTime,
    order_repository: OrderRepository,
    transaction_repository: TransactionRepository,
    posting_repository: PostingRepository,
):
    return OrderSubmitter(
        exchange,
        chain,
        id_generator,
        date_time,
        order_repository,
        transaction_repository,
        posting_repository,
    )


@fixture
def tries():
    return [
        Try(
            id="1",
            order_id="1",
            created_at=1752268296,
            fees=None,
            chain_transactions=[
                ChainTransaction(
                    id="1",
                    order_id="1",
                    try_id="1",
                    type="SEND",
                    data="encoded_input_data",
                    hash="12345",
                    status="PENDING",
                ),
            ],
            provider="MockExchange",
            buy_balance=BalanceAtomic(
                amount=Decimal(0), amount_atomic=0, asset=sol_token, decimals=18
            ),
        )
    ]


@mark.asyncio
async def test_order_submitter_submit_orders(order_submitter: OrderSubmitter):
    orders = [
        Order(
            id="3",
            sell_balance=BalanceAtomic(
                amount=Decimal("0.40"),
                amount_atomic=int(0.40 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
            buy_balance=BalanceAtomic(
                amount=Decimal(0), amount_atomic=0, asset=sol_token, decimals=18
            ),
            type="BUY",
            tries=[],
            created_at=1752268296,
            status="PENDING",
            trigger="MANUAL",
            basket_id="basket2",
        )
    ]

    result = await order_submitter.submit_orders(orders)

    assert result == orders


@mark.asyncio
async def test_order_submitter_submit_and_wait_order_without_tries(
    order_submitter: OrderSubmitter,
    id_generator: IdGenerator,
    date_time: DateTime,
    chain: Chain,
    exchange: Exchange,
    order_repository: OrderRepository,
    tries: list[Try],
):
    order = Order(
        id="1",
        sell_balance=BalanceAtomic(
            amount=Decimal("0.25"),
            amount_atomic=int(0.25 * 10**18),
            asset=bnb_token,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            amount=Decimal(0), amount_atomic=0, asset=sol_token, decimals=18
        ),
        type="BUY",
        tries=[],
        created_at=1752268296,
        status="PENDING",
        trigger="MANUAL",
        basket_id="basket1",
    )

    exchange.get_name.return_value = "MockExchange"
    exchange.build_transactions.return_value = [
        TransactionData(
            type="SEND",
            amount=25,
            encoded_input="encoded_input_data",
            gas=None,
            to_address="0x1234567890abcdef",
        )
    ]
    id_generator.generate_random_id.return_value = "1"
    date_time.now.return_value = 1752268296
    chain.sign_send_transaction.return_value = "12345"

    await order_submitter.submit_and_wait_order(order)

    chain.sign_send_transaction.assert_called_once_with(
        amount=25,
        gas=None,
        to_address="0x1234567890abcdef",
        encoded_input="encoded_input_data",
    )
    order_repository.add_order_try.assert_called_once_with(
        order.id,
        tries[0],
    )


@mark.asyncio
async def test_order_submitter_submit_and_wait_order_with_tries(
    order_submitter: OrderSubmitter,
    id_generator: IdGenerator,
    date_time: DateTime,
    chain: Chain,
    exchange: Exchange,
    order_repository: OrderRepository,
    tries: list[Try],
):
    order = Order(
        id="1",
        sell_balance=BalanceAtomic(
            amount=Decimal("0.25"),
            amount_atomic=int(0.25 * 10**18),
            asset=bnb_token,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            amount=Decimal(0), amount_atomic=0, asset=sol_token, decimals=18
        ),
        type="BUY",
        tries=tries,
        created_at=1752268296,
        status="PENDING",
        trigger="MANUAL",
        basket_id="basket1",
    )

    exchange.get_name.return_value = "MockExchange"
    exchange.build_transactions.return_value = [
        TransactionData(
            type="SEND",
            amount=25,
            encoded_input="encoded_input_data",
            gas=None,
            to_address="0x1234567890abcdef",
        )
    ]
    id_generator.generate_random_id.return_value = "1"
    date_time.now.return_value = 1752268296
    chain.sign_send_transaction.return_value = "12345"

    await order_submitter.submit_and_wait_order(order)

    chain.sign_send_transaction.assert_not_called()
    order_repository.add_order_try.assert_not_called()


@mark.asyncio
async def test_order_submitter_submit_and_wait_order_success(
    order_submitter: OrderSubmitter,
    id_generator: IdGenerator,
    date_time: DateTime,
    chain: Chain,
    exchange: Exchange,
    order_repository: OrderRepository,
    transaction_repository: TransactionRepository,
    posting_repository: PostingRepository,
    tries: list[Try],
):
    order = Order(
        id="1",
        sell_balance=BalanceAtomic(
            amount=Decimal("0.25"),
            amount_atomic=int(0.25 * 10**18),
            asset=bnb_token,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            amount=Decimal(5), amount_atomic=5 * 10**18, asset=sol_token, decimals=18
        ),
        type="BUY",
        tries=tries,
        created_at=1752268296,
        status="PENDING",
        trigger="MANUAL",
        basket_id="basket1",
    )

    exchange.get_name.return_value = "MockExchange"
    exchange.build_transactions.return_value = [
        TransactionData(
            type="SEND",
            amount=25,
            encoded_input="encoded_input_data",
            gas=None,
            to_address="0x1234567890abcdef",
        )
    ]
    id_generator.generate_random_id.return_value = "1"
    date_time.now.return_value = 1752268296
    chain.sign_send_transaction.return_value = "12345"
    chain.wait_transaction.return_value = True
    chain.parse_transaction_receipt.return_value = ParsedReceipt(
        executed_sell_balance=BalanceAtomic(
            amount=Decimal("0.33"),
            amount_atomic=int(0.33 * 10**18),
            asset=bnb_token,
            decimals=18,
        ),
        executed_buy_balance=BalanceAtomic(
            amount=Decimal("5.12"),
            amount_atomic=512 * 10**16,
            asset=sol_token,
            decimals=18,
        ),
    )

    await order_submitter.submit_and_wait_order(order)

    order_repository.set_order_to_success.assert_called_once_with(order.id)
    transaction_repository.create_transaction.assert_called_once_with(
        Transaction(
            id=order.id,
            sell_balance=order.sell_balance,
            buy_balance=order.buy_balance,
            executed_buy_balance=BalanceAtomic(
                amount=Decimal("5.12"),
                amount_atomic=512 * 10**16,
                asset=sol_token,
                decimals=18,
            ),
            executed_sell_balance=BalanceAtomic(
                amount=Decimal("0.33"),
                amount_atomic=int(0.33 * 10**18),
                asset=bnb_token,
                decimals=18,
            ),
            type=order.type,
            created_at=1752268296,
            fees=None,
            transaction_hash="12345",
            order_id=order.id,
            trigger=order.trigger,
            basket_id=order.basket_id,
        )
    )
    posting_repository.assert_has_calls(
        [
            # create_posting should only called once for buy_balance because sell_balance is a native token
            mock.call.create_posting(
                Posting(
                    id=order.id,
                    transaction_id=order.id,
                    asset_balance=BalanceAtomic(
                        amount=Decimal("5.12"),
                        amount_atomic=512 * 10**16,
                        asset=sol_token,
                        decimals=18,
                    ),
                    type=order.type,
                    created_at=1752268296,
                    basket_id=order.basket_id,
                )
            ),
        ]
    )


@mark.asyncio
async def test_order_submitter_submit_and_wait_order_failed(
    order_submitter: OrderSubmitter,
    id_generator: IdGenerator,
    date_time: DateTime,
    chain: Chain,
    exchange: Exchange,
    order_repository: OrderRepository,
    tries: list[Try],
):
    order = Order(
        id="1",
        sell_balance=BalanceAtomic(
            amount=Decimal("0.25"),
            amount_atomic=int(0.25 * 10**18),
            asset=bnb_token,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            amount=Decimal(0), amount_atomic=0, asset=sol_token, decimals=18
        ),
        type="BUY",
        tries=tries,
        created_at=1752268296,
        status="PENDING",
        trigger="MANUAL",
        basket_id="basket1",
    )

    exchange.get_name.return_value = "MockExchange"
    exchange.build_transactions.return_value = [
        TransactionData(
            type="SEND",
            amount=25,
            encoded_input="encoded_input_data",
            gas=None,
            to_address="0x1234567890abcdef",
        )
    ]
    id_generator.generate_random_id.return_value = "1"
    date_time.now.return_value = 1752268296
    chain.sign_send_transaction.return_value = "12345"
    chain.wait_transaction.side_effect = [
        False,
        False,
        False,
        False,
        False,
        False,
        True,
    ]

    await order_submitter.submit_and_wait_order(order)

    # 1 PENDING Try + 5 Attemps
    assert order_repository.set_order_try_chain_transaction_to_fail.call_count == 1 + 5

    order_repository.set_order_to_fail.assert_called_once_with(order.id)


@mark.asyncio
async def test_order_submitter_submit_and_wait_order_retries(
    order_submitter: OrderSubmitter,
    id_generator: IdGenerator,
    date_time: DateTime,
    chain: Chain,
    exchange: Exchange,
    order_repository: OrderRepository,
    tries: list[Try],
):
    order = Order(
        id="1",
        sell_balance=BalanceAtomic(
            amount=Decimal("0.25"),
            amount_atomic=int(0.25 * 10**18),
            asset=bnb_token,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            amount=Decimal(0), amount_atomic=0, asset=sol_token, decimals=18
        ),
        type="BUY",
        tries=tries,
        created_at=1752268296,
        status="PENDING",
        trigger="MANUAL",
        basket_id="basket1",
    )

    exchange.get_name.return_value = "MockExchange"
    exchange.build_transactions.return_value = [
        TransactionData(
            type="SEND",
            amount=25,
            encoded_input="encoded_input_data",
            gas=None,
            to_address="0x1234567890abcdef",
        )
    ]
    id_generator.generate_random_id.return_value = "1"
    date_time.now.return_value = 1752268296
    chain.sign_send_transaction.return_value = "12345"
    chain.wait_transaction.side_effect = [False, False, True, False, False, False]

    await order_submitter.submit_and_wait_order(order)

    chain.assert_has_calls(
        [
            mock.call.wait_transaction("12345"),
            mock.call.sign_send_transaction(
                amount=25,
                gas=None,
                to_address="0x1234567890abcdef",
                encoded_input="encoded_input_data",
            ),
            mock.call.wait_transaction("12345"),
            mock.call.sign_send_transaction(
                amount=25,
                gas=None,
                to_address="0x1234567890abcdef",
                encoded_input="encoded_input_data",
            ),
            mock.call.wait_transaction("12345"),
        ]
    )
    order_repository.set_order_to_success.assert_called_once_with(order.id)
    order_repository.set_order_to_fail.assert_not_called()
