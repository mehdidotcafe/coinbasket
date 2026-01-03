from api.address.address import Address
from api.chain.balance import Balance, BalanceAtomic
from api.investment.exchange.exchange import (
    Exchange,
    ExchangeConvertedBalance,
    ExchangeSignableSwap,
    SignableTransaction,
)
from api.investment.investment_parameters import InvestmentParameters
from api.protocol.asset import Asset


class TestExchange(Exchange):
    async def get_signable_swap(
        self,
        taker: Address,
        sell_balance: Balance[Asset],
        buy_balance: Balance[Asset],
        investment_parameters: InvestmentParameters,
    ) -> ExchangeSignableSwap:
        return ExchangeSignableSwap(
            sell_balance=BalanceAtomic(
                asset=sell_balance.asset,
                amount=sell_balance.amount,
                amount_atomic=sell_balance.amount * 10**sell_balance.asset.decimals,
                decimals=sell_balance.asset.decimals,
            ),
            buy_balance=BalanceAtomic(
                asset=buy_balance.asset,
                amount=buy_balance.amount,
                amount_atomic=buy_balance.amount * 10**buy_balance.asset.decimals,
                decimals=buy_balance.asset.decimals,
            ),
            signature_payload={"example_signature_field": "example_signature_value"},
            transaction=SignableTransaction(
                type="SIGN",
                amount=1000000,
                data={"example_field": "example_value"},
                gas=None,
                to_address=None,
            ),
        )

    async def convert_balance_to_asset(
        self,
        taker: Address,
        balance: BalanceAtomic[Asset],
        asset: Asset,
        investment_parameters: InvestmentParameters,
    ) -> ExchangeConvertedBalance:
        return ExchangeConvertedBalance(
            sell_balance=balance,
            buy_balance=BalanceAtomic(
                asset=asset,
                amount=balance.amount * 2,
                amount_atomic=balance.amount_atomic * 2,
                decimals=asset.decimals,
            ),
        )

    def get_name(self) -> str:
        return "TestExchange"
