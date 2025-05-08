from dataclasses import asdict
from data_agent.ingestion.data_source.data_source import DataSource
from data_agent.similarity.similarity_document import SimilarityDocument

from protocol.token import Token
from protocol.basket import Basket


class CmcTop102025BasketDataSource(DataSource):
    def __init__(self):
        self.basket = Basket(
            name="Coinmarketcap Top 10 2025",
            description="This basket features a diverse mix of leading Layer-1 and utility tokens that form the backbone of the blockchain ecosystem in 2025. Representing widely adopted smart contract platforms, cross-chain protocols, and decentralized infrastructure, these assets reflect the continued maturity and interoperability of the crypto space. By excluding stablecoins, the basket maintains direct exposure to market-driven value while focusing on assets that power network operations, governance, and user interaction across decentralized applications.",
            tokens=[
                Token(
                    name="Binance Pegged Bitcoin",
                    display_name="Bitcoin",
                    ticker="BTC",
                    address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
                ),
                Token(
                    name="Binance Pegged ETH",
                    display_name="Ethereum",
                    ticker="ETH",
                    address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                ),
                Token(
                    name="XRP Token",
                    display_name="XRP",
                    ticker="XRP",
                    address="0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
                ),
                Token(
                    name="WBNB Token",
                    display_name="Binance Coin",
                    ticker="BNB",
                    address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                ),
                Token(
                    name="SOLANA",
                    display_name="Solana",
                    ticker="SOL",
                    address="0x570A5D26f7765Ecb712C0924E4De545B89fD43dF",
                ),
                Token(
                    name="Tron",
                    display_name="Tron",
                    ticker="TRX",
                    address="0x85EAC5Ac2F758618dFa09bDbe0cf174e7d574D5B",
                ),
                Token(
                    name="Dogecoin",
                    display_name="Dogecoin",
                    ticker="DOGE",
                    address="0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                ),
                Token(
                    name="Cardano Token",
                    display_name="Cardano",
                    ticker="ADA",
                    address="0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47",
                ),
                Token(
                    name="ChainLink Token",
                    display_name="Chainlink",
                    ticker="LINK",
                    address="0xf8a0bf9cf54bb92f17374d9e9a321e6a111a51bd",
                ),
                Token(
                    name="Avalanche",
                    display_name="Avalanche",
                    ticker="AVAX",
                    address="0x1ce0c2827e2ef14d5c4f29a091d735a204794041",
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
