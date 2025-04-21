from abc import ABC, abstractmethod


class IChain(ABC):
    @abstractmethod
    def get_balance(self) -> float:
        pass

    @abstractmethod
    def send_and_wait_transaction(self) -> str:
        pass
