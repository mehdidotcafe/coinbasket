from decimal import Decimal
from unittest import mock
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.exchange.exchange import Exchange, TransactionData
from invest_agent.datetime.date_time import DateTime
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.order.order import ChainTransaction, Order, Try
from invest_agent.investment.order.order_repository import OrderRepository
from invest_agent.investment.transaction.transaction import Transaction
from invest_agent.investment.transaction.transaction_repository import (
    TransactionRepository,
)
from invest_agent.investment.order.order_submitter import OrderSubmitter

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
):
    return OrderSubmitter(
        exchange,
        chain,
        id_generator,
        date_time,
        order_repository,
        transaction_repository,
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
            buy_balance=Balance(amount=Decimal(0), token=sol_token),
        )
    ]


@mark.asyncio
async def test_order_submitter_submit_orders(order_submitter: OrderSubmitter):
    orders = [
        Order(
            id="3",
            sell_balance=Balance(amount=Decimal("0.40"), token=bnb_token),
            buy_balance=Balance(amount=Decimal(0), token=sol_token),
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
        sell_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
        buy_balance=Balance(amount=Decimal(0), token=sol_token),
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
        sell_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
        buy_balance=Balance(amount=Decimal(0), token=sol_token),
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
    tries: list[Try],
):
    order = Order(
        id="1",
        sell_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
        buy_balance=Balance(amount=Decimal(0), token=sol_token),
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

    await order_submitter.submit_and_wait_order(order)

    order_repository.set_order_to_success.assert_called_once_with(order.id)
    transaction_repository.create_transaction.assert_called_once_with(
        Transaction(
            id=order.id,
            sell_balance=order.sell_balance,
            buy_balance=order.buy_balance,
            type=order.type,
            created_at=1752268296,
            fees=None,
            transaction_hash="12345",
            order_id=order.id,
            trigger=order.trigger,
            basket_id=order.basket_id,
        )
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
        sell_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
        buy_balance=Balance(amount=Decimal(0), token=sol_token),
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
        sell_balance=Balance(amount=Decimal("0.25"), token=bnb_token),
        buy_balance=Balance(amount=Decimal(0), token=sol_token),
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
