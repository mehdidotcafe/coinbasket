import asyncio
import json
import sys

from api.chain.infrastructure.bsc.bsc_transaction_receipt_parser import (
    BscTransactionReceiptParser,
)
from api.ingestion.data_source.data_source import DataSource
from api.ingestion.data_source.infrastructure.bsc.cmc_top_20_basket_data_source import (
    CmcTop20BasketDataSource,
)
from api.ingestion.data_source.infrastructure.bsc.coingecko_live_tokens_data_source import (
    CoingeckoLiveTokenListDataSource,
)
from api.ingestion.data_source.infrastructure.bsc.dev_data_source import DevDataSource
from api.ingestion.data_source.infrastructure.bsc.test_data_source import TestDataSource
from api.ingestion.ingest_data_use_case import IngestDataUseCase
from api.protocol.token import Token
from api.shared.http_request.infrastructure.aiohttp_http_request import (
    AiohttpHttpRequest,
)
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
)
from web3 import AsyncWeb3, AsyncHTTPProvider

from api.configuration import Configuration
from api.chain.infrastructure.bsc.bsc_chain import BscChain
from api.registry import id_generator, similarity_storage, token_repository


configuration = Configuration()
w3 = AsyncWeb3(AsyncHTTPProvider(configuration.bsc_rpc_url))

transaction_receipt_parser = BscTransactionReceiptParser(w3=w3)

chain = BscChain(
    w3=w3,
    transaction_receipt_parser=transaction_receipt_parser,
)


async def get_address_balances():
    address = sys.argv[2]
    balance = await chain.get_address_native_token_balance(address=address)

    print(f"Native token ({chain.base_token.ticker}) Balance: {balance.amount}")

    for arg in sys.argv[3:]:
        balance_amount = await chain.get_address_asset_balance(
            address,
            Token(
                id="bsc:" + arg,
                name="Token",
                display_name="Token",
                ticker="Token",
                address=arg,
                description="",
                decimals=0,
                categories=[],
            ),
        )
        print(f"{arg} Balance: {balance_amount}")


async def make_assets_snapshot():
    http_request = AiohttpHttpRequest()
    coingecko_token_repository = CoingeckoTokenRepository(
        http_request,
        {
            "coingecko_base_url": configuration.coingecko_base_url,
            "coingecko_api_key": configuration.coingecko_api_key,
        },
    )

    print("Fetching all tokens...")
    tokens = await coingecko_token_repository.get_all_tokens()
    print(f"Found {len(tokens)} tokens")

    snapshot = []
    for i, token in enumerate(tokens, 1):
        print(f"Processing token {i}/{len(tokens)}: {token.address}")

        try:
            raw_token = await coingecko_token_repository.get_by_address_raw(
                token.address
            )

            if raw_token:
                snapshot.append(raw_token)
            else:
                print(f"  Warning: No data found for {token.address}")
        except Exception as e:
            print(f"  Error processing {token.address}: {e}")

        await asyncio.sleep(2)

    output_file = "data/dev_data_source_assets.json"
    with open(output_file, "w") as f:
        json.dump(snapshot, f, indent=4)

    print(f"\nSnapshot saved to {output_file}")
    print(f"Total tokens with data: {len(snapshot)}")


async def seed_assets():
    print(f"Seeding assets for environment: {configuration.app_env}")

    similarity_storage.start()

    data_sources: list[DataSource] = []

    match configuration.app_env:
        case "test":
            data_sources = [TestDataSource(id_generator)]
        case "development":
            data_sources = [DevDataSource(id_generator)]
        case _:
            data_sources = [
                CoingeckoLiveTokenListDataSource(
                    id_generator,
                    token_repository,
                ),
                CmcTop20BasketDataSource(
                    id_generator,
                ),
            ]

    ingest_data_use_case = IngestDataUseCase(
        similarity_storage=similarity_storage,
        id_generator=id_generator,
        data_sources=data_sources,
    )

    await ingest_data_use_case.execute()

    print("Assets seeded successfully.")


async def main():
    if sys.argv[1] == "get_address_balances":
        await get_address_balances()
    elif sys.argv[1] == "make_assets_snapshot":
        await make_assets_snapshot()
    elif sys.argv[1] == "seed_assets":
        await seed_assets()
    else:
        print("Invalid command.")


if __name__ == "__main__":
    asyncio.run(main())
