from unittest import mock
from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import Chain
from invest_agent.investment.build_priced_investment_plan_use_case import (
    BuildPricedInvestmentPlanUseCase,
)
from invest_agent.investment.exchange.exchange import Exchange, ExchangeConvertedBalance
from invest_agent.investment.investment_planner.intent_investment_plan import (
    IntentInvestmentPlan,
    IntentInvestmentPlanBalance,
    IntentInvestmentPlanStep,
)
from invest_agent.investment.investment_planner.priced_investment_plan import (
    PricedInvestmentPlan,
    PricedInvestmentPlanBalance,
    PricedInvestmentPlanStep,
)
from invest_agent.portfolio.holding.holding import Holding
from invest_agent.portfolio.posting.posting_repository import PostingRepository
from pytest import fixture, mark
from protocol.fixture.token import eth_token, bnb_token, usdt_token
from protocol.fixture.basket import big4_basket
from decimal import ROUND_DOWN, Decimal


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def chain():
    chain = mock.Mock(spec=Chain)

    chain.get_base_token.return_value = bnb_token
    chain.convert_amount_to_amount_atomic.side_effect = lambda token, amount_readable: (
        int(
            (Decimal(amount_readable) * (10**18)).to_integral_exact(rounding=ROUND_DOWN)
        ),
        18,
    )
    chain.convert_amount_atomic_to_amount.side_effect = lambda token, amount_atomic: (
        int((Decimal(amount_atomic) / (10**18)).to_integral_exact(rounding=ROUND_DOWN)),
        18,
    )

    return chain


@fixture
def posting_repository():
    return mock.Mock(spec=PostingRepository)


@fixture
def use_case(exchange: Exchange, chain: Chain, posting_repository: PostingRepository):
    return BuildPricedInvestmentPlanUseCase(
        exchange=exchange, chain=chain, posting_repository=posting_repository
    )


@mark.asyncio
async def test_build_priced_investment_plan_use_case_execute_defined_sell_token_amount(
    exchange: Exchange,
    posting_repository: PostingRepository,
    use_case: BuildPricedInvestmentPlanUseCase,
):
    intent_investment_plan = IntentInvestmentPlan(
        steps=[
            IntentInvestmentPlanStep(
                buy_asset_with_amount=IntentInvestmentPlanBalance(
                    # amount should be override in PricedInvestmentPlan
                    asset=eth_token,
                    amount=Decimal("1"),
                ),
                sell_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=bnb_token, amount=Decimal("100")
                ),
            )
        ]
    )

    posting_repository.get_holding_balances.return_value = []
    exchange.convert_balance_to_token.return_value = ExchangeConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("100"),
            amount_atomic=100 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=eth_token,
            amount=Decimal("42"),
            amount_atomic=42 * 10**18,
            decimals=18,
        ),
    )

    priced_investment_plan = await use_case.execute(intent_investment_plan)

    assert priced_investment_plan == PricedInvestmentPlan(
        steps=[
            PricedInvestmentPlanStep(
                buy_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=eth_token, amount=Decimal("42"), available_amount=Decimal("0")
                ),
                sell_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=bnb_token,
                    amount=Decimal("100"),
                    available_amount=Decimal("0"),
                ),
            )
        ]
    )


@mark.asyncio
async def test_build_priced_investment_plan_use_case_execute_defined_buy_token_amount(
    exchange: Exchange,
    posting_repository: PostingRepository,
    use_case: BuildPricedInvestmentPlanUseCase,
):
    intent_investment_plan = IntentInvestmentPlan(
        steps=[
            IntentInvestmentPlanStep(
                buy_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=eth_token,
                    amount=Decimal("1"),
                ),
                sell_asset_with_amount=IntentInvestmentPlanBalance(
                    # amount should be override in PricedInvestmentPlan
                    asset=bnb_token,
                    amount=None,
                ),
            )
        ]
    )

    posting_repository.get_holding_balances.return_value = []
    exchange.convert_balance_to_token.return_value = ExchangeConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=eth_token,
            amount=Decimal("1"),
            amount_atomic=1 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("100"),
            amount_atomic=100 * 10**18,
            decimals=18,
        ),
    )

    priced_investment_plan = await use_case.execute(intent_investment_plan)

    assert priced_investment_plan == PricedInvestmentPlan(
        steps=[
            PricedInvestmentPlanStep(
                buy_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=eth_token, amount=Decimal("1"), available_amount=Decimal("0")
                ),
                sell_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=bnb_token,
                    amount=Decimal("100"),
                    available_amount=Decimal("0"),
                ),
            )
        ]
    )


