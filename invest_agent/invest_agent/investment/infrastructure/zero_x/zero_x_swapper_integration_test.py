from decimal import Decimal
from invest_agent.configuration import Configuration
from invest_agent.http_request.infrastructure.requests_http_request import (
    RequestsHttpRequest,
)
from invest_agent.infrastructure.bsc.chain.bsc_chain import BscChain
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_swapper import (
    ZeroXSwapper,
)
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
from protocol.token import Token
from web3 import Web3


def test_integration_zero_x_swapper_execute_investment_plan():
    configuration = Configuration()

    api_client = ZeroXApiClient(
        {
            "zero_x_api_url": configuration.zero_x_api_url,
            "zero_x_api_key": configuration.zero_x_api_key,
        },
        RequestsHttpRequest(),
    )

    chain = BscChain(
        w3=Web3(Web3.HTTPProvider(configuration.bsc_rpc_url)),
        private_key=configuration.bsc_private_key,
        base_token=Token(
            name=configuration.bsc_base_token_name,
            display_name=configuration.bsc_base_token_display_name,
            ticker=configuration.bsc_base_token_ticker,
            address=configuration.bsc_base_token_address,
        ),
    )
    zero_x_swapper = ZeroXSwapper(
        api_client=api_client,
        chain=chain,
        configuration={
            "bsc_rpc_url": configuration.bsc_rpc_url,
            "private_key": configuration.bsc_private_key,
        },
        w3=Web3(Web3.HTTPProvider(configuration.bsc_rpc_url)),
    )

    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=btc_token,
                amount=Decimal(1),
            ),
            InvestmentPlanStep(
                token=eth_token,
                amount=Decimal(1),
            ),
            InvestmentPlanStep(
                token=wbnb_token,
                amount=Decimal(3),
            ),
            InvestmentPlanStep(
                token=sol_token,
                amount=Decimal(2),
            ),
            InvestmentPlanStep(
                token=usdt_token,
                amount=Decimal(2),
            ),
        ],
        balance=Balance(
            token=bnb_token,
            amount=Decimal(10),
        ),
    )

    zero_x_swapper.execute_investment_plan(investment_plan)


def test_integration_zero_x_swapper_execute_divestment_plan():
    configuration = Configuration()

    api_client = ZeroXApiClient(
        {
            "zero_x_api_url": configuration.zero_x_api_url,
            "zero_x_api_key": configuration.zero_x_api_key,
        },
        RequestsHttpRequest(),
    )

    chain = BscChain(
        w3=Web3(Web3.HTTPProvider(configuration.bsc_rpc_url)),
        private_key=configuration.bsc_private_key,
        base_token=Token(
            name=configuration.bsc_base_token_name,
            display_name=configuration.bsc_base_token_display_name,
            ticker=configuration.bsc_base_token_ticker,
            address=configuration.bsc_base_token_address,
        ),
    )
    zero_x_swapper = ZeroXSwapper(
        api_client=api_client,
        chain=chain,
        configuration={
            "bsc_rpc_url": configuration.bsc_rpc_url,
            "private_key": configuration.bsc_private_key,
        },
        w3=Web3(Web3.HTTPProvider(configuration.bsc_rpc_url)),
    )

    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=eth_token,
                amount=Decimal(1),
            ),
            InvestmentPlanStep(
                token=wbnb_token,
                amount=Decimal(3),
            ),
            InvestmentPlanStep(
                token=sol_token,
                amount=Decimal(2),
            ),
        ],
        balance=Balance(
            token=bnb_token,
            amount=Decimal(10),
        ),
    )

    # TODO: Find a way to set the balance of the account directly
    bids = zero_x_swapper.execute_investment_plan(investment_plan)

    divestment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=eth_token,
                amount=bids[0].balance_out.amount,
            ),
            InvestmentPlanStep(
                token=wbnb_token,
                amount=bids[1].balance_out.amount,
            ),
            InvestmentPlanStep(
                token=sol_token,
                amount=bids[2].balance_out.amount,
            ),
        ],
        balance=Balance(
            token=bnb_token,
            amount=Decimal(5),
        ),
    )

    zero_x_swapper.execute_divestment_plan(divestment_plan)
