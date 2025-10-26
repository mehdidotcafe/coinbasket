from decimal import Decimal
from data_agent.ingestion.data_source.data_source import DataSource
from data_agent.similarity.similarity_document import SimilarityDocument

from protocol.token import Token
from protocol.basket import Basket


class CryptoUmmahHalalBasketDataSource(DataSource):
    def __init__(self):
        self.id = "0f4b83f3-47eb-45a1-a698-688365ef2e64"
        self.basket = Basket(
            id=self.id,
            name="Cryptoummah.com Certified Halal",
            display_name="Cryptoummah.com Certified Halal",
            ticker="HALAL",
            description="This basket features a curated selection of major blockchain assets that align with Cryptoummah.com's halal screening framework. Focused on transparency, utility, and real-world adoption, these assets represent foundational layers of the global crypto economy while adhering to ethical and Shariah-compliant investment principles. This basket is designed for faith-conscious investors seeking exposure to leading digital assets without compromising on religious values.",
            denomination=Decimal("10.0"),
            tokens=[
                Token(
                    id="bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    name="Binance Pegged Bitcoin",
                    display_name="Bitcoin",
                    ticker="BTC",
                    address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                ),
                Token(
                    id="bsc:0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                    name="Binance Pegged ETH",
                    display_name="Ethereum",
                    ticker="ETH",
                    address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                ),
                Token(
                    id="bsc:0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
                    name="XRP Token",
                    display_name="XRP",
                    ticker="XRP",
                    address="0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
                ),
                Token(
                    id="bsc:0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                    name="WBNB Token",
                    display_name="Binance Coin",
                    ticker="BNB",
                    address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                ),
                Token(
                    id="bsc:0x570A5D26f7765Ecb712C0924E4De545B89fD43dF",
                    name="SOLANA",
                    display_name="Solana",
                    ticker="SOL",
                    address="0x570A5D26f7765Ecb712C0924E4De545B89fD43dF",
                ),
                Token(
                    id="bsc:0xce7de646e7208a4ef112cb6ed5038fa6cc6b12e3",
                    name="Tron",
                    display_name="Tron",
                    ticker="TRX",
                    address="0xce7de646e7208a4ef112cb6ed5038fa6cc6b12e3",
                ),
                Token(
                    id="bsc:0x3ee2200efb3400fabb9aacf31297cbdd1d435d47",
                    name="Cardano Token",
                    display_name="Cardano",
                    ticker="ADA",
                    address="0x3ee2200efb3400fabb9aacf31297cbdd1d435d47",
                ),
            ],
        )

    async def get(self):
        return [self.__map_basket_to_similarity_document(self.basket)]

    def version(self):
        return 2

    def __map_basket_to_similarity_document(self, basket: Basket) -> SimilarityDocument:
        """
        Map the basket to a similarity document.
        """
        return SimilarityDocument(
            id=self.id,
            page_content=str(basket),
            metadata={
                "source": basket.to_dict(),
                "type": "basket",
                "version": self.version(),
            },
        )
