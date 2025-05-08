from dataclasses import asdict
from data_agent.ingestion.data_source.data_source import DataSource
from data_agent.similarity.similarity_document import SimilarityDocument

from protocol.token import Token
from protocol.basket import Basket


class MemecoinManiaBasketDataSource(DataSource):
    def __init__(self):
        self.basket = Basket(
            name="Memecoin mania",
            description="This basket offers concentrated exposure to the memecoin sector—tokens driven by internet culture, viral trends, and highly engaged online communities. Often fueled by humor, speculation, and social media influence, memecoins represent a unique and volatile niche within the crypto landscape. This basket is designed for investors who understand the high-risk, high-reward nature of memecoins and are looking to capture upside from rapidly shifting narratives and collective enthusiasm in the digital economy.",
            tokens=[
                Token(
                    name="Dogecoin",
                    display_name="Dogecoin",
                    ticker="DOGE",
                    address="0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                ),
                Token(
                    name="SHIBA INU",
                    display_name="Shiba Inu",
                    ticker="SHIB",
                    address="0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",
                ),
                Token(
                    name="Pepe",
                    display_name="Pepe",
                    ticker="PEPE",
                    address="0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
                ),
                Token(
                    name="FLOKI",
                    display_name="FLOKI",
                    ticker="FLOKI",
                    address="0xfb5b838b6cfeedc2873ab27866079ac55363d37e",
                ),
                Token(
                    name="Bonk",
                    display_name="Bonk",
                    ticker="BONK",
                    address="0xA697e272a73744b343528C3Bc4702F2565b2F422",
                ),
                Token(
                    name="Test",
                    display_name="Test",
                    ticker="TST",
                    address="0x86Bb94DdD16Efc8bc58e6b056e8df71D9e666429",
                ),
                Token(
                    name="mubarak",
                    display_name="mubarak",
                    ticker="MUBARAK",
                    address="0x5C85D6C6825aB4032337F11Ee92a72DF936b46F6",
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
