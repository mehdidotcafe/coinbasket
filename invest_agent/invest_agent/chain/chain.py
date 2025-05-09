from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from protocol.token import Token

from invest_agent.chain.balance import Balance


class Chain(ABC):
    @abstractmethod
    def get_address(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_min_balance(self) -> Balance:
        raise NotImplementedError

    @abstractmethod
    def get_balance(self) -> Balance:
        raise NotImplementedError

    @abstractmethod
    def get_token_balance_amount(self, token_address_checksum: str) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    def get_base_token(self) -> Token:
        raise NotImplementedError

    @abstractmethod
    def sign_send_wait_transaction(
        self,
        amount: int,
        to_address: str | None = None,
        encoded_input: Any | None = None,
    ) -> Any:
        raise NotImplementedError

    @abstractmethod
    def compute_gas_estimate(
        self, amount: int, to_address: str, encoded_input: Any | None = None
    ) -> int:
        raise NotImplementedError
