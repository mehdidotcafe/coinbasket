import json
import os
import re
from typing import Any, cast
from api.shared.id_generator.id_generator import IdGenerator
from api.similarity.asset_similarity import AssetSimilarity, TokenSimilarity
from api.ingestion.data_source.data_source import DataSource
from api.protocol.asset_category import AssetCategory


class DevDataSource(DataSource):
    def __init__(
        self,
        id_generator: IdGenerator,
    ):
        self.id_generator = id_generator

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

        return [
            self._map_raw_token_to_token_similarity(raw_token)
            for raw_token in raw_tokens
        ]

    def version(self) -> int:
        return 2

    def _map_raw_token_to_token_similarity(
        self, raw_token: dict[str, Any]
    ) -> TokenSimilarity:
        address = raw_token["platforms"]["binance-smart-chain"]

        return TokenSimilarity(
            address=address,
            id=f"bsc:{address}".lower(),
            name=raw_token["name"],
            display_name=self._clean_display_name(raw_token["name"]),
            ticker=raw_token["symbol"].upper(),
            description=raw_token["description"]["en"],
            decimals=int(
                raw_token["detail_platforms"]["binance-smart-chain"]["decimal_place"]
            ),
            categories=self._make_categories(raw_token.get("categories")),
            logo_uri=raw_token["image"].get("small"),
            is_canonical=self._is_canonical(raw_token),
            market_cap_usd=int(raw_token["market_data"]["market_cap"].get("usd", 0)),
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

    def _is_canonical(self, token: dict[str, Any]) -> int:
        patterns = [
            r"(?i)\b(Binance Pegged|Binance Bridged|Binance-Peg)\b",
        ]

        if token["categories"] and "Binance Bridged" in token["categories"]:
            return 1

        for pattern in patterns:
            if re.search(pattern, token["name"]):
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
