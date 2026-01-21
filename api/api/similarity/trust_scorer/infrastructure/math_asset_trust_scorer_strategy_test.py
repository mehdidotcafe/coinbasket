import json
from typing import Any

from api.similarity.trust_scorer.infrastructure.math_asset_trust_scorer_strategy import (
    MathAssetTrustScorerStrategy,
)
from pytest import fixture, mark

from api.token.infrastructure.coingecko.coingecko_token_repository import (
    GetFromAddressToken,
)


@fixture
def raw_tokens() -> list[dict[str, Any]]:
    file_path = "data/dev_data_source_assets.json"

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


@fixture
def strategy() -> MathAssetTrustScorerStrategy:
    return MathAssetTrustScorerStrategy()


@fixture
def bitcoin() -> dict[str, Any]:
    return {
        "id": "binance-bitcoin",
        "name": "Binance Bitcoin",
        "symbol": "btcb",
        "categories": [
            "Crypto-Backed Tokens",
            "BNB Chain Ecosystem",
            "Harmony Ecosystem",
        ],
        "localization": {"en": "Binance Bitcoin"},
        "description": {
            "en": "Pegged tokens such as BTCB, are 100% backed by the native coin in reserve, which is Bitcoin (BTC) in BTCB’s case."
        },
        "links": {"homepage": [], "whitepaper": ""},
        "detail_platforms": {
            "binance_smart_chain": {
                "decimal_place": 18,
                "contract_address": "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c",
            }
        },
        "sentiment_votes_up_percentage": None,
        "sentiment_votes_down_percentage": None,
        "watchlist_portfolio_users": 3768,
        "market_cap_rank": None,
        "image": {
            "small": "https://coin-images.coingecko.com/coins/images/14108/small/Binance-bitcoin.png?1696513829"
        },
        "market_data": {
            "mcap_to_tvl_ratio": None,
            "fdv_to_tvl_ratio": None,
            "ath_change_percentage": {"usd": -24.48843},
            "ath_date": {"usd": "2025-10-07T12:17:11.658Z"},
            "atl_change_percentage": {"usd": 517.19845},
            "atl_date": {"usd": "2022-11-21T19:43:29.896Z"},
            "market_cap": {"usd": 0.0},
            "market_cap_rank": None,
            "fully_diluted_valuation": {"usd": 6255114841.0},
            "total_volume": {"usd": 79673549.0},
            "price_change_percentage_24h": -1.02109,
            "price_change_percentage_7d": 5.67915,
            "price_change_percentage_30d": 9.44372,
            "price_change_percentage_60d": 1.98756,
            "price_change_percentage_200d": -10.83719,
            "price_change_percentage_1y": -3.34953,
            "total_supply": 65300.96996478414,
            "max_supply": None,
            "circulating_supply": 0.0,
            "total_value_locked": None,
        },
        "developer_data": {"forks": 0, "stars": 0},
        "tickers": [
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 32382679.7557351,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 120.0970464937,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 68.8073862052,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XBB73BB2505AC4643D5C0A99C2A1F34B3DFD09D11",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 55221.4523864,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 8767758.08937333,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X1BA42E5193DFA8B03D15DD1B86A3113BBBEF8EEB",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 3170.5338621798,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 72.4802990807,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "THENA V3",
                    "identifier": "thena-v3",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 3.7304870669,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Pancakeswap Infinity CLMM (BSC)",
                    "identifier": "pancakeswap-infinity-clmm",
                    "has_trading_incentive": False,
                },
                "base": "0X0000000000000000000000000000000000000000",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 330.5845660699,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 1057.55732667,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 1176101.21935647,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "SquadSwap WOW (BSC)",
                    "identifier": "squadswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 3.9389212677,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Pancakeswap Infinity CLMM (BSC)",
                    "identifier": "pancakeswap-infinity-clmm",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 264882.332685538,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XA67C48F86FC6D0176DCA38883CA8153C76A532C7",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 7.04256613,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.6105529128,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "DNAX",
                    "identifier": "dnax",
                    "has_trading_incentive": False,
                },
                "base": "0XA9EE28C80F960B889DFBD1902055218CBA016F75",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 35.9020142852,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "THENA FUSION",
                    "identifier": "thena-fusion",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.8696769594,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "THENA V3",
                    "identifier": "thena-v3",
                    "has_trading_incentive": False,
                },
                "base": "0X4AAE823A6A0B376DE6A78E74ECC5B079D38CBCF7",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.8473606569,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V4 (BSC)",
                    "identifier": "uniswap-v4-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0X8AC76A51CC950D9822D68B83FE1AD97B32CD580D",
                "volume": 0.8994016387,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X1D2F0DA169CEB9FC7B3144628DB156F3F6C60DBE",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 533995.681105646,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "THENA V3",
                    "identifier": "thena-v3",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 41.6075647555,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X4AAE823A6A0B376DE6A78E74ECC5B079D38CBCF7",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 8.8489353172,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 49.3098562835,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 9.5193970325,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "THENA FUSION",
                    "identifier": "thena-fusion",
                    "has_trading_incentive": False,
                },
                "base": "0XF4C8E32EADEC4BFE97E0F595ADD0F4450A863A11",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 197752.743319967,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "DNAX",
                    "identifier": "dnax",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0X8AC76A51CC950D9822D68B83FE1AD97B32CD580D",
                "volume": 0.2996728976,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XC58C1117DA964AEBE91FEF88F6F5703E79BDA574",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 10.68529191,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Unchain X",
                    "identifier": "unchain-x",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.1517012165,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Biswap",
                    "identifier": "biswap",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 1.8245440203,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "DNAX",
                    "identifier": "dnax",
                    "has_trading_incentive": False,
                },
                "base": "0X8D0D000EE44948FC98C9B98A4FA4921476F08B0D",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 16477.7773527072,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 2213036.11179445,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XE9E7CEA3DEDCA5984780BAFC599BD69ADD087D56",
                "volume": 0.167431754,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Unchain X",
                    "identifier": "unchain-x",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 3.1190224966,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "ApeSwap",
                    "identifier": "apeswap_bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.025206833,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Pancakeswap Infinity CLMM (BSC)",
                    "identifier": "pancakeswap-infinity-clmm",
                    "has_trading_incentive": False,
                },
                "base": "0X0000000000000000000000000000000000000000",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 21.8832410208,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V1 (BSC)",
                    "identifier": "pancakeswap-v1-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.02328103396,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 56.7660966856,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V4 (BSC)",
                    "identifier": "uniswap-v4-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 14672.1553966965,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X3E7F1039896454B9CB27C53CC7383E1AB9D9512A",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 250847.90959114,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "DNAX",
                    "identifier": "dnax",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XE9E7CEA3DEDCA5984780BAFC599BD69ADD087D56",
                "volume": 0.1257148541,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 84.5924596664,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X1A4D41219C547F3A0EE36CF3D9E68F80699CF283",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 15351.6666577951,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Biswap V3",
                    "identifier": "biswap-v3-1",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 2490.0972040783,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Biswap",
                    "identifier": "biswap",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 3015.5289205852,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Mdex BSC",
                    "identifier": "mdex_bsc",
                    "has_trading_incentive": True,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.3701409619,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Biswap",
                    "identifier": "biswap",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.0235351449,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "AutoShark Finance",
                    "identifier": "autoshark_finance",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.3739191252,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 22883.7091211174,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XF3B3F0971F4C7A06740B653557566446919A4098",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 27116.5832175133,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Nomiswap",
                    "identifier": "nomiswap",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 1226.7648391553,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Bakeryswap",
                    "identifier": "bakeryswap",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.005851700001,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V1 (BSC)",
                    "identifier": "pancakeswap-v1-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.3214347139,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X2F8A339B5889FFAC4C5A956787CDA593B3C36867",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 915.8150776044,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XF585B5B4F22816BAF7629AEA55B701662630397B",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 150290.629212022,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X1BA42E5193DFA8B03D15DD1B86A3113BBBEF8EEB",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 290.2328871387,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X3EE2200EFB3400FABB9AACF31297CBDD1D435D47",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 81830.3853923541,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Unchain X",
                    "identifier": "unchain-x",
                    "has_trading_incentive": False,
                },
                "base": "0X4F0572CA0BF96F5AE17B7062D97CEA3F35BDEA6F",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 654803.09209841,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X4AAE823A6A0B376DE6A78E74ECC5B079D38CBCF7",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.3429057625,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0X8AC76A51CC950D9822D68B83FE1AD97B32CD580D",
                "volume": 1.645667739,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Mdex BSC",
                    "identifier": "mdex_bsc",
                    "has_trading_incentive": True,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 780.1621853521,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Unchain X",
                    "identifier": "unchain-x",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 1613.7284213656,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X0555E30DA8F98308EDB960AA94C0DB47230D2B9C",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 1.14586834,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Biswap V3",
                    "identifier": "biswap-v3-1",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.005293675698,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X0E09FABB73BD3ADE0A17ECC321FD13A19E81CE82",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 50443.1094373288,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0X8AC76A51CC950D9822D68B83FE1AD97B32CD580D",
                "volume": 0.2171213289,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.6752462261,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X0555E30DA8F98308EDB960AA94C0DB47230D2B9C",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.2226707,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "CoinSwap",
                    "identifier": "coinswap",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.001982653428,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X3EE2200EFB3400FABB9AACF31297CBDD1D435D47",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 209261.66739136,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "SquadSwap WOW (BSC)",
                    "identifier": "squadswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.003246332344,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "THENA FUSION",
                    "identifier": "thena-fusion",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.4375456637,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X4338665CBB7B2485A8855A139B75D5E34AB0DB94",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 256.8187497001,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X26C5E01524D2E6280A48F2C50FF6DE7E52E9611C",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 13.6646300815,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Nomiswap",
                    "identifier": "nomiswap",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.002427787896,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XF8A0BF9CF54BB92F17374D9E9A321E6A111A51BD",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 1337.5403933639,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Pancakeswap Infinity CLMM (BSC)",
                    "identifier": "pancakeswap-infinity-clmm",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.2490988326,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V4 (BSC)",
                    "identifier": "uniswap-v4-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X4C32964715E9A42F8D119BFA8917D57822D3ADF1",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 1750.021008624,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BabyDogeSwap",
                    "identifier": "babydogeswap",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.0007058480149,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XF6718B2701D4A6498EF77D7C152B2137AB28B8A3",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.2177768717,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Pancakeswap Infinity CLMM (BSC)",
                    "identifier": "pancakeswap-infinity-clmm",
                    "has_trading_incentive": False,
                },
                "base": "0XBE1936A67F503E0EAF2434B0CF9F4E3D7100008A",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 6962.3866288493,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Biswap V3",
                    "identifier": "biswap-v3-1",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.01818436707,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.08076607939,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X4338665CBB7B2485A8855A139B75D5E34AB0DB94",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 554.6861575702,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BabySwap",
                    "identifier": "babyswap",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 115.7575917618,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Nomiswap",
                    "identifier": "nomiswap",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.04560177654,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 8050.70378251,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X4AAE823A6A0B376DE6A78E74ECC5B079D38CBCF7",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.3354568177,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XFCB8A4B1A0B645E08064E05B98E9CC6F48D2AA57",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 26479.8404537983,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 4321.6175183995,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 70997.10985923,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XF8A0BF9CF54BB92F17374D9E9A321E6A111A51BD",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 437.4805204759,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "SmarDex (BSC)",
                    "identifier": "smardex-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XFDC66A08B0D0DC44C17BBD471B88F49F50CDD20F",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 8492.6908703409,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 10809.9851522331,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Planet Finance",
                    "identifier": "planet_finance",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.0004936876534,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V4 (BSC)",
                    "identifier": "uniswap-v4-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 0.1124281495,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Planet Finance",
                    "identifier": "planet_finance",
                    "has_trading_incentive": False,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XE9E7CEA3DEDCA5984780BAFC599BD69ADD087D56",
                "volume": 0.0006229431639,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X0E09FABB73BD3ADE0A17ECC321FD13A19E81CE82",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 178.0370630202,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V4 (BSC)",
                    "identifier": "uniswap-v4-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 185.946313036,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Mdex BSC",
                    "identifier": "mdex_bsc",
                    "has_trading_incentive": True,
                },
                "base": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 0.0004433985041,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V4 (BSC)",
                    "identifier": "uniswap-v4-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X55D398326F99059FF775485246999027B3197955",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 197.5487992743,
            },
        ],
        "platforms": {
            "binance-smart-chain": "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c",
            "harmony-shard-0": "0x34224dcf981da7488fdd01c7fdd64e74cd55dcf7",
        },
        "logoURI": None,
    }


