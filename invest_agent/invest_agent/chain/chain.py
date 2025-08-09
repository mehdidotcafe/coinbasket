from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from protocol.token import Token

from invest_agent.chain.balance import Balance


class TransactionFailure(Exception):
    def __init__(self):
        self.message = "Transaction failed."
        super().__init__(self.message)


@dataclass
class Gas:
    gas: int | None
    gas_price: int | None


class Chain(ABC):
    @abstractmethod
    def is_native_token(self, token: Token) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_chain_id(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_address(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_min_balance(self) -> Balance[Token]:
        raise NotImplementedError

    @abstractmethod
    async def get_balance(self) -> Balance[Token]:
        raise NotImplementedError

    @abstractmethod
    async def get_available_balance(
        self,
    ) -> Balance[Token]:
        raise NotImplementedError

    @abstractmethod
    async def get_token_balance_amount(self, token_address: str) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    async def get_address_balance(self, address: str) -> Balance[Token]:
        raise NotImplementedError

    @abstractmethod
    async def get_address_token_balance_amount(
        self, address: str, token_address: str
    ) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    def get_base_token(self) -> Token:
        raise NotImplementedError

    @abstractmethod
    async def sign_send_transaction(
        self,
        amount: int,
        gas: Gas | None = None,
        to_address: str | None = None,
        encoded_input: Any | None = None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def wait_transaction(
        self,
        transaction_hash: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def compute_gas_estimate(
        self, amount: int, to_address: str, encoded_input: Any | None = None
    ) -> int:
        raise NotImplementedError
