# @author: Claude Code
from typing import Any
from api.similarity.trust_scorer.asset_trust_scorer_strategy import (
    AssetTrustScorerStrategy,
)


class MathAssetTrustScorerStrategy(AssetTrustScorerStrategy):
    # Major centralized exchanges that indicate higher trust
    MAJOR_EXCHANGES = {
        "binance",
        "coinbase",
        "kraken",
        "okx",
        "bybit_spot",
        "gate",
        "kucoin",
        "mxc",  # MEXC
        "hotcoin_global",
    }

    # Major DEXes with good reputation
    MAJOR_DEXES = {
        "pancakeswap-v3-bsc",
        "pancakeswap-new",
        "uniswap-bsc",
        "uniswap_v3",
        "uniswap-v4-bsc",
        "uniswap-bsc",
        "thena-v3",
        "thena-fusion",
        "pancakeswap-infinity-clmm",
    }

    async def score(self, raw_asset: dict[str, Any]) -> int:
        score = 0.0

        # --- Binance-Peg ID bonus (15 points) ---
        asset_id = raw_asset.get("id", "")
        if asset_id.startswith("binance-"):
            score += 15

        # --- Description (up to 10 points) ---
        description = raw_asset.get("description", {}).get("en", "")
        if description:
            if len(description) > 200:
                score += 10
            elif len(description) > 50:
                score += 5

        # --- Categories (up to 5 points, penalty for meme) ---
        categories = raw_asset.get("categories", [])
        if len(categories) >= 3:
            score += 5
        elif len(categories) >= 1:
            score += 2

        # Penalty for meme tokens (cumulative)
        meme_categories = {"Meme", "4chan-Themed"}
        meme_count = sum(1 for cat in categories if cat in meme_categories)
        score -= meme_count * 11

        # Bonus for wrapped/pegged tokens (generally trustworthy)
        trusted_categories = {
            "Crypto-Backed Tokens",
            "Wrapped Tokens",
            "Binance-Peg",
            "Bridged USDT",
            "Binance-Peg Tokens",
        }
        if any(cat in trusted_categories for cat in categories):
            score += 16

        # --- Links/Documentation (up to 10 points) ---
        links = raw_asset.get("links", {})
        homepage = links.get("homepage", [])
        whitepaper = links.get("whitepaper")

        if homepage and any(h for h in homepage if h):
            score += 5
        if whitepaper:
            score += 5

        # --- Market Cap & Rank (up to 20 points) ---
        market_data = raw_asset.get("market_data", {})
        market_cap = market_data.get("market_cap", {}).get("usd", 0) or 0
        market_cap_rank = raw_asset.get("market_cap_rank")

        # Market cap scoring (if not 0)
        if market_cap > 0:
            if market_cap >= 1_000_000_000:  # $1B+
                score += 15
            elif market_cap >= 100_000_000:  # $100M+
                score += 12
            elif market_cap >= 10_000_000:  # $10M+
                score += 8
            elif market_cap >= 1_000_000:  # $1M+
                score += 4

        # Market cap rank bonus
        if market_cap_rank is not None:
            if market_cap_rank <= 100:
                score += 5
            elif market_cap_rank <= 500:
                score += 3
            elif market_cap_rank <= 1000:
                score += 2

        # --- Trading Volume (up to 10 points) ---
        total_volume = market_data.get("total_volume", {}).get("usd", 0) or 0
        if total_volume >= 10_000_000:  # $10M+
            score += 10
        elif total_volume >= 1_000_000:  # $1M+
            score += 7
        elif total_volume >= 100_000:  # $100K+
            score += 4
        elif total_volume >= 10_000:  # $10K+
            score += 2

        # --- Tickers / Exchange Listings (up to 25 points) ---
        tickers = raw_asset.get("tickers", [])

        green_tickers = 0
        yellow_tickers = 0
        major_exchange_listings = 0
        major_dex_listings = 0
        unique_markets: set[str] = set()

        for ticker in tickers:
            trust = ticker.get("trust_score")
            market = ticker.get("market", {})
            identifier = market.get("identifier", "")

            unique_markets.add(identifier)

            if trust == "green":
                green_tickers += 1
            elif trust == "yellow":
                yellow_tickers += 1

            if identifier in self.MAJOR_EXCHANGES:
                major_exchange_listings += 1
            if identifier in self.MAJOR_DEXES:
                major_dex_listings += 1

        # Green ticker ratio scoring
        total_tickers = green_tickers + yellow_tickers
        if total_tickers > 0:
            green_ratio = green_tickers / total_tickers
            if green_ratio >= 0.7:
                score += 10
            elif green_ratio >= 0.5:
                score += 5
            elif green_ratio >= 0.3:
                score += 2
            # Penalty for having no green tickers at all
            if green_tickers == 0:
                score -= 10

        # Bonus for having many green tickers (absolute count)
        if green_tickers >= 20:
            score += 10
        elif green_tickers >= 10:
            score += 5
        elif green_tickers >= 5:
            score += 2

        # Number of unique markets
        num_markets = len(unique_markets)
        if num_markets >= 20:
            score += 15
        elif num_markets >= 15:
            score += 12
        elif num_markets >= 10:
            score += 8
        elif num_markets >= 5:
            score += 4
        elif num_markets >= 2:
            score += 2

        # Major exchange listings
        if major_exchange_listings >= 3:
            score += 7
        elif major_exchange_listings >= 1:
            score += 4

        # Major DEX listings (stronger bonus for DEX presence)
        # Multiple tickers on major DEXes indicates good liquidity
        if major_dex_listings >= 10:
            score += 20
        elif major_dex_listings >= 5:
            score += 15
        elif major_dex_listings >= 3:
            score += 10
        elif major_dex_listings >= 1:
            score += 5

        # --- Watchlist Users (up to 5 points) ---
        watchlist_users = raw_asset.get("watchlist_portfolio_users", 0) or 0
        if watchlist_users >= 10000:
            score += 5
        elif watchlist_users >= 5000:
            score += 3
        elif watchlist_users >= 1000:
            score += 2

        # --- FDV (Fully Diluted Valuation) as backup for market cap (up to 15 points) ---
        fdv = market_data.get("fully_diluted_valuation", {}).get("usd", 0) or 0
        if market_cap == 0 and fdv > 0:
            if fdv >= 1_000_000_000:  # $1B+
                score += 15
            elif fdv >= 100_000_000:  # $100M+
                score += 10
            elif fdv >= 10_000_000:  # $10M+
                score += 5
            elif fdv >= 1_000_000:  # $1M+
                score += 2

        # --- ATH Change Percentage (mild penalty for extreme drops) ---
        # Note: Many legitimate tokens drop significantly in bear markets,
        # so this penalty is kept mild
        ath_change = market_data.get("ath_change_percentage", {}).get("usd", 0) or 0
        if ath_change < -99:  # Lost more than 99% from ATH (likely rug/dead)
            score -= 10
        elif ath_change < -98:  # Lost more than 98% from ATH
            score -= 5

        # Clamp score between 0 and 100
        return max(0, min(100, int(score)))
