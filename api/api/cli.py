import asyncio
import sys

from api.chain.infrastructure.bsc.transaction_receipt_parser import (
    BscTransactionReceiptParser,
)
from api.protocol.token import Token
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
        balance_amount = await chain.get_address_token_balance(
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


async def main():
    if sys.argv[1] == "get_address_balances":
        await get_address_balances()

    else:
        print("Invalid command.")


if __name__ == "__main__":
    asyncio.run(main())
