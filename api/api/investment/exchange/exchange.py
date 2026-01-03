from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from api.address.address import Address
from api.chain.balance import BalanceAtomic

from api.chain.chain import Gas
from api.investment.investment_parameters import InvestmentParameters

from api.chain.balance import Balance
from api.protocol.token import Token


@dataclass
class ExchangeConvertedBalance:
    sell_balance: BalanceAtomic[Token]
    buy_balance: BalanceAtomic[Token]


@dataclass
class SignableTransaction:
    type: Literal["SIGN", "SEND"]
    amount: int
    data: Any
    gas: Gas | None = None
    to_address: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the TransactionData to a dictionary."""
        return {
            "type": self.type,
            "amount": self.amount,
            "data": self.data,
            "gas": self.gas.to_dict() if self.gas else None,
            "to_address": self.to_address,
        }


@dataclass
class ExchangeSignableSwap:
    sell_balance: BalanceAtomic[Token]
    buy_balance: BalanceAtomic[Token]
    signature_payload: dict[str, Any] | None
    transaction: SignableTransaction


class Exchange(ABC):
    @abstractmethod
    async def get_signable_swap(
        self,
        taker: Address,
        sell_balance: Balance[Token],
        buy_balance: Balance[Token],
        investment_parameters: InvestmentParameters,
    ) -> ExchangeSignableSwap:
        """Creates transaction data to be sent on-chain for the given order."""
        raise NotImplementedError

    @abstractmethod
    async def convert_balance_to_token(
        self,
        taker: Address,
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
