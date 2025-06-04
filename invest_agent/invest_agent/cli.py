import sys

from web3 import Web3

from invest_agent.configuration import Configuration
from invest_agent.infrastructure.bsc.chain.bsc_chain import BscChain


configuration = Configuration()
chain = BscChain(
    w3=Web3(Web3.HTTPProvider(configuration.bsc_rpc_url)),
    private_key=configuration.bsc_private_key,
)


def get_balances():
    balance = chain.get_balance()

    print(f"Native token ({chain.base_token.ticker}) Balance: {balance.amount}")

    for arg in sys.argv[2:]:
        balance_amount = chain.get_token_balance_amount(arg)
        print(f"{arg} Balance: {balance_amount}")


def get_address_balances():
    address = sys.argv[2]
    balance = chain.get_address_balance(address=sys.argv[2])

    print(f"Native token ({chain.base_token.ticker}) Balance: {balance.amount}")

    for arg in sys.argv[3:]:
        balance_amount = chain.get_address_token_balance_amount(address, arg)
        print(f"{arg} Balance: {balance_amount}")


def main():
    if sys.argv[1] == "get_balances":
        get_balances()

    elif sys.argv[1] == "get_address_balances":
        get_address_balances()

    else:
        print("Invalid command.")


if __name__ == "__main__":
    main()
