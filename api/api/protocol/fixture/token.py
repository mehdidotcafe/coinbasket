from api.protocol.token import Token

bnb_token = Token(
    id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    name="Binance Coin",
    display_name="Binance Coin",
    ticker="BNB",
    address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    description="Binance native token",
    decimals=18,
    categories=[
        "Crypto-Backed Tokens",
        "BNB Chain Ecosystem",
        "Wrapped-Tokens",
        "Coinbasket Selection",
    ],
    logo_uri="https://token-registry.s3.amazonaws.com/icons/tokens/bsc/64/0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c.png",
    trust_score=100,
)


wbnb_token = Token(
    id="bsc:0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    name="Wrapped BNB",
    display_name="Wrapped BNB",
    ticker="WBNB",
    address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    description="Wrapped BNB a wrapped version of the BNB native tokens on the BEP-20 standard on the Binance Smart Chain and other EVM-compatible chains. Not to be confused with BNB Native Token on the BSC Chain.",
    decimals=18,
    categories=[
        "Crypto-Backed Tokens",
        "BNB Chain Ecosystem",
        "Wrapped-Tokens",
    ],
    logo_uri="https://token-registry.s3.amazonaws.com/icons/tokens/bsc/64/0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c.png",
    trust_score=100,
)

eth_token = Token(
    id="bsc:0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
    name="Binance Ethereum",
    display_name="Ethereum",
    ticker="ETH",
    address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
    description="Binance pegged Ethereum token",
    decimals=18,
    categories=["BNB Chain Ecosystem", "Binance-Peg Tokens", "Coinbasket Selection"],
    logo_uri="https://coin-images.coingecko.com/coins/images/39580/thumb/weth.png",
    trust_score=100,
)

btc_token = Token(
    id="bsc:0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
    name="Binance Bitcoin",
    display_name="Bitcoin",
    ticker="BTC",
    address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
    description="Pegged tokens such as BTCB, are 100% backed by the native coin in reserve, which is Bitcoin (BTC) in BTCB's case.",
    decimals=18,
    categories=[
        "Crypto-Backed Tokens",
        "BNB Chain Ecosystem",
        "Harmony Ecosystem",
        "Bitcoin Ecosystem",
        "Coinbasket Selection",
    ],
    logo_uri="https://coin-images.coingecko.com/coins/images/14108/thumb/Binance-bitcoin.png",
    trust_score=100,
)

sol_token = Token(
    id="bsc:0x570A5D26f7765Ecb712C0924E4De545B89fD43dF",
    name="SOLANA",
    display_name="Solana",
    ticker="SOL",
    address="0x570A5D26f7765Ecb712C0924E4De545B89fD43dF",
    description="Solana token",
    decimals=18,
    categories=["BNB Chain Ecosystem", "Binance-Peg Tokens"],
    logo_uri="https://coin-images.coingecko.com/coins/images/54582/thumb/wsol.png",
    trust_score=100,
)

usdt_token = Token(
    id="bsc:0x55d398326f99059ff775485246999027b3197955",
    name="Tether USD",
    display_name="Tether USD",
    ticker="USDT",
    address="0x55d398326f99059ff775485246999027b3197955",
    description="Tether USD stablecoin",
    decimals=18,
    categories=[
        "BNB Chain Ecosystem",
        "Bridged USDT",
        "Bridged-Tokens",
        "Bridged Stablecoin",
        "Coinbasket Selection",
    ],
    logo_uri="https://coin-images.coingecko.com/coins/images/35021/thumb/USDT.png",
    trust_score=100,
)

shib_token = Token(
    id="bsc:0x2859e4544c4bb03966803b044a93563bd2d0dd4d",
    name="Shiba Inu",
    display_name="Shiba Inu",
    ticker="SHIB",
    address="0x2859e4544c4bb03966803b044a93563bd2d0dd4d",
    description="Shiba Inu meme token",
    decimals=18,
    categories=["BNB Chain Ecosystem", "Meme", "Dog-Themed", "Binance-Peg Tokens"],
    logo_uri="https://coin-images.coingecko.com/coins/images/50193/thumb/shib.png",
    trust_score=100,
)

