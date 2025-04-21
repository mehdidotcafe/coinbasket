from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder, ExtraDataToPOAMiddleware

from coinbasket.chain.ichain import IChain


class BscChain(IChain):
    def __init__(self, rpc_url: str, private_key: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        self.account = self.web3.eth.account.from_key(private_key)

        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.web3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(self.account), layer=0
        )
        print("Bsc chain initialized")

    def get_balance(self) -> float:
        """Get the balance of the agent address."""
        balance = self.web3.eth.get_balance(self.account.address)
        print(f"Balance: {self.web3.fromWei(balance, 'ether')} BNB")
        return self.web3.fromWei(balance, "ether")

    def send_and_wait_transaction(self) -> str:
        """Send and wait for transaction."""
        # Implement the logic to send a transaction and wait for its confirmation
        print("Sending transaction on BSC chain")
        print(self.account.address)
        return "Transaction sent on BSC chain"
