from abc import ABC, abstractmethod

from coinbasket.chain.balance import Balance


class Chain(ABC):
    @abstractmethod
    def get_min_balance(self) -> Balance:
        pass

    @abstractmethod
    def get_balance(self) -> Balance:
        pass

    @abstractmethod
    def send_and_wait_transaction(self) -> str:
        pass
