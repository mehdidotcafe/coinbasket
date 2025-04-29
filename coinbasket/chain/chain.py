from abc import ABC, abstractmethod

from coinbasket.basket import Token
from coinbasket.chain.balance import Balance


class Chain(ABC):
    @abstractmethod
    def get_min_balance(self) -> Balance:
        pass

    @abstractmethod
    def get_balance(self) -> Balance:
        pass

    @abstractmethod
    def get_base_token(self) -> Token:
        pass

    @abstractmethod
    def send_and_wait_transaction(self) -> str:
        pass
