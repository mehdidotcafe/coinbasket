import asyncio
import json
import os
import re
from typing import Any, cast
from api.shared.id_generator.id_generator import IdGenerator
from api.similarity.asset_similarity import AssetSimilarity, TokenSimilarity
from api.ingestion.data_source.data_source import DataSource
from api.protocol.asset_category import AssetCategory
from api.similarity.trust_scorer.asset_trust_scorer_strategy import (
    AssetTrustScorerStrategy,
)
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    GetFromAddressToken,
)


class DevDataSource(DataSource):
    blacklist_tokens = [
        # CMC20 basket
        "0x2f8a339b5889ffac4c5a956787cda593b3c36867",
        # "Wrapped BNB"
        "0x0555e30da8f98308edb960aa94c0db47230d2b9c",
    ]

    def __init__(
        self,
        id_generator: IdGenerator,
        asset_trust_scorer_strategy: AssetTrustScorerStrategy,
    ):
        self.id_generator = id_generator
        self.asset_trust_scorer_strategy = asset_trust_scorer_strategy

    async def get(self) -> list[AssetSimilarity]:
        file_path = "data/dev_data_source_assets.json"
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                "run make_assets_snapshot command to generate dev assets snapshot"
            )

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:
            raw_tokens = json.load(f)

        raw_tokens = [
            token
            for token in raw_tokens
            if token["platforms"]["binance-smart-chain"] not in self.blacklist_tokens
        ]

        tokens: list[AssetSimilarity] = []

        batch_size = 50

        batched_tokens = [
            raw_tokens[i : i + batch_size]
            for i in range(0, len(raw_tokens), batch_size)
        ]

        i = 0
        for raw_token_batch in batched_tokens:
            try:
                batch_tokens = await asyncio.gather(
                    *[
                        self._score_and_map_token(raw_token)
                        for raw_token in raw_token_batch
                    ]
                )
                tokens.extend(batch_tokens)
                print(f"Processing token batch {i}/{len(batched_tokens)}")
                i += 1
            except Exception as e:
                print(f"  Error processing token batch {i}: {e}")
                await asyncio.sleep(1)
        return tokens

    def version(self) -> int:
        return 6

    async def _score_and_map_token(self, raw_token: dict[str, Any]) -> TokenSimilarity:
        validated_token = GetFromAddressToken.model_validate(raw_token)

        trust_score = await self.asset_trust_scorer_strategy.score(
            validated_token.model_dump()
        )
        token_similarity = self._map_validated_token_to_token_similarity(
            validated_token, trust_score
        )

        return token_similarity

    def _map_validated_token_to_token_similarity(
        self, token: GetFromAddressToken, trust_score: int
    ) -> TokenSimilarity:
        address = token.platforms["binance-smart-chain"] if token.platforms else ""

        return TokenSimilarity(
            address=address.lower(),
            id=f"bsc:{address}".lower(),
            name=token.name,
            display_name=self._clean_display_name(token.name),
            ticker=token.symbol.upper(),
            description=token.description.en if token.description else "",
            decimals=token.detail_platforms.binance_smart_chain.decimal_place,
            categories=self._make_categories(token.categories),
            logo_uri=f"https://token-registry.s3.amazonaws.com/icons/tokens/bsc/64/{address}.png",
            is_canonical=self._is_canonical_from_token(token),
            market_cap_usd=int(token.market_data.market_cap.usd or 0)
            if token.market_data.market_cap
            else 0,
            trust_score=trust_score,
        )

    def _make_categories(self, categories: list[str] | None) -> list[str]:
        categories = [cast(AssetCategory, category) for category in categories or []]

        if "Storage" in categories:
            categories.append("DePIN")

        if next(
            (
                category
                for category in categories
                if re.search(r"(?i)\b(Stablecoin)\b", category)
                and category != "Stablecoins"
            ),
            None,
        ):
            categories.append("Stablecoins")

        return list(set(categories))

    def _is_canonical_from_token(self, token: GetFromAddressToken) -> int:
        patterns = [
            r"(?i)\b(Binance Pegged|Binance Bridged|Binance-Peg)\b",
        ]
        if token.id.startswith("binance-"):
            return 1

        if token.categories and "Binance Bridged" in token.categories:
            return 1

        for pattern in patterns:
            if re.search(pattern, token.name):
                return 1
        return 0

    def _clean_display_name(self, name: str) -> str:
        display_name = re.sub(
            r"(?i)(\b(Binance Pegged|Wrapped|Binance Bridged|Binance-Peg)\b|\(BNB Smart Chain\))",
            "",
            name,
        ).strip()
        display_name = re.sub(r"\s+", " ", display_name)
        return display_name