@fixture
def harryPotterObamaSonic10Inu() -> dict[str, Any]:
    return {
        "id": "harrypotterobamasonic10in",
        "name": "HarryPotterObamaSonic10Inu (ETH)",
        "symbol": "bitcoin",
        "categories": [
            "BNB Chain Ecosystem",
            "Meme",
            "Ethereum Ecosystem",
            "Base Ecosystem",
            "Berachain Ecosystem",
            "Murad Picks",
            "Binance Alpha Spotlight",
            "4chan-Themed",
        ],
        "localization": {"en": "HarryPotterObamaSonic10Inu (ETH)"},
        "description": {
            "en": "HarryPotterObamaSonic10Inu (Ticker: BITCOIN) is a endgame of crypto-assets (0 Tax). BITCOIN incentivizes the creation of novel and entertaining meme content. With ownership renounced and Liquidity locked, our robust growing community has taken the lead; we have successfully completed a full audit, an NFT collection, and are exploring partnerships with other tokens in the space, a one-of-a -kind website, and one-of-a-kind merchandise and ecommerce site in the works based on the legendary meme that inspired BITCOIN's creation. Our goal is to create an ecosystem for active community members to meet, collaborate, and share our rich lore (the archive of our token's storied history) with the world."
        },
        "links": {"homepage": ["https://hpos10i.com"], "whitepaper": ""},
        "detail_platforms": {
            "binance_smart_chain": {
                "decimal_place": 8,
                "contract_address": "0xc4044d67585d421495fb0bf08c50b15683647003",
            }
        },
        "sentiment_votes_up_percentage": 66.67,
        "sentiment_votes_down_percentage": 33.33,
        "watchlist_portfolio_users": 17599,
        "market_cap_rank": 744,
        "image": {
            "small": "https://coin-images.coingecko.com/coins/images/30323/small/hpos10i_logo_casino_night-dexview.png?1696529224"
        },
        "market_data": {
            "mcap_to_tvl_ratio": None,
            "fdv_to_tvl_ratio": None,
            "ath_change_percentage": {"usd": -88.09868},
            "ath_date": {"usd": "2024-10-13T05:00:06.998Z"},
            "atl_change_percentage": {"usd": 6599.47405},
            "atl_date": {"usd": "2023-05-31T23:11:46.784Z"},
            "market_cap": {"usd": 44273583.0},
            "market_cap_rank": 744,
            "fully_diluted_valuation": {"usd": 44273583.0},
            "total_volume": {"usd": 9217012.0},
            "price_change_percentage_24h": -6.35458,
            "price_change_percentage_7d": -6.22195,
            "price_change_percentage_30d": 7.76502,
            "price_change_percentage_60d": 2.98716,
            "price_change_percentage_200d": -27.83537,
            "price_change_percentage_1y": -78.26001,
            "total_supply": 999798155.0,
            "max_supply": 1000000000.0,
            "circulating_supply": 999798155.0,
            "total_value_locked": None,
        },
        "developer_data": {"forks": 0, "stars": 0},
        "tickers": [
            {
                "trust_score": "yellow",
                "market": {
                    "name": "OrangeX",
                    "identifier": "orangex",
                    "has_trading_incentive": False,
                },
                "base": "BITCOIN",
                "target": "USDT",
                "volume": 707787.45,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Gate",
                    "identifier": "gate",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "USDT",
                "volume": 5832148.8,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Bybit",
                    "identifier": "bybit_spot",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "USDT",
                "volume": 2192901.0,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (Ethereum)",
                    "identifier": "uniswap_v3",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0XC02AAA39B223FE8D0A0E5C4F27EAD9083C756CC2",
                "volume": 1325362.55928373,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Hotcoin",
                    "identifier": "hotcoin_global",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "USDT",
                "volume": 22510912.96,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (Ethereum)",
                    "identifier": "uniswap_v3",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0XC02AAA39B223FE8D0A0E5C4F27EAD9083C756CC2",
                "volume": 605970.32885334,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V2 (Ethereum)",
                    "identifier": "uniswap_v2",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0XE0F63A424A4439CBE457D80E4F4B51AD25B2C56C",
                "volume": 364561.18789077,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "HTX",
                    "identifier": "huobi",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "USDT",
                "volume": 147530016.4184,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "MEXC",
                    "identifier": "mxc",
                    "has_trading_incentive": False,
                },
                "base": "HARRY",
                "target": "USDT",
                "volume": 1741216.44,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Ourbit",
                    "identifier": "ourbit",
                    "has_trading_incentive": False,
                },
                "base": "BITCOIN",
                "target": "USDT",
                "volume": 1050278.64,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "CoinW",
                    "identifier": "coinw",
                    "has_trading_incentive": False,
                },
                "base": "BITCOIN",
                "target": "USDT",
                "volume": 5781271.69,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Aerodrome SlipStream",
                    "identifier": "aerodrome-slipstream",
                    "has_trading_incentive": False,
                },
                "base": "0X2A06A17CBC6D0032CAC2C6696DA90F29D39A1A29",
                "target": "0X4200000000000000000000000000000000000006",
                "volume": 288955.32253467,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "KuCoin",
                    "identifier": "kucoin",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "USDT",
                "volume": 0.0,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BloFin",
                    "identifier": "blofin_spot",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "USDT",
                "volume": 690733.88,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XC4044D67585D421495FB0BF08C50B15683647003",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 150507.810784,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Meteora",
                    "identifier": "meteora",
                    "has_trading_incentive": False,
                },
                "base": "CTGIAZUK12KCCB8SOSN4NT2NZTZLGTPQDWYQYR2SYATC",
                "target": "EPJFWDD5AUFQSSQEM2QN1XZYBAPC8G4WEGGKZWYTDT1V",
                "volume": 124850.93755241,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Raydium (CLMM)",
                    "identifier": "raydium-clmm",
                    "has_trading_incentive": False,
                },
                "base": "CTGIAZUK12KCCB8SOSN4NT2NZTZLGTPQDWYQYR2SYATC",
                "target": "SO11111111111111111111111111111111111111112",
                "volume": 57804.49877343,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "LBank",
                    "identifier": "lbank",
                    "has_trading_incentive": False,
                },
                "base": "BITCOIN",
                "target": "USDT",
                "volume": 1688548.9,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (Base)",
                    "identifier": "uniswap-v3-base",
                    "has_trading_incentive": False,
                },
                "base": "0X2A06A17CBC6D0032CAC2C6696DA90F29D39A1A29",
                "target": "0X833589FCD6EDB6E08F4C7C32D4F71B54BDA02913",
                "volume": 81271.77382854,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "CoinEx",
                    "identifier": "coinex",
                    "has_trading_incentive": False,
                },
                "base": "BITCOIN",
                "target": "USDT",
                "volume": 566825.31075199,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "BTSE",
                    "identifier": "btse",
                    "has_trading_incentive": False,
                },
                "base": "HARRY",
                "target": "USDT",
                "volume": 1477096.110945082,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Bittime",
                    "identifier": "bittime",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "IDR",
                "volume": 667860.6,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (Ethereum)",
                    "identifier": "uniswap_v3",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0XA0B86991C6218B36C1D19D4A2E9EB0CE3606EB48",
                "volume": 89435.12246938,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "XT.COM",
                    "identifier": "xt",
                    "has_trading_incentive": False,
                },
                "base": "BITCOIN",
                "target": "USDT",
                "volume": 8041297.23,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Raydium (CLMM)",
                    "identifier": "raydium-clmm",
                    "has_trading_incentive": False,
                },
                "base": "26S3UGB9HUND1QSPAPY1ZYGCRITXAOOGG7O63BMN89YQ",
                "target": "CTGIAZUK12KCCB8SOSN4NT2NZTZLGTPQDWYQYR2SYATC",
                "volume": 7181309.70040306,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Cypher",
                    "identifier": "cypher",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0XC02AAA39B223FE8D0A0E5C4F27EAD9083C756CC2",
                "volume": 12624.22219512,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BVOX",
                    "identifier": "bitvenus_spot",
                    "has_trading_incentive": False,
                },
                "base": "HARRY",
                "target": "USDT",
                "volume": 169078.24,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Kraken",
                    "identifier": "kraken",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "USD",
                "volume": 31737.47799,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Kodiak V3",
                    "identifier": "kodiak-v3",
                    "has_trading_incentive": False,
                },
                "base": "0X6B26F778BFAE56CFB4BF9B62C678D9D40E725227",
                "target": "0X6969696969696969696969696969696969696969",
                "volume": 2524.09975957,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V2 (Ethereum)",
                    "identifier": "uniswap_v2",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0XC02AAA39B223FE8D0A0E5C4F27EAD9083C756CC2",
                "volume": 1645.24819056,
            },
            {
                "trust_score": "red",
                "market": {
                    "name": "Raydium (CLMM)",
                    "identifier": "raydium-clmm",
                    "has_trading_incentive": False,
                },
                "base": "6OGZHHZDRQR9PGV6HZ2MNZE7URZBMAFYBBWUYP1FHITX",
                "target": "CTGIAZUK12KCCB8SOSN4NT2NZTZLGTPQDWYQYR2SYATC",
                "volume": 28845.700757,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Aerodrome (Base)",
                    "identifier": "aerodrome-base",
                    "has_trading_incentive": False,
                },
                "base": "0X2A06A17CBC6D0032CAC2C6696DA90F29D39A1A29",
                "target": "0X4200000000000000000000000000000000000006",
                "volume": 994.06996708,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (Ethereum)",
                    "identifier": "uniswap_v3",
                    "has_trading_incentive": False,
                },
                "base": "0X25CBB21A9DA7C3C63BB77CCCA5B2E2482AEDB710",
                "target": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "volume": 1287.757953298,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (Ethereum)",
                    "identifier": "uniswap_v3",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0X6B175474E89094C44DA98B954EEDEAC495271D0F",
                "volume": 958.75103621,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (Base)",
                    "identifier": "uniswap-v3-base",
                    "has_trading_incentive": False,
                },
                "base": "0X2A06A17CBC6D0032CAC2C6696DA90F29D39A1A29",
                "target": "0X4200000000000000000000000000000000000006",
                "volume": 620.43494803,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (Ethereum)",
                    "identifier": "uniswap_v3",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0XD43FBA1F38D9B306AEEF9D78AD177D51EF802B46",
                "volume": 477.35001495,
            },
            {
                "trust_score": "red",
                "market": {
                    "name": "Uniswap V3 (Ethereum)",
                    "identifier": "uniswap_v3",
                    "has_trading_incentive": False,
                },
                "base": "0X0000000000C5DC95539589FBD24BE07C6C14ECA4",
                "target": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "volume": 32722.0820046909,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (Ethereum)",
                    "identifier": "uniswap_v3",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0XC32DB1D3282E872D98F6437D3BCFA57801CA6D5C",
                "volume": 160.67212747,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "Mudrex",
                    "identifier": "mudrex",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "USDT",
                "volume": 3942.5804998874128,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (Ethereum)",
                    "identifier": "uniswap_v3",
                    "has_trading_incentive": False,
                },
                "base": "0X72E4F9F808C49A2A61DE9C5896298920DC4EEEA9",
                "target": "0X76E222B07C53D28B89B0BAC18602810FC22B49A8",
                "volume": 255.59523606,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "NovaDAX",
                    "identifier": "novadax",
                    "has_trading_incentive": False,
                },
                "base": "BITCOIN",
                "target": "BRL",
                "volume": 266.44,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "Bit2Me",
                    "identifier": "bit2me",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "EUR",
                "volume": 50.396499999999996,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "Kraken",
                    "identifier": "kraken",
                    "has_trading_incentive": False,
                },
                "base": "HPOS10I",
                "target": "EUR",
                "volume": 2743.87102,
            },
        ],
        "platforms": {
            "ethereum": "0x72e4f9f808c49a2a61de9c5896298920dc4eeea9",
            "berachain": "0x6b26f778bfae56cfb4bf9b62c678d9d40e725227",
            "base": "0x2a06a17cbc6d0032cac2c6696da90f29d39a1a29",
            "solana": "CTgiaZUK12kCcB8sosn4Nt2NZtzLgtPqDwyQyr2syATC",
            "binance-smart-chain": "0xc4044d67585d421495fb0bf08c50b15683647003",
        },
        "logoURI": None,
    }


