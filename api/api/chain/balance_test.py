import pytest
from decimal import Decimal
from api.protocol.token import Token
from api.protocol.basket import Basket
from api.chain.balance import BalanceAtomic


@pytest.fixture
def token():
    return Token(
        id="1",
        name="TestToken",
        display_name="Test Token",
        ticker="TTK",
        address="0x123",
        description="Test token for testing",
        decimals=18,
        logo_uri=None,
        categories=["test", "token"],
        trust_score=85,
    )


@pytest.fixture
def basket():
    return Basket(
        id="2",
        name="TestBasket",
        display_name="Test Basket",
        ticker="TBK",
        address="0x123",
        description="A test basket",
        decimals=18,
        logo_uri=None,
        categories=["test", "basket"],
        trust_score=90,
    )


@pytest.fixture
def balance_atomic_token(token: Token):
    return BalanceAtomic(
        asset=token,
        amount=Decimal("1.23"),
        amount_atomic=123,
        decimals=2,
    )


@pytest.fixture
def balance_atomic_basket(basket: Token):
    return BalanceAtomic(
        asset=basket,
        amount=Decimal("2.00"),
        amount_atomic=200,
        decimals=2,
    )


def test_balance_add(balance_atomic_token: BalanceAtomic):
    b1 = balance_atomic_token
    b2 = BalanceAtomic(
        asset=b1.asset, amount=Decimal("0.77"), amount_atomic=77, decimals=2
    )
    result = b1 + b2
    assert result.amount_atomic == 200
    assert result.amount == Decimal("2.00")


def test_balance_add_decimal(balance_atomic_token: BalanceAtomic):
    b1 = balance_atomic_token
    result = b1 + Decimal("1.00")
    assert result.amount_atomic == 124
    assert result.amount == Decimal("1.24")


def test_balance_sub(balance_atomic_token: BalanceAtomic):
    b1 = balance_atomic_token
    b2 = BalanceAtomic(
        asset=b1.asset, amount=Decimal("0.23"), amount_atomic=23, decimals=2
    )
    result = b1 - b2
    assert result.amount_atomic == 100
    assert result.amount == Decimal("1.00")


def test_balance_sub_decimal(balance_atomic_token: BalanceAtomic):
    b1 = balance_atomic_token
    result = b1 - Decimal("23")
    assert result.amount_atomic == 100
    assert result.amount == Decimal("1.00")


def test_balance_mul(balance_atomic_token: BalanceAtomic):
    b1 = balance_atomic_token
    result = b1 * Decimal("2")
    assert result.amount_atomic == 246
    assert result.amount == Decimal("2.46")


def test_balance_mul_balance_atomic(balance_atomic_token: BalanceAtomic):
    b1 = balance_atomic_token
    b2 = BalanceAtomic(
        asset=b1.asset, amount=Decimal("2.00"), amount_atomic=2, decimals=2
    )
    result = b1 * b2
    assert result.amount_atomic == 246  # 123 * 2
    assert result.amount == Decimal("2.46")


def test_balance_truediv(balance_atomic_token: BalanceAtomic):
    b1 = balance_atomic_token
    result = b1 / Decimal("2")
    assert result.amount_atomic == 61  # int(123 / 2)
    assert result.amount == Decimal("0.61")


def test_balance_truediv_balance_atomic(balance_atomic_token: BalanceAtomic):
    b1 = balance_atomic_token
    b2 = BalanceAtomic(
        asset=b1.asset, amount=Decimal("1.00"), amount_atomic=1, decimals=2
    )
    result = b1 / b2
    assert result.amount_atomic == 123  # int(123 / 1)
    assert result.amount == Decimal("1.23")
