from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from api.chain.balance import BalanceAtomic

from api.chain.chain import Gas
from api.investment.investment_parameters import InvestmentParameters

from api.investment.order.order import Order
from protocol.token import Token


@dataclass
class ExchangeConvertedBalance:
    sell_balance: BalanceAtomic[Token]
    buy_balance: BalanceAtomic[Token]


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
    async def convert_balance_to_token(
        self,
        balance: BalanceAtomic[Token],
        token: Token,
        investment_parameters: InvestmentParameters,
    ) -> ExchangeConvertedBalance:
        """Converts an asset balance to an asset."""
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the exchange."""
        raise NotImplementedError