@fixture
def buffDogecoin() -> dict[str, Any]:
    return {
        "id": "buff-doge-coin",
        "name": "Buff Doge Coin",
        "symbol": "dogecoin",
        "categories": ["BNB Chain Ecosystem"],
        "localization": {"en": "Buff Doge Coin"},
        "description": {
            "en": '"Buff Doge Coin is the Buff version of Dogecoin. Buff Doge Coin was established because of the popularity of Dogecoin with a purpose to be The King of Memes. Buff Doge Coin has several unique characteristics. One of which is hyper deflationary, where each burn will be double its quantity from the previous burn. The coin burning will be very frequent, so it will burn 100% of the remaining supply of the available Buff Doge Coin. \r\n\r\nBurning Scheme of Buff Doge Coin:\r\n#1st Burn : 1,000,000\r\n#2nd Burn : 2,000,000\r\n#3rd Burn : 4,000,000\r\n#4th Burn : 8,000,000\r\n#5th Burn : 16,000,000\r\n#6th  Till the end (Continuing doubling its burn, we will burn trillions of Buff Doge Coin until all the remaining supply is burned).\r\n*more details about Burn are in the whitepaper and website.\r\n\r\nThe Buff Doge Coin protocol, according to the white paper, works in the following way: in each trade, the transaction is taxed with a fee of 10%, which is cut in half. \r\n•\t5% fee = redistributed to all existing holders.\r\n•\t5% fee is split 50/50 half of which is sold by the contract into BNB, while the other half of the Buff Doge Coin are automatically paired with the previously mentioned BNB and added as a liquidity pair on Pancake Swap. \r\nProgress on September 18, 2021, is 4.563 Holders with a market cap of $706.930 and liquidity of $107.838. We have liquidity locked on DXsale to ensure the safety of holders.\r\n\r\nSome percentage of the developer Buff Doge Coin profit will be donated to the animal shelter and environmental issues, such as forest reconstruction to prevent global warming. It is due to the Interconnection of Everything. When we destroy nature, it will also destroy humans and animals as “We Are One”. If we destroy one part, the other part will also get affected. Thus, some of the developer’s profit will be donated to rescue animal shelters and the environment."'
        },
        "links": {"homepage": ["https://www.buffdogecoin.io/"], "whitepaper": None},
        "detail_platforms": {
            "binance_smart_chain": {
                "decimal_place": 9,
                "contract_address": "0x23125108bc4c63e4677b2e253fa498ccb4b3298b",
            }
        },
        "sentiment_votes_up_percentage": None,
        "sentiment_votes_down_percentage": None,
        "watchlist_portfolio_users": 9660,
        "market_cap_rank": None,
        "image": {
            "small": "https://coin-images.coingecko.com/coins/images/18516/small/BUFF_KOIN.png?1696517997"
        },
        "market_data": {
            "mcap_to_tvl_ratio": None,
            "fdv_to_tvl_ratio": None,
            "ath_change_percentage": {"usd": -98.65222},
            "ath_date": {"usd": "2021-11-01T23:27:36.422Z"},
            "atl_change_percentage": {"usd": 779.63853},
            "atl_date": {"usd": "2025-12-05T06:31:32.921Z"},
            "market_cap": {"usd": 0.0},
            "market_cap_rank": None,
            "fully_diluted_valuation": {"usd": 2354353.0},
            "total_volume": {"usd": 43813.0},
            "price_change_percentage_24h": -1.99824,
            "price_change_percentage_7d": 3.73409,
            "price_change_percentage_30d": 10.33864,
            "price_change_percentage_60d": -5.8113,
            "price_change_percentage_200d": 25.20079,
            "price_change_percentage_1y": 7.6836,
            "total_supply": 1000000000000000.0,
            "max_supply": None,
            "circulating_supply": 0.0,
            "total_value_locked": None,
        },
        "developer_data": {"forks": 0, "stars": 0},
        "tickers": [
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X23125108BC4C63E4677B2E253FA498CCB4B3298B",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 119481551690.717,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "LBank",
                    "identifier": "lbank",
                    "has_trading_incentive": False,
                },
                "base": "DOGECOIN",
                "target": "USDT",
                "volume": 10147007550936.0,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BitMart",
                    "identifier": "bitmart",
                    "has_trading_incentive": False,
                },
                "base": "DOGECOIN",
                "target": "USDT",
                "volume": 8337090695626.0,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "KoinBX",
                    "identifier": "koinbazar",
                    "has_trading_incentive": False,
                },
                "base": "DOGECOIN",
                "target": "INR",
                "volume": 6086691086.2,
            },
        ],
        "platforms": {
            "binance-smart-chain": "0x23125108bc4c63e4677b2e253fa498ccb4b3298b"
        },
        "logoURI": None,
    }


