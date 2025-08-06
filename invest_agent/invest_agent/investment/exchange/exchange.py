from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from invest_agent.chain.asset_balance import AssetBalance
from invest_agent.chain.balance import Balance

from invest_agent.chain.chain import Gas
from invest_agent.investment.investment_parameters import InvestmentParameters

from invest_agent.investment.order.order import Order
from protocol.token import Token


# TODO: Delete TokenConvertedBalance
@dataclass
class TokenConvertedBalance:
    sell_balance: Balance
    buy_balance: Balance


@dataclass
class ConvertedBalance:
    sell_balance: AssetBalance
    buy_balance: AssetBalance


@dataclass
class Wallet:
    balances: list[TokenConvertedBalance]
    total_balance: Balance


@dataclass
class TransactionData:
    type: Literal["SIGN", "SEND"]
    amount: int
    encoded_input: Any
    gas: Gas | None = None
    to_address: str | None = None


class Exchange(ABC):
    @abstractmethod
    async def build_transactions(
        self,
        order: Order,
        investment_parameters: InvestmentParameters,
    ) -> list[TransactionData]:
        """Creates transaction data to be sent on-chain for the given order."""
        raise NotImplementedError

    @abstractmethod
    async def get_wallet_in_token(
        self,
        tokens_balance: list[Balance],
        token: Token,
        investment_parameters: InvestmentParameters,
    ) -> Wallet:
        raise NotImplementedError

    @abstractmethod
    async def convert_balance_to_token(
        self,
        balance: Balance,
        token: Token,
        investment_parameters: InvestmentParameters,
    ) -> TokenConvertedBalance:
        """Converts an asset balance to an asset."""
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the exchange."""
        raise NotImplementedError
