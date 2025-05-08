from dataclasses import asdict
from data_agent.ingestion.data_source.data_source import DataSource
from data_agent.similarity.similarity_document import SimilarityDocument

from protocol.token import Token
from protocol.basket import Basket


class Big4BasketDataSource(DataSource):
    def __init__(self):
        self.basket = Basket(
            name="Big4",
            description="This curated basket offers broad exposure to the crypto market through a selection of established, high-liquidity digital assets spanning different blockchain ecosystems. It is designed to balance long-term value preservation with growth potential, reflecting both foundational and emerging trends in decentralized technology. The combination supports diversification across transaction layers, use cases, and network adoption, making it a resilient core holding for crypto-oriented portfolios.",
            tokens=[
                Token(
                    name="Binance Pegged Bitcoin",
                    display_name="Bitcoin",
                    ticker="BTC",
                    address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                ),
                Token(
                    name="Binance Pegged Ethereum",
                    display_name="Ethereum",
                    ticker="ETH",
                    address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                ),
                Token(
                    name="SOLANA",
                    display_name="Solana",
                    ticker="SOL",
                    address="0x570A5D26f7765Ecb712C0924E4De545B89fD43dF",
                ),
                Token(
                    name="WBNB Token",
                    display_name="Binance Coin",
                    ticker="WBNB",
                    address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                ),
            ],
        )

    def get(self):
        return [self.__map_basket_to_similarity_document(self.basket)]

    def version(self):
        return 1

    def __map_basket_to_similarity_document(self, basket: Basket) -> SimilarityDocument:
        """
        Map the basket to a similarity document.
        """
        return SimilarityDocument(
            page_content=str(basket),
            metadata={"source": asdict(basket), "type": "basket"},
        )