@fixture
def polkadot() -> dict[str, Any]:
    return {
        "id": "binance-peg-polkadot",
        "name": "Binance-Peg Polkadot",
        "symbol": "dot",
        "categories": [
            "Crypto-Backed Tokens",
            "BNB Chain Ecosystem",
            "Binance-Peg Tokens",
        ],
        "localization": {"en": "Binance-Peg Polkadot"},
        "description": {
            "en": "Tokens that are wrapped and pegged by Binance on a 1:1 ratio to the corresponding native token. Also supports BEP20 token deposits and withdrawals at Binance.com"
        },
        "links": {"homepage": ["https://polkadot.network/"], "whitepaper": None},
        "detail_platforms": {
            "binance_smart_chain": {
                "decimal_place": 18,
                "contract_address": "0x7083609fce4d1d8dc0c979aab8c869ea2c873402",
            }
        },
        "sentiment_votes_up_percentage": None,
        "sentiment_votes_down_percentage": None,
        "watchlist_portfolio_users": 1158,
        "market_cap_rank": None,
        "image": {
            "small": "https://coin-images.coingecko.com/coins/images/15457/small/-Tj2WF_6_400x400.jpg?1696515104"
        },
        "market_data": {
            "mcap_to_tvl_ratio": None,
            "fdv_to_tvl_ratio": None,
            "ath_change_percentage": {"usd": -96.13363},
            "ath_date": {"usd": "2021-11-04T13:55:25.997Z"},
            "atl_change_percentage": {"usd": 27.72135},
            "atl_date": {"usd": "2025-12-26T00:52:21.342Z"},
            "market_cap": {"usd": 0.0},
            "market_cap_rank": None,
            "fully_diluted_valuation": {"usd": 23296941.0},
            "total_volume": {"usd": 510415.0},
            "price_change_percentage_24h": -4.37618,
            "price_change_percentage_7d": -1.0709,
            "price_change_percentage_30d": 11.03148,
            "price_change_percentage_60d": -22.3947,
            "price_change_percentage_200d": -38.04738,
            "price_change_percentage_1y": -69.50237,
            "total_supply": 10999999.99,
            "max_supply": None,
            "circulating_supply": 0.0,
            "total_value_locked": None,
        },
        "developer_data": {"forks": 0, "stars": 0},
        "tickers": [
            {
                "trust_score": None,
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 10324.8366492776,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 22883.7091211174,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V1 (BSC)",
                    "identifier": "pancakeswap-v1-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 2006.1897177036,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 10861.7764800688,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "ApeSwap",
                    "identifier": "apeswap_bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 667.0240090289,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 4321.6175183995,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 5613.4797514414,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X1FA4A73A3F0133F0025378AF00236F3ABDEE5D63",
                "target": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "volume": 1562.5617956893,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "CoinSwap",
                    "identifier": "coinswap",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 125.8128682931,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 585.0842239647,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XE9E7CEA3DEDCA5984780BAFC599BD69ADD087D56",
                "volume": 508.0845146799,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Mdex BSC",
                    "identifier": "mdex_bsc",
                    "has_trading_incentive": True,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 109.2934395129,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "volume": 102.5630189573,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Mdex BSC",
                    "identifier": "mdex_bsc",
                    "has_trading_incentive": True,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 57.3884078274,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XE3894CB9E92CA78524FB6A30FF072FA5E533C162",
                "target": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "volume": 12881.3586662388,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Nomiswap",
                    "identifier": "nomiswap",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X8AC76A51CC950D9822D68B83FE1AD97B32CD580D",
                "volume": 64.1775460896,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V1 (BSC)",
                    "identifier": "pancakeswap-v1-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0X2170ED0880AC9A755FD29B2688956BD959F933F8",
                "volume": 20.1815499017,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 31833.931335415,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 136353.66853773,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Biswap",
                    "identifier": "biswap",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 1579.9634666963,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 6303.0145753586,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X7083609FCE4D1D8DC0C979AAB8C869EA2C873402",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 16959.6778639584,
            },
        ],
        "platforms": {
            "binance-smart-chain": "0x7083609fce4d1d8dc0c979aab8c869ea2c873402"
        },
        "logoURI": None,
    }