cake_token = Token(
    id="bsc:0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
    name="PancakeSwap",
    display_name="PancakeSwap",
    ticker="CAKE",
    address="0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
    description="PancakeSwap is an automated market maker (“AMM”) that allows two tokens to be exchanged on the Binance Smart Chain. It is fast, cheap, and allows anyone to participate.",
    decimals=18,
    categories=[
        "Decentralized Exchange (DEX)",
        "Exchange-based Tokens",
        "Decentralized Finance (DeFi)",
        "Yield Farming",
        "Automated Market Maker (AMM)",
        "BNB Chain Ecosystem",
        "Perpetuals",
        "Solana Ecosystem",
        "Launchpad",
        "Arbitrum Ecosystem",
        "Ethereum Ecosystem",
        "Aptos Ecosystem",
        "ZkSync Ecosystem",
        "Linea Ecosystem",
        "Base Ecosystem",
        "Polygon zkEVM Ecosystem",
        "YZi Labs (Prev. Binance Labs) Portfolio",
        "opBNB Ecosystem",
        "GMCI DeFi Index",
        "GMCI Index",
        "Governance",
    ],
    logo_uri="https://coin-images.coingecko.com/coins/images/12632/thumb/pancakeswap-cake-logo_%281%29.png",
    trust_score=100,
)

doge_token = Token(
    id="bsc:0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
    name="Dogecoin",
    display_name="Dogecoin",
    ticker="DOGE",
    address="0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
    decimals=8,
    categories=[
        "BNB Chain Ecosystem",
        "Avalanche Ecosystem",
        "Meme",
        "Binance-Peg Tokens",
    ],
    description="Tokens that are wrapped and pegged by Binance on a 1:1 ratio to the corresponding native token. Also supports BEP20 token deposits and withdrawals at Binance.com",
    logo_uri="https://coin-images.coingecko.com/coins/images/15768/thumb/dogecoin.png",
    trust_score=100,
)

pepe_token = Token(
    id="bsc:0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
    name="Pepe",
    display_name="Pepe",
    ticker="PEPE",
    address="0x25d887Ce7a35172C62FeBFD67a1856F20FaEbB00",
    description="What is the project about?\r\nPepe is a community based meme token surround the iconic meme Pepe the frog. Pepe aims to leverage the power of such an iconic meme to become the most memeable memecoin in existence. \r\n\r\nWhat makes your project unique?\r\nPepe is here to make memecoins great again. Ushering in a new paradigm for memecoins, Pepe represents the memecoin in it's purest simplicity. With zero taxes, liquidity locked forever, and contract immutable, Pepe is for the people, forever. Pepe is about culture, rallying together a community to have fun and enjoy memes, fueled purely by memetic power. \r\n\r\nHistory of your project.\r\nPepe was stealth launched on Friday, April 14th, 2023. \r\n\r\nWhat’s next for your project?\r\nPepe will focus on developing a tight-knit community around the token and building resources to enrich the communities knowledge and success in crypto through a token gated group, newsletter, and more tools. \r\n\r\nWhat can your token be used for?\r\nPepe can be used to speculate on the power of memes, and does not pretend to be anything more. \r\n",
    categories=[
        "BNB Chain Ecosystem",
        "Avalanche Ecosystem",
        "Meme",
        "Arbitrum Ecosystem",
        "Ethereum Ecosystem",
        "Frog-Themed",
        "GMCI Meme Index",
        "GMCI Index",
        "The Boy’s Club",
        "4chan-Themed",
    ],
    decimals=18,
    trust_score=100,
)


xrp_token = Token(
    id="bsc:0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
    name="Binance XRP",
    display_name="XRP",
    ticker="XRP",
    address="0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE",
    decimals=18,
    description="Tokens that are wrapped and pegged by Binance on a 1:1 ratio to the corresponding native token. Also supports BEP20 token deposits and withdrawals at Binance.com",
    categories=[
        "Crypto-Backed Tokens",
        "BNB Chain Ecosystem",
        "Binance-Peg Tokens",
        "Coinbasket Selection",
    ],
    trust_score=100,
)

ada_token = Token(
    id="bsc:0x3ee2200efb3400fabb9aacf31297cbdd1d435d47",
    name="Binance Cardano",
    display_name="Cardano",
    ticker="ADA",
    address="0x3ee2200efb3400fabb9aacf31297cbdd1d435d47",
    decimals=18,
    description="Tokens that are wrapped and pegged by Binance on a 1:1 ratio to the corresponding native token. Also supports BEP20 token deposits and withdrawals at Binance.com",
    categories=[
        "Crypto-Backed Tokens",
        "BNB Chain Ecosystem",
        "Harmony Ecosystem",
        "Binance-Peg Tokens",
    ],
    trust_score=100,
)

trx_token = Token(
    id="bsc:0xce7de646e7208a4ef112cb6ed5038fa6cc6b12e3",
    name="TRON",
    display_name="TRON",
    ticker="TRX",
    address="0xce7de646e7208a4ef112cb6ed5038fa6cc6b12e3",
    decimals=6,
    description="",
    categories=["BNB Chain Ecosystem", "Bridged-Tokens"],
    trust_score=100,
)
