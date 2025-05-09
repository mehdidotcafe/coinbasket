from invest_agent.investment.basket_investment import BasketInvestment
from invest_agent.storage.storage import Storage


class GetBasketInvestmentUseCase:
    def __init__(self, storage: Storage[BasketInvestment]):
        self.storage = storage

    def execute(self) -> BasketInvestment | str:
        """
        Retrieves the investment result from the storage.

        Args:
            storage (Storage[BasketInvestment]): The storage instance to retrieve the investment result from.

        Returns:
            BasketInvestment | str: The retrieved investment result or a message indicating no result was found.
        """
        basket = self.storage.get("basket_investment")

        if basket is None:
            return "No basket investment found."

        return basket[0]