@mark.asyncio
async def test_build_priced_investment_plan_use_case_execute_not_defined_tokens(
    exchange: Exchange,
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: BuildPricedInvestmentPlanUseCase,
):
    intent_investment_plan = IntentInvestmentPlan(
        steps=[
            IntentInvestmentPlanStep(
                buy_asset_with_amount=None,
                sell_asset_with_amount=None,
            )
        ]
    )

    posting_repository.get_holding_balances.return_value = []
    chain.get_base_token.return_value = bnb_token

    priced_investment_plan = await use_case.execute(intent_investment_plan)

    assert priced_investment_plan == PricedInvestmentPlan(steps=[])

    exchange.convert_balance_to_token.assert_not_called()


@mark.asyncio
async def test_build_priced_investment_plan_use_case_execute_not_defined_sell_token(
    exchange: Exchange,
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: BuildPricedInvestmentPlanUseCase,
):
    intent_investment_plan = IntentInvestmentPlan(
        steps=[
            IntentInvestmentPlanStep(
                buy_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=eth_token,
                    amount=None,
                ),
                sell_asset_with_amount=None,
            )
        ]
    )

    posting_repository.get_holding_balances.return_value = []
    chain.get_base_token.return_value = bnb_token

    priced_investment_plan = await use_case.execute(intent_investment_plan)

    assert priced_investment_plan == PricedInvestmentPlan(
        steps=[
            PricedInvestmentPlanStep(
                buy_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=eth_token, amount=None, available_amount=Decimal("0")
                ),
                sell_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=bnb_token,
                    amount=None,
                    available_amount=Decimal("0"),
                ),
            )
        ]
    )

    exchange.convert_balance_to_token.assert_not_called()


@mark.asyncio
async def test_build_priced_investment_plan_use_case_execute_not_defined_buy_token(
    exchange: Exchange,
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: BuildPricedInvestmentPlanUseCase,
):
    intent_investment_plan = IntentInvestmentPlan(
        steps=[
            IntentInvestmentPlanStep(
                buy_asset_with_amount=None,
                sell_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=eth_token,
                    amount=None,
                ),
            )
        ]
    )

    posting_repository.get_holding_balances.return_value = []
    chain.get_base_token.return_value = bnb_token

    priced_investment_plan = await use_case.execute(intent_investment_plan)

    assert priced_investment_plan == PricedInvestmentPlan(
        steps=[
            PricedInvestmentPlanStep(
                buy_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=bnb_token, amount=None, available_amount=Decimal("0")
                ),
                sell_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=eth_token,
                    amount=None,
                    available_amount=Decimal("0"),
                ),
            )
        ]
    )

    exchange.convert_balance_to_token.assert_not_called()


@mark.asyncio
async def test_build_priced_investment_plan_use_case_execute_defined_buy_basket_amount(
    exchange: Exchange,
    posting_repository: PostingRepository,
    use_case: BuildPricedInvestmentPlanUseCase,
):
    intent_investment_plan = IntentInvestmentPlan(
        steps=[
            IntentInvestmentPlanStep(
                buy_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=big4_basket,
                    amount=Decimal("50.0"),
                ),
                sell_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=bnb_token,
                    amount=None,
                ),
            )
        ]
    )

    posting_repository.get_holding_balances.return_value = []
    exchange.convert_balance_to_token.return_value = ExchangeConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("1"),
            amount_atomic=1 * 10**18,
            decimals=18,
        ),
    )

    priced_investment_plan = await use_case.execute(intent_investment_plan)

    assert priced_investment_plan == PricedInvestmentPlan(
        steps=[
            PricedInvestmentPlanStep(
                buy_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=big4_basket,
                    amount=Decimal("50.0"),
                    available_amount=Decimal("0"),
                ),
                sell_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=bnb_token, amount=Decimal("1"), available_amount=Decimal("0")
                ),
            )
        ]
    )

    exchange.convert_balance_to_token.assert_called_once_with(
        balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**18,
            decimals=18,
        ),
        token=bnb_token,
        investment_parameters=mock.ANY,
    )


