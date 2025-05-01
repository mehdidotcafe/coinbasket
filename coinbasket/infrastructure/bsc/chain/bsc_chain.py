from decimal import Decimal
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder, ExtraDataToPOAMiddleware  # type: ignore

from coinbasket.basket import Token
from coinbasket.chain.balance import Balance
from coinbasket.chain.chain import Chain


class BscChain(Chain):
    def __init__(
        self,
        rpc_url: str,
        private_key: str,
        base_token: Token,
    ):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))

        self.private_key = private_key
        self.base_token = base_token

        self.account = self.web3.eth.account.from_key(private_key)

        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)  # type: ignore
        self.web3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(self.account),  # type: ignore
            layer=0,
        )
        print("Bsc chain initialized")

    def get_min_balance(self) -> Balance:
        """Get the minimum balance required for the agent address."""
        return Balance(token=self.base_token, amount=Decimal("1"))

    def get_balance(self) -> Balance:
        """Get the balance of the agent address."""
        balance = self.web3.eth.get_balance(self.account.address)
        print(f"Balance: {self.web3.from_wei(balance, 'ether')} BNB")

        return Balance(
            token=self.base_token,
            amount=self.web3.from_wei(balance, "ether"),  # type: ignore
        )

    def get_base_token(self):
        return self.base_token

    def send_and_wait_transaction(self) -> str:
        """Send and wait for transaction."""
        # Implement the logic to send a transaction and wait for its confirmation
        print("Sending transaction on BSC chain")
        print(self.account.address)
        return "Transaction sent on BSC chain"