@fixture
def dogecoin() -> dict[str, Any]:
    return {
        "id": "binance-peg-dogecoin",
        "name": "Binance-Peg Dogecoin",
        "symbol": "doge",
        "categories": [
            "BNB Chain Ecosystem",
            "Avalanche Ecosystem",
            "Meme",
            "Binance-Peg Tokens",
        ],
        "localization": {"en": "Binance-Peg Dogecoin"},
        "description": {
            "en": "Tokens that are wrapped and pegged by Binance on a 1:1 ratio to the corresponding native token. Also supports BEP20 token deposits and withdrawals at Binance.com"
        },
        "links": {"homepage": ["http://dogecoin.com/"], "whitepaper": ""},
        "detail_platforms": {
            "binance_smart_chain": {
                "decimal_place": 8,
                "contract_address": "0xba2ae424d960c26247dd6c32edc70b295c744c43",
            }
        },
        "sentiment_votes_up_percentage": None,
        "sentiment_votes_down_percentage": None,
        "watchlist_portfolio_users": 6671,
        "market_cap_rank": 200,
        "image": {
            "small": "https://coin-images.coingecko.com/coins/images/15768/small/dogecoin.png?1696515392"
        },
        "market_data": {
            "mcap_to_tvl_ratio": None,
            "fdv_to_tvl_ratio": None,
            "ath_change_percentage": {"usd": -70.86717},
            "ath_date": {"usd": "2024-12-08T04:37:38.676Z"},
            "atl_change_percentage": {"usd": 182.51744},
            "atl_date": {"usd": "2022-06-18T20:56:27.223Z"},
            "market_cap": {"usd": 359070165.0},
            "market_cap_rank": 200,
            "fully_diluted_valuation": {"usd": 359070165.0},
            "total_volume": {"usd": 3468073.0},
            "price_change_percentage_24h": -5.2262,
            "price_change_percentage_7d": -1.97308,
            "price_change_percentage_30d": 5.64807,
            "price_change_percentage_60d": -9.44643,
            "price_change_percentage_200d": -14.73919,
            "price_change_percentage_1y": -62.24635,
            "total_supply": 2564461048.435581,
            "max_supply": None,
            "circulating_supply": 2564461048.435581,
            "total_value_locked": None,
        },
        "developer_data": {"forks": 0, "stars": 0},
        "tickers": [
            {
                "trust_score": "green",
                "market": {
                    "name": "SquadSwap WOW (BSC)",
                    "identifier": "squadswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 18754630.807037,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 2209128.75820696,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 1486435.42084801,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 403515.19923661,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 280998.59166265,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "THENA V3",
                    "identifier": "thena-v3",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 254091.21375053,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Unchain X",
                    "identifier": "unchain-x",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 89553.14095457,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 93461.06141297,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Biswap",
                    "identifier": "biswap",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 32550.10494587,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Unchain X",
                    "identifier": "unchain-x",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 62122.6915649,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 38035.94901695,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 179029.85029486,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "ApeSwap",
                    "identifier": "apeswap_bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 12764.58998938,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 42714.26044848,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Unchain X",
                    "identifier": "unchain-x",
                    "has_trading_incentive": False,
                },
                "base": "0X570A5D26F7765ECB712C0924E4DE545B89FD43DF",
                "target": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "volume": 26.8108757222,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Mdex BSC",
                    "identifier": "mdex_bsc",
                    "has_trading_incentive": True,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 7967.65908513,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BabySwap",
                    "identifier": "babyswap",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 9110.12398913,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 70997.10985923,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X5F980533B994C93631A639DEDA7892FC49995839",
                "target": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "volume": 351.09797945,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 26065.92902352,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V1 (BSC)",
                    "identifier": "pancakeswap-v1-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XE9E7CEA3DEDCA5984780BAFC599BD69ADD087D56",
                "volume": 5090.55309509,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XE9E7CEA3DEDCA5984780BAFC599BD69ADD087D56",
                "volume": 7793.53887307,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Biswap V3",
                    "identifier": "biswap-v3-1",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 1047.54854871,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XAFCC12E4040615E7AFE9FB4330EB3D9120ACAC05",
                "target": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "volume": 42474.29606036,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X7130D2A12B9BCBFAE4F2634D864A1EE1CE3EAD9C",
                "volume": 8019.75191878,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X0E09FABB73BD3ADE0A17ECC321FD13A19E81CE82",
                "target": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "volume": 430.1974702585,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BabyDogeSwap",
                    "identifier": "babydogeswap",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 1241.99145457,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "SquadSwap Dynamo (BSC)",
                    "identifier": "squadswap-v2-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 984.7541571,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XE550A593D09FBC8DCD557B5C88CEA6946A8B404A",
                "target": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "volume": 41108.60847958,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Unchain X",
                    "identifier": "unchain-x",
                    "has_trading_incentive": False,
                },
                "base": "0X4F0572CA0BF96F5AE17B7062D97CEA3F35BDEA6F",
                "target": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "volume": 56527.0501586087,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Bakeryswap",
                    "identifier": "bakeryswap",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XE02DF9E3E622DEBDD69FB838BB799E3F168902C5",
                "volume": 579.80272533,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V1 (BSC)",
                    "identifier": "pancakeswap-v1-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 485.71435426,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Nomiswap",
                    "identifier": "nomiswap",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 554.1475132,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Bakeryswap",
                    "identifier": "bakeryswap",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 370.61569008,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X8AC76A51CC950D9822D68B83FE1AD97B32CD580D",
                "volume": 376.08003636,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X0E09FABB73BD3ADE0A17ECC321FD13A19E81CE82",
                "volume": 283.47712096,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BabyDogeSwap",
                    "identifier": "babydogeswap",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 98.06228657,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Uniswap V4 (BSC)",
                    "identifier": "uniswap-v4-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 38.95615851,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XFE8BF5B8F5E4EB5F9BC2BE16303F7DAB8CF56AA8",
                "volume": 122.60914796,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "SmarDex (BSC)",
                    "identifier": "smardex-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XFDC66A08B0D0DC44C17BBD471B88F49F50CDD20F",
                "volume": 26.93497122,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X25D887CE7A35172C62FEBFD67A1856F20FAEBB00",
                "target": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "volume": 1285514.75306713,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "Blackhole V3",
                    "identifier": "blackhole-v3",
                    "has_trading_incentive": False,
                },
                "base": "0X846E52D0DD71C2FDC891538B2D37FF84345C7B9F",
                "target": "0XB97EF9EF8734C71904D8002F8B6BC66DD9C48A6E",
                "volume": 957.6250546362,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "Uniswap V3 (BSC)",
                    "identifier": "uniswap-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XCF6BB5389C92BDDA8A3747DDB454CB7A64626C63",
                "volume": 3957.37081315,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X8AC76A51CC950D9822D68B83FE1AD97B32CD580D",
                "volume": 752.015372,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 522.57826524,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XFB5B838B6CFEEDC2873AB27866079AC55363D37E",
                "volume": 83.77764027,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0X641EC142E67AB213539815F67E4276975C2F8D50",
                "target": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "volume": 5588039821.20917,
            },
            {
                "trust_score": "red",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X2859E4544C4BB03966803B044A93563BD2D0DD4D",
                "target": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "volume": 574612.113742331,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X4A68C250486A116DC8D6A0C5B0677DE07CC09C5D",
                "volume": 9.44416707,
            },
            {
                "trust_score": "red",
                "market": {
                    "name": "THENA FUSION",
                    "identifier": "thena-fusion",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 331.21566885,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Blackhole V3",
                    "identifier": "blackhole-v3",
                    "has_trading_incentive": False,
                },
                "base": "0X846E52D0DD71C2FDC891538B2D37FF84345C7B9F",
                "target": "0XCD94A87696FAC69EDAE3A70FE5725307AE1C43F6",
                "volume": 107.3183375789,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "PancakeSwap (v2)",
                    "identifier": "pancakeswap_new",
                    "has_trading_incentive": False,
                },
                "base": "0XBA2AE424D960C26247DD6C32EDC70B295C744C43",
                "target": "0X4A824EE819955A7D769E03FE36F9E0C3BD3AA60B",
                "volume": 105.29591083,
            },
        ],
        "platforms": {
            "binance-smart-chain": "0xba2ae424d960c26247dd6c32edc70b295c744c43",
            "avalanche": "0x846e52d0dd71c2fdc891538b2d37ff84345c7b9f",
        },
        "logoURI": None,
    }


