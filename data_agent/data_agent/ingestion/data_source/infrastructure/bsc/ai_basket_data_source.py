from decimal import Decimal
from data_agent.ingestion.data_source.data_source import DataSource
from data_agent.similarity.similarity_document import SimilarityDocument

from protocol.token import Token
from protocol.basket import Basket


class AiBasketDataSource(DataSource):
    def __init__(self):
        self.id = "50041f0f-dc5f-4d3d-9029-538ad1a794b4"
        self.basket = Basket(
            id=self.id,
            name="AI",
            display_name="AI",
            ticker="AI",
            description="This basket provides targeted exposure to cutting-edge blockchain projects focused on infrastructure scalability, decentralized data, and artificial intelligence. These tokens represent foundational technologies driving the next wave of decentralized applications, offering a blend of utility, interoperability, and innovation. Ideal for forward-looking investors, the basket captures key narratives shaping the evolution of Web3—from smart contract optimization to intelligent agent networks.",
            denomination=Decimal("10.0"),
            tokens=[
                Token(
                    id="bsc:0x1Fa4a73a3F0133f0025378af00236f3aBDEE5D63",
                    name="NEAR Protocol",
                    display_name="NEAR Protocol",
                    ticker="NEAR",
                    address="0x1Fa4a73a3F0133f0025378af00236f3aBDEE5D63",
                ),
                Token(
                    id="bsc:0x0D8Ce2A99Bb6e3B7Db580eD848240e4a0F9aE153",
                    name="Filecoin",
                    display_name="Filecoin",
                    ticker="FIL",
                    address="0x0D8Ce2A99Bb6e3B7Db580eD848240e4a0F9aE153",
                ),
                Token(
                    id="bsc:0x031b41e504677879370e9DBcF937283A8691Fa7f",
                    name="FetchToken",
                    display_name="Fetch.ai",
                    ticker="FET",
                    address="0x031b41e504677879370e9DBcF937283A8691Fa7f",
                ),
                Token(
                    id="bsc:0xa2b726b1145a4773f68593cf171187d8ebe4d495",
                    name="Injective",
                    display_name="Injective",
                    ticker="INJ",
                    address="0xa2b726b1145a4773f68593cf171187d8ebe4d495",
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
