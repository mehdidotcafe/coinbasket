from decimal import Decimal
from api.ingestion.data_source.data_source import DataSource
from api.similarity.similarity_document import SimilarityDocument

from api.protocol.token import Token
from api.protocol.basket import Basket


class CmcTop102025BasketDataSource(DataSource):
    def __init__(self):
        self.id = "bec1f741-61f2-4903-a4fd-363c63deaa4e"
        self.basket = Basket(
            id=self.id,
            name="Coinmarketcap Top 10 2025",
            display_name="Coinmarketcap Top 10 2025",
            ticker="CMC10",
            description="This basket features a diverse mix of leading Layer-1 and utility tokens that form the backbone of the blockchain ecosystem in 2025. Representing widely adopted smart contract platforms, cross-chain protocols, and decentralized infrastructure, these assets reflect the continued maturity and interoperability of the crypto space. By excluding stablecoins, the basket maintains direct exposure to market-driven value while focusing on assets that power network operations, governance, and user interaction across decentralized applications.",
            denomination=Decimal("10.0"),
            tokens=[
                Token(
                    id="bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    name="Binance Pegged Bitcoin",
                    display_name="Bitcoin",
                    ticker="BTC",
                    address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                    categories=[],
                    description="",
                    decimals=18,
                ),
                Token(
                    id="bsc:0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                    name="Binance Pegged ETH",
                    display_name="Ethereum",
                    ticker="ETH",
                    address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                    categories=[],
                    description="",
                    decimals=18,
                ),
                Token(
                    id="bsc:0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
                    name="XRP Token",
                    display_name="XRP",
                    ticker="XRP",
                    address="0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
                    categories=[],
                    description="",
                    decimals=18,
                ),
                Token(
                    id="bsc:0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                    name="WBNB Token",
                    display_name="Binance Coin",
                    ticker="BNB",
                    address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                    categories=[],
                    description="",
                    decimals=18,
                ),
                Token(
                    id="bsc:0x570A5D26f7765Ecb712C0924E4De545B89fD43dF",
                    name="SOLANA",
                    display_name="Solana",
                    ticker="SOL",
                    address="0x570A5D26f7765Ecb712C0924E4De545B89fD43dF",
                    categories=[],
                    description="",
                    decimals=18,
                ),
                Token(
                    id="bsc:0xCE7de646e7208a4Ef112cb6ed5038FA6cC6b12e3",
                    name="Tron",
                    display_name="Tron",
                    ticker="TRX",
                    address="0xCE7de646e7208a4Ef112cb6ed5038FA6cC6b12e3",
                    categories=[],
                    description="",
                    decimals=6,
                ),
                Token(
                    id="bsc:0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                    name="Dogecoin",
                    display_name="Dogecoin",
                    ticker="DOGE",
                    address="0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                    categories=[],
                    description="",
                    decimals=8,
                ),
                Token(
                    id="bsc:0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47",
                    name="Cardano Token",
                    display_name="Cardano",
                    ticker="ADA",
                    address="0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47",
                    categories=[],
                    description="",
                    decimals=18,
                ),
                Token(
                    id="bsc:0xf8a0bf9cf54bb92f17374d9e9a321e6a111a51bd",
                    name="ChainLink Token",
                    display_name="Chainlink",
                    ticker="LINK",
                    address="0xf8a0bf9cf54bb92f17374d9e9a321e6a111a51bd",
                    categories=[],
                    description="",
                    decimals=18,
                ),
                Token(
                    id="bsc:0x1ce0c2827e2ef14d5c4f29a091d735a204794041",
                    name="Avalanche",
                    display_name="Avalanche",
                    ticker="AVAX",
                    address="0x1ce0c2827e2ef14d5c4f29a091d735a204794041",
                    categories=[],
                    description="",
                    decimals=18,
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
