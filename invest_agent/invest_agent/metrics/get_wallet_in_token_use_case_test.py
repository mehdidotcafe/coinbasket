from decimal import Decimal
from unittest import mock
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain

# from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.exchange.exchange import Wallet, Exchange
from invest_agent.investment.investment_parameters import (
    IntegratorFee,
    InvestmentParameters,
)
from invest_agent.metrics.get_wallet_in_token_use_case import (
    Configuration,
    GetWalletInTokenUseCase,
)
from invest_agent.storage.storage import Storage
from protocol.token import Token
from pytest import fixture, mark


# @fixture
# def storage():
#     return mock.Mock(spec=Storage[BasketInvestment])


@fixture
def exchange():
    return mock.Mock(spec=Exchange)


@fixture
def chain():
    return mock.Mock(spec=Chain)


# @fixture
# def basket_investment():
#     return BasketInvestment(
#         name="basket_investment",
#         description="description",
#         type="type",
#         invested_at="2023-10-01T00:00:00Z",
#         bids=[
#             Bid(
#                 token=Token(
#                     id="bsc:0x00001",
#                     name="Token 1",
#                     display_name="Token 1",
#                     ticker="TK1",
#                     address="0x00001",
#                 ),
#                 sell_balance=Balance(
#                     amount=Decimal("1000"),
#                     token=Token(
#                         id="bsc:0x00001",
#                         name="Token 1",
#                         display_name="Token 1",
#                         ticker="TK1",
#                         address="0x00001",
#                     ),
#                 ),
#                 buy_balance=Balance(
#                     amount=Decimal("333"),
#                     token=Token(
#                         id="bsc:0x00008",
#                         name="Token 8",
#                         display_name="Token 8",
#                         ticker="TK8",
#                         address="0x00008",
#                     ),
#                 ),
#             ),
#             Bid(
#                 token=Token(
#                     id="bsc:0x00002",
#                     name="Token 2",
#                     display_name="Token 2",
#                     ticker="TK2",
#                     address="0x00002",
#                 ),
#                 sell_balance=Balance(
#                     amount=Decimal("99999"),
#                     token=Token(
#                         id="bsc:0x00002",
#                         name="Token 2",
#                         display_name="Token 2",
#                         ticker="TK2",
#                         address="0x00002",
#                     ),
#                 ),
#                 buy_balance=Balance(
#                     amount=Decimal("9384"),
#                     token=Token(
#                         id="bsc:0x00009",
#                         name="Token 9",
#                         display_name="Token 9",
#                         ticker="TK9",
#                         address="0x00009",
#                     ),
#                 ),
#             ),
#         ],
#         status="invested",
#     )


@fixture
def balance():
    return Balance(
        amount=Decimal("0"),
        token=Token(
            id="bsc:0x00000",
            name="BNB",
            display_name="BNB",
            ticker="BNB",
            address="0x00000",
        ),
    )


@fixture
def configuration() -> Configuration:
    return {
        "fee_integrator_address": "0x1234567890abcdef1234567890abcdef12345678",
        "fee_value_in_percentage": Decimal(0.15),
    }


@fixture
def wallet():
    return Wallet(
        balances=[],
        total_balance=Balance(
            amount=Decimal("0"),
            token=Token(
                id="bsc:0x55d398326f99059ff775485246999027b3197955",
                name="Tether USD",
                display_name="Tether USD",
                ticker="USDT",
                address="0x55d398326f99059ff775485246999027b3197955",
            ),
        ),
    )


# @mark.asyncio
# async def test_get_wallet_in_token_use_case_basket_investment_not_found(
#     storage: Storage[BasketInvestment],
#     exchange: Exchange,
#     chain: Chain,
#     configuration: Configuration,
#     balance: Balance,
# ):
#     storage.get.return_value = None
#     chain.get_balance.return_value = balance

#     use_case = GetWalletInTokenUseCase(
#         storage=storage, exchange=exchange, chain=chain, configuration=configuration
#     )

#     await use_case.execute(
#         Token(
#             id="bsc:0x55d398326f99059ff775485246999027b3197955",
#             name="Tether USD",
#             display_name="Tether USD",
#             ticker="USDT",
#             address="0x55d398326f99059ff775485246999027b3197955",
#         ),
#     )

#     exchange.get_wallet_in_token.assert_called_once_with(
#         tokens_balance=[
#             Balance(
#                 amount=Decimal("0"),
#                 token=Token(
#                     id="bsc:0x00000",
#                     name="BNB",
#                     display_name="BNB",
#                     ticker="BNB",
#                     address="0x00000",
#                 ),
#             ),
#         ],
#         token=mock.ANY,
#         investment_parameters=mock.ANY,
#     )


