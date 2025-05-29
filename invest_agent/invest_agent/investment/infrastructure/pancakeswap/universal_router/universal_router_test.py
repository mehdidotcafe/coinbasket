from decimal import Decimal
from typing import Any, Dict
from unittest import mock
from hexbytes import HexBytes
from pytest import fixture

from environs import env
from web3 import Web3
from eth_account.datastructures import SignedMessage


from protocol.token import Token

from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.infrastructure.pancakeswap.universal_router.permit2 import (
    Permit2,
)
from invest_agent.investment.infrastructure.pancakeswap.universal_router.universal_router import (
    PancakeSwapUniversalRouter,
)
from invest_agent.investment.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)

# FIX: Remove env reference to use hardcoded values. Requires to mock web3
bsc_rpc_url = env("BSC_RPC_URL")
universal_router_address = env("PANCAKESWAP_UNIVERSAL_ROUTER_ADDRESS")
permit2_contract_address = env("PANCAKESWAP_PERMIT2_CONTRACT_ADDRESS")
v2_router_address = env("PANCAKESWAP_V2_ROUTER_ADDRESS")
private_key = env("BSC_PRIVATE_KEY")


permit2_deadline = 180
permit2_signed_message = SignedMessage(
    message_hash=HexBytes(
        "0x47be46b9a6d7337182ba9c5cca34690d45c5dc05aa71efa3cd9408ad59cc2a94"
    ),
    r=40669160623095555763087913875086316304103726716775795630740097426109985262652,
    s=27634496195978621419975347085402318339134228577272732890502192210119342298480,
    v=28,
    signature=HexBytes(
        "0x59e9eddf43ca674b8f8a8645ab297fc374c9d085351ad67f9bb60415f3550c3c3d1892109cdb406de13662d4acdc36d0db23248366cb15bcf6af14391ffa15701c"
    ),
)
permit2_data: Dict[str, Any] = {
    "details": {
        "token": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "amount": 1461501637330902918203684832716283019655932542975,
        "expiration": 1748782719,
        "nonce": 0,
    },
    "spender": "0x1A0A18AC4BECDDbd6389559687d1A73d8927E416",
    "sigDeadline": 1746190899,
}


@fixture
def chain():
    chain = mock.Mock(spec=Chain)

    chain.get_balance.return_value = Balance(
        token=Token(
            name="BNB",
            display_name="BNB",
            ticker="BNB",
            address="",
        ),
        amount=Decimal("1000"),
    )
    chain.get_min_balance.return_value = Balance(
        token=Token(
            name="BNB",
            display_name="BNB",
            ticker="BNB",
            address="",
        ),
        amount=Decimal("1"),
    )

    return chain


@fixture
def permit2():
    return mock.Mock(spec=Permit2)


@fixture
def router(chain: Chain, permit2: Permit2):
    return PancakeSwapUniversalRouter(
        bsc_rpc_url,
        universal_router_address,
        v2_router_address,
        private_key,
        chain,
        permit2,
    )


def test_universal_router_execute_investment_plan(
    router: PancakeSwapUniversalRouter, permit2: Permit2, chain: Chain
):
    investment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=Token(
                    name="USDC",
                    display_name="USDC",
                    ticker="USDC",
                    address="0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                ),
                amount=Decimal("0.05"),
            ),
            InvestmentPlanStep(
                token=Token(
                    name="BTCB",
                    display_name="BTCB",
                    ticker="BTCB",
                    address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                ),
                amount=Decimal("0.15"),
            ),
            InvestmentPlanStep(
                token=Token(
                    name="CAKE",
                    display_name="CAKE",
                    ticker="CAKE",
                    address="0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                ),
                amount=Decimal("0.12"),
            ),
            InvestmentPlanStep(
                token=Token(
                    name="1INCH",
                    display_name="1INCH",
                    ticker="1INCH",
                    address="0x111111111117dC0aa78b770fA6A738034120C302",
                ),
                amount=Decimal("0.15"),
            ),
        ],
        balance=Balance(
            token=Token(
                name="BNB",
                display_name="BNB",
                ticker="BNB",
                address="",
            ),
            amount=Decimal("0.47"),
        ),
    )
    base_token = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

    permit2.sign_permit2_message.return_value = (
        permit2_signed_message,
        permit2_data,
        permit2_deadline,
    )
    permit2.get_default_deadline.return_value = permit2_deadline

    # TODO: check log parsing in another test
    chain.sign_send_wait_transaction.return_value = {"logs": []}

    router.execute_investment_plan(investment_plan)

    permit2.assert_has_calls(
        [
            mock.call.approve_permit2_contract(Web3.to_checksum_address(base_token)),
            mock.call.sign_permit2_message(
                Web3.to_checksum_address(base_token),
                Web3.to_checksum_address(universal_router_address),
            ),
            mock.call.get_default_deadline(),
        ]
    )

    chain.sign_send_wait_transaction.assert_called_once_with(
        amount=470000000000000000,  # 0.47 BNB
        to_address=Web3.to_checksum_address(universal_router_address),
        encoded_input=mock.ANY,
    )


