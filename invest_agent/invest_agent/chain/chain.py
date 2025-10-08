from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from protocol.asset import Asset
from protocol.token import Token

from invest_agent.chain.balance import (
    AmountAtomic,
    AmountReadable,
    BalanceAtomic,
)


class TransactionFailure(Exception):
    def __init__(self):
        self.message = "Transaction failed."
        super().__init__(self.message)


@dataclass
class Gas:
    gas: int | None
    gas_price: int | None


@dataclass
class ParsedReceipt:
    executed_sell_balance: BalanceAtomic
    executed_buy_balance: BalanceAtomic
    rate: Decimal | None = None


class Chain(ABC):
    @abstractmethod
    def is_native_token(self, asset: Asset) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_wrapped_native_token(self, asset: Asset) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_chain_id(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_address(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_min_balance(self) -> BalanceAtomic[Token]:
        raise NotImplementedError

    @abstractmethod
    async def get_native_token_balance(self) -> BalanceAtomic[Token]:
        raise NotImplementedError

    @abstractmethod
    async def get_native_token_available_balance(
        self,
    ) -> BalanceAtomic[Token]:
        raise NotImplementedError

    @abstractmethod
    async def get_token_balance(self, token: Token) -> BalanceAtomic[Token]:
        raise NotImplementedError

    @abstractmethod
    async def get_address_native_token_balance(
        self, address: str
    ) -> BalanceAtomic[Token]:
        raise NotImplementedError

    @abstractmethod
    async def get_address_token_balance(
        self, address: str, token: Token
    ) -> BalanceAtomic[Token]:
        raise NotImplementedError

    @abstractmethod
    def get_base_token(self) -> Token:
        raise NotImplementedError

    @abstractmethod
    def get_wrapped_base_token(self) -> Token:
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

    @abstractmethod
    async def get_token_decimals(self, token_address: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def convert_amount_to_amount_atomic(
        self, token: Token, amount_readable: AmountReadable
    ) -> tuple[AmountAtomic, int]:
        raise NotImplementedError

    @abstractmethod
    async def convert_amount_atomic_to_amount(
        self, token: Token, amount_atomic: AmountAtomic
    ) -> tuple[AmountReadable, int]:
        raise NotImplementedError

    @abstractmethod
    async def parse_transaction_receipt(
        self, sell_token: Token, buy_token: Token, transaction_hash: str
    ) -> ParsedReceipt:
        raise NotImplementedError
