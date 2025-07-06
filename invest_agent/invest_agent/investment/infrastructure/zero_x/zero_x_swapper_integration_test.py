from decimal import Decimal
from invest_agent.configuration import Configuration
from shared.http_request.infrastructure.requests_http_request import (
    RequestsHttpRequest,
)
from invest_agent.infrastructure.bsc.chain.bsc_chain import BscChain
from invest_agent.infrastructure.bsc.chain.bsc_contract import BscContract
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_swapper import (
    ZeroXSwapper,
)
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep
from invest_agent.chain.balance import Balance


from protocol.fixture.token import (
    bnb_token,
    eth_token,
    wbnb_token,
    sol_token,
    btc_token,
    usdt_token,
)
from web3 import AsyncHTTPProvider, AsyncWeb3
from pytest import fixture, mark


@fixture
def zero_x_swapper():
    configuration = Configuration()

    w3 = AsyncWeb3(AsyncHTTPProvider(configuration.bsc_rpc_url))

    api_client = ZeroXApiClient(
        {
            "zero_x_api_url": configuration.zero_x_api_url,
            "zero_x_api_key": configuration.zero_x_api_key,
        },
        RequestsHttpRequest(),
    )

    chain = BscChain(
        w3=w3,
        private_key=configuration.bsc_private_key,
    )
    contract = BscContract(w3=w3)

    return ZeroXSwapper(
        api_client=api_client,
        chain=chain,
        contract=contract,
        configuration={
            "bsc_rpc_url": configuration.bsc_rpc_url,
            "private_key": configuration.bsc_private_key,
        },
        w3=w3,
    )


@mark.asyncio
async def test_integration_zero_x_swapper_execute_investment_plan(
    zero_x_swapper: ZeroXSwapper,
):
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=btc_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("1.39283831092838"),
                ),
            ),
            InvestmentPlanStep(
                token=eth_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("1.289891283838"),
                ),
            ),
            InvestmentPlanStep(
                token=wbnb_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("3.189234898934589"),
                ),
            ),
            InvestmentPlanStep(
                token=sol_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("2.0000000000"),
                ),
            ),
            InvestmentPlanStep(
                token=usdt_token,
                sell_balance=Balance(
                    token=bnb_token,
                    amount=Decimal("0.9213909028917891"),
                ),
            ),
        ],
        sell_total_balance=Balance(
            token=bnb_token,
            amount=Decimal(10),
        ),
    )
    investment_parameters = InvestmentParameters(
        slippage_tolerance_in_percentage=Decimal(5),
    )

    await zero_x_swapper.execute_investment_plan(investment_plan, investment_parameters)


@mark.asyncio
async def test_integration_zero_x_swapper_execute_divestment_plan(
    zero_x_swapper: ZeroXSwapper,
):
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=eth_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal(1)),
            ),
            InvestmentPlanStep(
                token=wbnb_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal(3)),
            ),
            InvestmentPlanStep(
                token=sol_token,
                sell_balance=Balance(token=bnb_token, amount=Decimal(2)),
            ),
        ],
        sell_total_balance=Balance(
            token=bnb_token,
            amount=Decimal(10),
        ),
    )
    investment_parameters = InvestmentParameters(
        slippage_tolerance_in_percentage=Decimal(5),
    )

    # TODO: Find a way to set the balance of the account directly
    bids = await zero_x_swapper.execute_investment_plan(
        investment_plan, investment_parameters
    )

    divestment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=eth_token,
                sell_balance=Balance(
                    token=eth_token,
                    amount=bids[0].buy_balance.amount,
                ),
            ),
            InvestmentPlanStep(
                token=wbnb_token,
                sell_balance=Balance(
                    token=wbnb_token,
                    amount=bids[1].buy_balance.amount,
                ),
            ),
            InvestmentPlanStep(
                token=sol_token,
                sell_balance=Balance(
                    token=sol_token,
                    amount=bids[2].buy_balance.amount,
                ),
            ),
        ],
        sell_total_balance=Balance(
            token=bnb_token,
            amount=Decimal(5),
        ),
    )
    investment_parameters = InvestmentParameters(
        slippage_tolerance_in_percentage=Decimal(5),
    )

    await zero_x_swapper.execute_divestment_plan(divestment_plan, investment_parameters)