# @mark.asyncio
# async def test_get_wallet_in_token_use_case_basket_investment(
#     storage: Storage[BasketInvestment],
#     exchange: Exchange,
#     basket_investment: BasketInvestment,
#     chain: Chain,
#     configuration: Configuration,
#     balance: Balance,
#     wallet: Wallet,
# ):
#     storage.get.return_value = [basket_investment, 1]
#     chain.get_balance.return_value = balance
#     exchange.get_wallet_in_token.return_value = wallet

#     use_case = GetWalletInTokenUseCase(storage, exchange, chain, configuration)

#     result = await use_case.execute(
#         Token(
#             id="bsc:0x55d398326f99059ff775485246999027b3197955",
#             name="Tether USD",
#             display_name="Tether USD",
#             ticker="USDT",
#             address="0x55d398326f99059ff775485246999027b3197955",
#         ),
#     )

#     assert result == Wallet(
#         balances=[],
#         total_balance=Balance(
#             amount=Decimal("0"),
#             token=Token(
#                 id="bsc:0x55d398326f99059ff775485246999027b3197955",
#                 name="Tether USD",
#                 display_name="Tether USD",
#                 ticker="USDT",
#                 address="0x55d398326f99059ff775485246999027b3197955",
#             ),
#         ),
#     )

#     storage.get.assert_called_once_with("basket_investment")
#     exchange.get_wallet_in_token.assert_called_once_with(
#         tokens_balance=[
#             Balance(
#                 amount=Decimal("0"),
#                 token=Token(
#                     id="bsc:0x00000",
#                     name="BNB",
#                     display_name="BNB",
#                     ticker="BNB",
#                     address="0x00000",
#                 ),
#             ),
#             Balance(
#                 amount=Decimal("333"),
#                 token=Token(
#                     id="bsc:0x00008",
#                     name="Token 8",
#                     display_name="Token 8",
#                     ticker="TK8",
#                     address="0x00008",
#                 ),
#             ),
#             Balance(
#                 amount=Decimal("9384"),
#                 token=Token(
#                     id="bsc:0x00009",
#                     name="Token 9",
#                     display_name="Token 9",
#                     ticker="TK9",
#                     address="0x00009",
#                 ),
#             ),
#         ],
#         token=Token(
#             id="bsc:0x55d398326f99059ff775485246999027b3197955",
#             name="Tether USD",
#             display_name="Tether USD",
#             ticker="USDT",
#             address="0x55d398326f99059ff775485246999027b3197955",
#         ),
#         investment_parameters=InvestmentParameters(
#             slippage_tolerance_in_percentage=Decimal("1"),
#             integrator_fee=IntegratorFee(
#                 recipient="0x1234567890abcdef1234567890abcdef12345678",
#                 value_in_percentage=Decimal(0.15),
#                 token=Token(
#                     id="bsc:0x55d398326f99059ff775485246999027b3197955",
#                     name="Tether USD",
#                     display_name="Tether USD",
#                     ticker="USDT",
#                     address="0x55d398326f99059ff775485246999027b3197955",
#                 ),
#             ),
#         ),
#     )


# @mark.asyncio
# async def test_get_wallet_in_token_use_case_basket_investment_with_no_integrator_fee(
#     storage: Storage[BasketInvestment],
#     exchange: Exchange,
#     basket_investment: BasketInvestment,
#     chain: Chain,
#     balance: Balance,
#     wallet: Wallet,
# ):
#     storage.get.return_value = [basket_investment, 1]
#     chain.get_balance.return_value = balance
#     exchange.get_wallet_in_token.return_value = wallet

#     use_case = GetWalletInTokenUseCase(
#         storage=storage,
#         exchange=exchange,
#         chain=chain,
#         configuration=Configuration(
#             fee_integrator_address=None,
#             fee_value_in_percentage=None,
#         ),
#     )

#     await use_case.execute(
#         Token(
#             id="bsc:0x55d398326f99059ff775485246999027b3197955",
#             name="Tether USD",
#             display_name="Tether USD",
#             ticker="USDT",
#             address="0x55d398326f99059ff775485246999027b3197955",
#         ),
#     )

#     storage.get.assert_called_once_with("basket_investment")
#     exchange.get_wallet_in_token.assert_called_once_with(
#         tokens_balance=mock.ANY,
#         token=mock.ANY,
#         investment_parameters=InvestmentParameters(
#             slippage_tolerance_in_percentage=mock.ANY,
#             integrator_fee=None,
#         ),
#     )
