from coinbasket.investment.investment_result import InvestmentResult
from coinbasket.storage.storage import Storage


class GetInvestmentResultUseCase:
    def __init__(self, storage: Storage[InvestmentResult]):
        self.storage = storage

    def execute(self) -> InvestmentResult | str:
        """
        Retrieves the investment result from the storage.

        Args:
            storage (Storage[InvestmentResult]): The storage instance to retrieve the investment result from.

        Returns:
            InvestmentResult | str: The retrieved investment result or a message indicating no result was found.
        """
        basket = self.storage.get("investment_result")

        return basket or "No invested basket found."
