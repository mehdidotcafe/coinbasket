import asyncio
import json
import sys

from api.chain.infrastructure.bsc.bsc_transaction_receipt_parser import (
    BscTransactionReceiptParser,
)
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


async def make_tokens_snapshot():
    http_request = AiohttpHttpRequest()
    token_repository = CoingeckoTokenRepository(
        http_request,
        {
            "coingecko_base_url": configuration.coingecko_base_url,
            "coingecko_api_key": configuration.coingecko_api_key,
        },
    )

    print("Fetching all tokens...")
    tokens = await token_repository.get_all_tokens()
    print(f"Found {len(tokens)} tokens")

    snapshot = []
    for i, token in enumerate(tokens, 1):
        print(f"Processing token {i}/{len(tokens)}: {token.address}")

        try:
            raw_token = await token_repository.get_by_address_raw(token.address)

            print(f"raw_token: {raw_token}")  # Debugging line

            if raw_token:
                snapshot.append(raw_token)
            else:
                print(f"  Warning: No data found for {token.address}")
        except Exception as e:
            print(f"  Error processing {token.address}: {e}")

        await asyncio.sleep(2)

    output_file = "data/dev_data_source_tokens.json"
    with open(output_file, "w") as f:
        json.dump(snapshot, f, indent=4)

    print(f"\nSnapshot saved to {output_file}")
    print(f"Total tokens with data: {len(snapshot)}")


async def main():
    if sys.argv[1] == "get_address_balances":
        await get_address_balances()
    elif sys.argv[1] == "make_tokens_snapshot":
        await make_tokens_snapshot()
    else:
        print("Invalid command.")


if __name__ == "__main__":
    asyncio.run(main())
