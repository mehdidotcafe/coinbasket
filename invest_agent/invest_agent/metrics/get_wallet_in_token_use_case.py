from invest_agent.investment.basket_investment import BasketInvestment, Bid
from invest_agent.investment.exchange.exchange import Exchange
from invest_agent.storage.storage import Storage
from protocol.token import Token
from invest_agent.chain.chain import Chain


class GetWalletInTokenUseCase:
    def __init__(
        self, storage: Storage[BasketInvestment], exchange: Exchange, chain: Chain
    ):
        self.storage = storage
        self.exchange = exchange
        self.chain = chain

    def execute(self, token: Token):
        basket_investment = self.storage.get("basket_investment")

        return self.exchange.get_wallet_in_token(
            [self.chain.get_balance()]
            + self.__map_basket_investment_bids_to_balances(
                basket_investment[0].bids if basket_investment else []
            ),
            token,
        )

    def __map_basket_investment_bids_to_balances(self, bids: list[Bid]):
        return [bid.buy_balance for bid in bids]
