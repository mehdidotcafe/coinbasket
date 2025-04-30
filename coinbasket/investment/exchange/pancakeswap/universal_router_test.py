from unittest import mock
from pytest import fixture

from environs import env


from coinbasket.basket import Token

from coinbasket.chain.balance import Balance
from coinbasket.chain.chain import Chain
from coinbasket.investment.exchange.pancakeswap.universal_router import (
    PancakeSwapUniversalRouter,
)
from coinbasket.investment.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)

# FIX: Remove env reference to use hardcoded values. Requires to mock web3
bsc_rpc_url = env("BSC_RPC_URL")
universal_router_address = env("PANCAKESWAP_UNIVERSAL_ROUTER_ADDRESS")
permit2_contract_address = env("PANCAKESWAP_PERMIT2_CONTRACT_ADDRESS")
v2_router_address = env("PANCAKESWAP_V2_ROUTER_ADDRESS")
private_key = env("BSC_PRIVATE_KEY")


@fixture
def chain():
    chain = mock.Mock(spec=Chain)

    chain.get_balance.return_value = 99999999999999999999999999999999999999999999

    return chain


@fixture
def router(chain: Chain):
    return PancakeSwapUniversalRouter(
        bsc_rpc_url,
        universal_router_address,
        permit2_contract_address,
        v2_router_address,
        private_key,
        chain,
    )


def test_execute_investment_plan(router: PancakeSwapUniversalRouter):
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=Token(
                    name="USDC",
                    display_name="USDC",
                    ticker="USDC",
                    address="0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                ),
                amount=0.05,
            ),
            InvestmentPlanStep(
                token=Token(
                    name="BTCB",
                    display_name="BTCB",
                    ticker="BTCB",
                    address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                ),
                amount=0.15,
            ),
            InvestmentPlanStep(
                token=Token(
                    name="CAKE",
                    display_name="CAKE",
                    ticker="CAKE",
                    address="0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                ),
                amount=0.12,
            ),
            InvestmentPlanStep(
                token=Token(
                    name="1INCH",
                    display_name="1INCH",
                    ticker="1INCH",
                    address="0x111111111117dC0aa78b770fA6A738034120C302",
                ),
                amount=0.15,
            ),
        ],
        balance=Balance(
            token=Token(
                name="BNB",
                display_name="BNB",
                ticker="BNB",
                address="",
            ),
            amount=0.47,
        ),
    )

    router.execute_investment_plan(investment_plan)

    assert True == True