@mark.asyncio
async def test_build_priced_investment_plan_use_case_execute_defined_sell_basket_amount(
    exchange: Exchange,
    posting_repository: PostingRepository,
    use_case: BuildPricedInvestmentPlanUseCase,
):
    intent_investment_plan = IntentInvestmentPlan(
        steps=[
            IntentInvestmentPlanStep(
                buy_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=bnb_token,
                    amount=None,
                ),
                sell_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=big4_basket,
                    amount=Decimal("50.0"),
                ),
            )
        ]
    )

    posting_repository.get_holding_balances.return_value = []
    exchange.convert_balance_to_token.return_value = ExchangeConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("1"),
            amount_atomic=1 * 10**18,
            decimals=18,
        ),
    )

    priced_investment_plan = await use_case.execute(intent_investment_plan)

    assert priced_investment_plan == PricedInvestmentPlan(
        steps=[
            PricedInvestmentPlanStep(
                buy_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=bnb_token, amount=Decimal("1"), available_amount=Decimal("0")
                ),
                sell_asset_with_amount=PricedInvestmentPlanBalance(
                    asset=big4_basket,
                    amount=Decimal("50.0"),
                    available_amount=Decimal("0"),
                ),
            )
        ]
    )

    exchange.convert_balance_to_token.assert_called_once_with(
        balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("500"),
            amount_atomic=500 * 10**18,
            decimals=18,
        ),
        token=bnb_token,
        investment_parameters=mock.ANY,
    )


@mark.asyncio
async def test_build_priced_investment_plan_use_case_execute_available_amount_defined(
    exchange: Exchange,
    chain: Chain,
    posting_repository: PostingRepository,
    use_case: BuildPricedInvestmentPlanUseCase,
):
    intent_investment_plan = IntentInvestmentPlan(
        steps=[
            IntentInvestmentPlanStep(
                buy_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=bnb_token,
                    amount=None,
                ),
                sell_asset_with_amount=IntentInvestmentPlanBalance(
                    asset=usdt_token,
                    amount=Decimal("200"),
                ),
            )
        ]
    )

    chain.get_native_token_balance.return_value = BalanceAtomic(
        asset=bnb_token,
        amount=Decimal("5000"),
        amount_atomic=5000 * 10**18,
        decimals=18,
    )
    posting_repository.get_holding_balances.return_value = [
        Holding(
            balance=BalanceAtomic(
                asset=usdt_token,
                amount=Decimal("80000"),
                amount_atomic=80000 * 10**18,
                decimals=18,
            ),
            children=None,
        )
    ]
    exchange.convert_balance_to_token.return_value = ExchangeConvertedBalance(
        sell_balance=BalanceAtomic(
            asset=usdt_token,
            amount=Decimal("200"),
            amount_atomic=500 * 10**18,
            decimals=18,
        ),
        buy_balance=BalanceAtomic(
            asset=bnb_token,
            amount=Decimal("1"),
            amount_atomic=1 * 10**18,
            decimals=18,
        ),
    )

    priced_investment_plan = await use_case.execute(intent_investment_plan)

    assert priced_investment_plan.steps[0].buy_asset_with_amount is not None
    assert priced_investment_plan.steps[
        0
    ].buy_asset_with_amount.available_amount == Decimal("5000")

    assert priced_investment_plan.steps[0].sell_asset_with_amount is not None
    assert priced_investment_plan.steps[
        0
    ].sell_asset_with_amount.available_amount == Decimal("80000")

    posting_repository.get_holding_balances.assert_called_once()
