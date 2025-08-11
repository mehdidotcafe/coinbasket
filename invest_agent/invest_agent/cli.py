import asyncio
import sys

from invest_agent.infrastructure.bsc.chain.nonce_manager import (
    NonceManager,
    Configuration as ConfigurationNM,
)
from protocol.token import Token
from web3 import AsyncWeb3, AsyncHTTPProvider

from invest_agent.configuration import Configuration
from invest_agent.infrastructure.bsc.chain.bsc_chain import BscChain


configuration = Configuration()
w3 = AsyncWeb3(AsyncHTTPProvider(configuration.bsc_rpc_url))
nonce_manager = NonceManager(
    w3=w3,
    configuration=ConfigurationNM(
        private_key=configuration.bsc_private_key,
    ),
)
chain = BscChain(
    w3=w3,
    nonce_manager=nonce_manager,
    private_key=configuration.bsc_private_key,
)


async def get_balances():
    balance = await chain.get_native_token_balance()

    print(f"Address: {chain.get_address()}")
    print(f"Native token ({chain.base_token.ticker}) Balance: {balance.amount}")

    for arg in sys.argv[2:]:
        balance_amount = await chain.get_token_balance(
            Token(
                id="bsc:" + arg,
                name="Token",
                display_name="Token",
                ticker="Token",
                address=arg,
            )
        )
        print(f"{arg} Balance: {balance_amount}")


async def get_address_balances():
    address = sys.argv[2]
    balance = await chain.get_address_native_token_balance(address=sys.argv[2])

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
            ),
        )
        print(f"{arg} Balance: {balance_amount}")


async def main():
    if sys.argv[1] == "get_balances":
        await get_balances()

    elif sys.argv[1] == "get_address_balances":
        await get_address_balances()

    else:
        print("Invalid command.")


if __name__ == "__main__":
    asyncio.run(main())
