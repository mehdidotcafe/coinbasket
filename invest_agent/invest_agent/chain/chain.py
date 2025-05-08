from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from protocol.token import Token

from invest_agent.chain.balance import Balance


class Chain(ABC):
    @abstractmethod
    def get_min_balance(self) -> Balance:
        pass

    @abstractmethod
    def get_balance(self) -> Balance:
        pass

    @abstractmethod
    def get_token_balance_amount(self, token_address_checksum: str) -> Decimal:
        pass

    @abstractmethod
    def get_base_token(self) -> Token:
        pass

    @abstractmethod
    def sign_send_wait_transaction(
        self, amount: int, to_address: str, encoded_input: Any | None = None
    ) -> Any:
        pass

    @abstractmethod
    def compute_gas_estimate(
        self, amount: int, to_address: str, encoded_input: Any | None = None
    ) -> int:
        pass
