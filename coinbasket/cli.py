import sys

from web3 import Web3

from coinbasket.basket import Token
from coinbasket.config import Config
from coinbasket.infrastructure.bsc.chain.bsc_chain import BscChain


config = Config()
chain = BscChain(
    w3=Web3(Web3.HTTPProvider(config.bsc_rpc_url)),
    private_key=config.bsc_private_key,
    base_token=Token(
        name=config.bsc_base_token_name,
        display_name=config.bsc_base_token_display_name,
        ticker=config.bsc_base_token_ticker,
        address=config.bsc_base_token_address,
    ),
)


def get_balances():
    balance = chain.get_balance()

    print(
        f"{chain.base_token.address} ({chain.base_token.ticker}) Balance: {balance.amount}"
    )

    for arg in sys.argv[2:]:
        balance_amount = chain.get_token_balance_amount(Web3.to_checksum_address(arg))
        print(f"{arg} Balance: {balance_amount}")


def main():
    if sys.argv[1] == "get-balances":
        get_balances()

    else:
        print("Invalid command.")