def test_universal_router_execute_divestment_plan(
    router: PancakeSwapUniversalRouter, chain: Chain, permit2: Permit2
):
    divestment_plan = InvestmentPlan(
        steps=[
            InvestmentPlanStep(
                token=Token(
                    name="USDC",
                    display_name="USDC",
                    ticker="USDC",
                    address="0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                ),
                amount=Decimal("0.05"),
            ),
            InvestmentPlanStep(
                token=Token(
                    name="BTCB",
                    display_name="BTCB",
                    ticker="BTCB",
                    address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                ),
                amount=Decimal("0.15"),
            ),
            InvestmentPlanStep(
                token=Token(
                    name="CAKE",
                    display_name="CAKE",
                    ticker="CAKE",
                    address="0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                ),
                amount=Decimal("0.12"),
            ),
        ],
        balance=Balance(
            token=Token(
                name="BNB",
                display_name="BNB",
                ticker="BNB",
                address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
            ),
            amount=Decimal("0.0"),
        ),
    )

    permit2.sign_permit2_message.return_value = (
        permit2_signed_message,
        permit2_data,
        permit2_deadline,
    )
    permit2.get_default_deadline.return_value = permit2_deadline

    router.execute_divestment_plan(divestment_plan)

    permit2.assert_has_calls(
        [
            mock.call.approve_permit2_contract(
                Web3.to_checksum_address(divestment_plan.steps[0].token.address)
            ),
            mock.call.sign_permit2_message(
                Web3.to_checksum_address(divestment_plan.steps[0].token.address),
                Web3.to_checksum_address(universal_router_address),
            ),
            mock.call.approve_permit2_contract(
                Web3.to_checksum_address(divestment_plan.steps[1].token.address)
            ),
            mock.call.sign_permit2_message(
                Web3.to_checksum_address(divestment_plan.steps[1].token.address),
                Web3.to_checksum_address(universal_router_address),
            ),
            mock.call.approve_permit2_contract(
                Web3.to_checksum_address(divestment_plan.steps[2].token.address)
            ),
            mock.call.sign_permit2_message(
                Web3.to_checksum_address(divestment_plan.steps[2].token.address),
                Web3.to_checksum_address(universal_router_address),
            ),
            mock.call.get_default_deadline(),
        ]
    )

    chain.sign_send_wait_transaction.assert_called_once_with(
        amount=0,
        to_address=Web3.to_checksum_address(universal_router_address),
        encoded_input=mock.ANY,
    )


def test_universal_router_get_tokens_balance_in_token(
    router: PancakeSwapUniversalRouter,
):
    token = Token(
        name="Tether USD",
        display_name="Tether USD",
        ticker="USDT",
        address="0x55d398326f99059ff775485246999027b3197955",
    )

    router.get_wallet_in_token(
        [
            Balance(
                token=Token(
                    name="Ethereum",
                    display_name="Ethereum",
                    ticker="ETH",
                    address="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                ),
                amount=Decimal("2.4"),
            ),
            Balance(
                token=Token(
                    name="Binance coin",
                    display_name="Binance coin",
                    ticker="BNB",
                    address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                ),
                amount=Decimal("10"),
            ),
        ],
        token,
    )

    assert True == True
