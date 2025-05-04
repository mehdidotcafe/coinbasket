from decimal import Decimal
import json
from typing import Any, cast
from eth_typing import ChecksumAddress, HexStr
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder, ExtraDataToPOAMiddleware  # type: ignore
from web3.types import TxParams, Wei

from coinbasket.basket import Token
from coinbasket.chain.balance import Balance
from coinbasket.chain.chain import Chain


class BscChain(Chain):
    def __init__(
        self,
        w3: Web3,
        private_key: str,
        base_token: Token,
    ):
        self.w3 = w3

        self.private_key = private_key
        self.base_token = base_token

        with open(
            "./coinbasket/infrastructure/bsc/chain/erc20_token_abi.json", "r"
        ) as f:
            self.erc20_token_abi = json.load(f)

        self.account: LocalAccount = self.w3.eth.account.from_key(private_key)

        # TODO: Investigate why this is needed
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)  # type: ignore
        self.w3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(self.account),  # type: ignore
            layer=0,
        )

    def get_min_balance(self) -> Balance:
        """Get the minimum balance required for the agent wallet."""
        gas_used = 200_000
        transaction_count = 20

        total_gas = gas_used * transaction_count
        gas_price = self.w3.eth.gas_price
        total_gas_cost = gas_price * total_gas

        return Balance(
            token=self.base_token,
            amount=Decimal(self.w3.from_wei(total_gas_cost, "ether")),
        )

    def get_balance(self) -> Balance:
        """Get the balance of the agent address."""
        print(f"Account: {self.account.address}")

        balance = self.w3.eth.get_balance(self.account.address)
        balance_in_ether = self.w3.from_wei(balance, "ether")
        print(f"Balance: {balance_in_ether} BNB")

        return Balance(
            token=self.base_token,
            amount=Decimal(balance_in_ether),
        )

    def get_token_balance_amount(self, token_address_checksum: str) -> Decimal:
        """Get the balance of a specific token."""
        token_contract = self.w3.eth.contract(
            address=cast(ChecksumAddress, token_address_checksum),
            abi=self.erc20_token_abi,
        )
        balance = token_contract.functions.balanceOf(self.account.address).call()

        return Decimal(self.w3.from_wei(balance, "ether"))

    def get_base_token(self):
        return self.base_token

    def compute_gas_estimate(
        self,
        amount: int,
        # address checksum
        to_address: str,
        encoded_input: HexStr | None = None,
    ) -> int:
        transaction_params: TxParams = {
            "from": self.account.address,
            "to": to_address,
            "value": Wei(amount),
        }

        if encoded_input is not None:
            transaction_params["data"] = encoded_input

        return int(self.w3.eth.estimate_gas(transaction_params) * 1.1)

    def sign_send_wait_transaction(
        self,
        amount: int,
        # address checksum
        to_address: str,
        encoded_input: HexStr | None = None,
    ) -> Any:
        latest_block = self.w3.eth.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas", 0)
        max_priority_fee = self.w3.to_wei(2, "gwei")  # This is the miner "tip"
        max_fee_per_gas = Wei(base_fee * 2 + max_priority_fee)

        gas_estimate = self.compute_gas_estimate(
            encoded_input=encoded_input,
            to_address=to_address,
            amount=amount,
        )

        transaction_params: TxParams = {
            "from": self.account.address,
            "to": to_address,
            "gas": gas_estimate,
            "maxPriorityFeePerGas": max_priority_fee,
            "maxFeePerGas": max_fee_per_gas,
            "chainId": self.w3.eth.chain_id,
            "type": HexStr("0x2"),
            "value": Wei(amount),
            "nonce": self.w3.eth.get_transaction_count(self.account.address, "pending"),
        }
        if encoded_input is not None:
            transaction_params["data"] = encoded_input

        raw_transaction = self.w3.eth.account.sign_transaction(
            transaction_params, self.account.key
        ).raw_transaction
        transaction_hash = self.w3.eth.send_raw_transaction(raw_transaction)
        print(f"Trx Hash: {transaction_hash.hex()}")

        receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        print(f"Receipt: {receipt}")

        return receipt
