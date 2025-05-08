import sys

from protocol.token import Token

from web3 import Web3

from invest_agent.configuration import Configuration
from invest_agent.infrastructure.bsc.chain.bsc_chain import BscChain


configuration = Configuration()
chain = BscChain(
    w3=Web3(Web3.HTTPProvider(configuration.bsc_rpc_url)),
    private_key=configuration.bsc_private_key,
    base_token=Token(
        name=configuration.bsc_base_token_name,
        display_name=configuration.bsc_base_token_display_name,
        ticker=configuration.bsc_base_token_ticker,
        address=configuration.bsc_base_token_address,
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
