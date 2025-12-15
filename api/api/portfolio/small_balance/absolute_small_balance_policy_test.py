# @Copilot

import pytest
from decimal import Decimal
from api.chain.balance import BalanceAtomic
from api.portfolio.small_balance.absolute_small_balance_policy import (
    AbsoluteSmallBalancePolicy,
    Configuration,
)
from api.protocol.fixture.token import usdt_token


@pytest.fixture
def configuration() -> Configuration:
    return {"threshold": Decimal("0.10")}


@pytest.fixture
def usd_rate_balance() -> BalanceAtomic:
    # 1 token = 2 USD
    return BalanceAtomic(
        amount=Decimal("2.0"), amount_atomic=2, decimals=0, asset=usdt_token
    )


def test_absolute_small_balance_policy_is_small_balance_true(
    configuration: Configuration,
    usd_rate_balance: BalanceAtomic,
) -> None:
    policy = AbsoluteSmallBalancePolicy(configuration)
    small_balance = BalanceAtomic(
        amount=Decimal("0.04"), amount_atomic=4 * 10**16, decimals=18, asset=usdt_token
    )
    # 0.04 * 2.0 = 0.08 < 0.10
    assert policy.is_small_balance(small_balance, usd_rate_balance) is True


def test_absolute_small_balance_policy_is_small_balance_false(
    configuration: Configuration,
    usd_rate_balance: BalanceAtomic,
) -> None:
    policy = AbsoluteSmallBalancePolicy(configuration)
    not_small_balance = BalanceAtomic(
        amount=Decimal("0.10"), amount_atomic=10 * 10**16, decimals=18, asset=usdt_token
    )
    # 0.10 * 2.0 = 0.20 >= 0.10
    assert policy.is_small_balance(not_small_balance, usd_rate_balance) is False

    not_small_balance2 = BalanceAtomic(
        amount=Decimal("1.00"), amount_atomic=10 * 10**16, decimals=18, asset=usdt_token
    )
    # 1.00 * 2.0 = 2.00 >= 0.10
    assert policy.is_small_balance(not_small_balance2, usd_rate_balance) is False