@fixture
def siren() -> dict[str, Any]:
    return {
        "id": "siren-2",
        "name": "Siren",
        "symbol": "siren",
        "categories": [
            "BNB Chain Ecosystem",
            "Meme",
            "Binance Alpha Spotlight",
            "Four.meme Ecosystem (BNB Memes)",
        ],
        "localization": {"en": "Siren"},
        "description": {"en": ""},
        "links": {
            "homepage": [
                "https://sirenai.me/",
                "https://four.meme/token/0x997a58129890bbda032231a52ed1ddc845fc18e1",
            ],
            "whitepaper": "",
        },
        "detail_platforms": {
            "binance_smart_chain": {
                "decimal_place": 18,
                "contract_address": "0x997a58129890bbda032231a52ed1ddc845fc18e1",
            }
        },
        "sentiment_votes_up_percentage": None,
        "sentiment_votes_down_percentage": None,
        "watchlist_portfolio_users": 939,
        "market_cap_rank": 653,
        "image": {
            "small": "https://coin-images.coingecko.com/coins/images/54479/small/siren.png?1739960056"
        },
        "market_data": {
            "mcap_to_tvl_ratio": None,
            "fdv_to_tvl_ratio": None,
            "ath_change_percentage": {"usd": -61.59801},
            "ath_date": {"usd": "2025-05-13T13:50:22.297Z"},
            "atl_change_percentage": {"usd": 179.94655},
            "atl_date": {"usd": "2025-03-11T06:21:52.561Z"},
            "market_cap": {"usd": 53753357.0},
            "market_cap_rank": 653,
            "fully_diluted_valuation": {"usd": 53753357.0},
            "total_volume": {"usd": 6128543.0},
            "price_change_percentage_24h": -7.13758,
            "price_change_percentage_7d": -10.50386,
            "price_change_percentage_30d": 7.47701,
            "price_change_percentage_60d": -1.47375,
            "price_change_percentage_200d": 33.30448,
            "price_change_percentage_1y": 0.0,
            "total_supply": 728879834.9013236,
            "max_supply": 1000000000.0,
            "circulating_supply": 728879834.9013236,
            "total_value_locked": None,
        },
        "developer_data": {"forks": 0, "stars": 0},
        "tickers": [
            {
                "trust_score": "green",
                "market": {
                    "name": "LBank",
                    "identifier": "lbank",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 75748468.91,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X997A58129890BBDA032231A52ED1DDC845FC18E1",
                "target": "0XBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C",
                "volume": 946572.743472019,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "KuCoin",
                    "identifier": "kucoin",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 0.0,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Toobit",
                    "identifier": "toobit",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 554301.59,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Gate",
                    "identifier": "gate",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 516634.21,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "BingX",
                    "identifier": "bingx",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 355362.89,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Biconomy.com",
                    "identifier": "biconomy",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 543750.95,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "Ourbit",
                    "identifier": "ourbit",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 278223.33,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "XT.COM",
                    "identifier": "xt",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 777135.28,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BitKan",
                    "identifier": "bitkan",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 85046.86,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "CoinEx",
                    "identifier": "coinex",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 119952.57638978,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "BVOX",
                    "identifier": "bitvenus_spot",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 338166.03,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "DigiFinex",
                    "identifier": "digifinex",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 32878.9217,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Bitunix",
                    "identifier": "bitunix",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 833649.31,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "HashKey Global",
                    "identifier": "hashkey-global",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 106836.24,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Phemex",
                    "identifier": "phemex",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 148595.821,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "Bitrue",
                    "identifier": "bitrue",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 107730.1395,
            },
            {
                "trust_score": "yellow",
                "market": {
                    "name": "BTSE",
                    "identifier": "btse",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "USDT",
                "volume": 205735.5878034604,
            },
            {
                "trust_score": "green",
                "market": {
                    "name": "PancakeSwap V3 (BSC)",
                    "identifier": "pancakeswap-v3-bsc",
                    "has_trading_incentive": False,
                },
                "base": "0X997A58129890BBDA032231A52ED1DDC845FC18E1",
                "target": "0X55D398326F99059FF775485246999027B3197955",
                "volume": 900025.102519264,
            },
            {
                "trust_score": None,
                "market": {
                    "name": "NovaDAX",
                    "identifier": "novadax",
                    "has_trading_incentive": False,
                },
                "base": "SIREN",
                "target": "BRL",
                "volume": 184.92,
            },
        ],
        "platforms": {
            "binance-smart-chain": "0x997a58129890bbda032231a52ed1ddc845fc18e1"
        },
        "logoURI": None,
    }


@mark.asyncio
async def test_math_asset_trust_scorer_strategy_score_high(
    strategy: MathAssetTrustScorerStrategy,
    bitcoin: dict[str, Any],
):
    validated = GetFromAddressToken.model_validate(bitcoin)

    trust_score = await strategy.score(raw_asset=validated.model_dump())

    assert trust_score >= 70


@mark.asyncio
async def test_math_asset_trust_scorer_strategy_score_medium(
    strategy: MathAssetTrustScorerStrategy,
    harryPotterObamaSonic10Inu: dict[str, Any],
):
    validated = GetFromAddressToken.model_validate(harryPotterObamaSonic10Inu)

    trust_score = await strategy.score(raw_asset=validated.model_dump())

    assert trust_score < 70 and trust_score >= 30


@mark.asyncio
async def test_math_asset_trust_scorer_strategy_score_low(
    strategy: MathAssetTrustScorerStrategy,
    buffDogecoin: dict[str, Any],
):
    validated = GetFromAddressToken.model_validate(buffDogecoin)

    trust_score = await strategy.score(raw_asset=validated.model_dump())

    assert trust_score < 30


@mark.asyncio
async def test_math_asset_trust_scorer_strategy_score_2_high(
    strategy: MathAssetTrustScorerStrategy, polkadot: dict[str, Any]
):
    validated = GetFromAddressToken.model_validate(polkadot)

    trust_score = await strategy.score(raw_asset=validated.model_dump())

    assert trust_score >= 70


@mark.asyncio
async def test_math_asset_trust_scorer_strategy_score_3_high(
    strategy: MathAssetTrustScorerStrategy, dogecoin: dict[str, Any]
):
    validated = GetFromAddressToken.model_validate(dogecoin)

    trust_score = await strategy.score(raw_asset=validated.model_dump())

    assert trust_score >= 70


@mark.asyncio
async def test_math_asset_trust_scorer_strategy_score_2_medium(
    strategy: MathAssetTrustScorerStrategy, siren: dict[str, Any]
):
    validated = GetFromAddressToken.model_validate(siren)

    trust_score = await strategy.score(raw_asset=validated.model_dump())

    assert trust_score < 70 and trust_score >= 30
