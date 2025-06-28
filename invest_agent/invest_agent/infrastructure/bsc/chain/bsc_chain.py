from decimal import Decimal
import json
from typing import Any, TypedDict
from eth_typing import HexStr
from eth_account.signers.local import LocalAccount
from web3 import AsyncWeb3
from web3.middleware import SignAndSendRawMiddlewareBuilder, ExtraDataToPOAMiddleware  # type: ignore
from web3.types import TxParams, Wei

from protocol.token import Token
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain, Gas, TransactionFailure

from async_lru import alru_cache


class Eip1559Gas(TypedDict):
    type: int
    maxFeePerGas: Wei
    maxPriorityFeePerGas: Wei


class BscChain(Chain):
    def __init__(
        self,
        w3: AsyncWeb3,
        private_key: str,
    ):
        self.w3 = w3

        self.private_key = private_key
        self.base_token = Token(
            name="BNB",
            display_name="BNB",
            ticker="BNB",
            address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        )

        with open(
            "./invest_agent/infrastructure/bsc/chain/erc20_token_abi.json", "r"
        ) as f:
            self.erc20_token_abi = json.load(f)

        self.account: LocalAccount = self.w3.eth.account.from_key(private_key)

        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)  # type: ignore
        self.w3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(self.account),  # type: ignore
            layer=0,
        )

    def is_native_token(self, token: Token) -> bool:
        return token.address.lower() == self.base_token.address.lower()

    @alru_cache
    async def get_chain_id(self):  # type: ignore
        """Get the chain ID of the BSC network."""
        return await self.w3.eth._chain_id()  # type: ignore

    def get_address(self) -> str:
        """Get the address of the agent wallet."""
        return self.account.address

    async def get_min_balance(self) -> Balance:
        """Get the minimum balance required for the agent wallet."""
        gas_used = 200_000
        transaction_count = 20

        total_gas = gas_used * transaction_count
        gas_price = await self.w3.eth._gas_price()  # type: ignore
        total_gas_cost = gas_price * total_gas

        return Balance(
            token=self.base_token,
            amount=Decimal(self.w3.from_wei(total_gas_cost, "ether")),
        )

    async def get_balance(self) -> Balance:
        """Get the balance of the agent address."""
        balance = await self.w3.eth.get_balance(self.account.address)
        balance_in_ether = self.w3.from_wei(balance, "ether")

        return Balance(
            token=self.base_token,
            amount=Decimal(balance_in_ether),
        )

    async def get_token_balance_amount(self, token_address: str) -> Decimal:
        """Get the balance of a specific token."""
        token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token_address),
            abi=self.erc20_token_abi,
        )
        balance = await token_contract.functions.balanceOf(self.account.address).call()

        return Decimal(self.w3.from_wei(balance, "ether"))

    async def get_address_balance(self, address: str) -> Balance:
        """Get the balance of the address."""
        balance = await self.w3.eth.get_balance(self.w3.to_checksum_address(address))
        balance_in_ether = self.w3.from_wei(balance, "ether")

        return Balance(
            token=self.base_token,
            amount=Decimal(balance_in_ether),
        )

    async def get_address_token_balance_amount(
        self, address: str, token_address: str
    ) -> Decimal:
        """Get the balance of a specific token."""
        token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token_address),
            abi=self.erc20_token_abi,
        )
        balance = await token_contract.functions.balanceOf(
            self.w3.to_checksum_address(address)
        ).call()

        return Decimal(self.w3.from_wei(balance, "ether"))

    def get_base_token(self):
        return self.base_token

    async def compute_gas_estimate(
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

        gas_estimate = int(await self.w3.eth.estimate_gas(transaction_params) * 1.1)

        return gas_estimate

    async def sign_send_wait_transaction(
        self,
        amount: int,
        gas: Gas | None = None,
        to_address: str | None = None,
        encoded_input: HexStr | None = None,
    ) -> Any:
        transaction_params: TxParams = {
            "from": self.account.address,
            "chainId": await self.get_chain_id(),
            "value": Wei(amount),
            "nonce": await self.w3.eth.get_transaction_count(self.account.address),
        }
        if encoded_input is not None:
            transaction_params["data"] = encoded_input

        if to_address is not None:
            transaction_params["to"] = self.w3.to_checksum_address(to_address)

        if gas is None:
            eip1559Gas = await self.__compute_eip1559_gas_estimate()

            transaction_params["type"] = eip1559Gas["type"]
            transaction_params["maxFeePerGas"] = eip1559Gas["maxFeePerGas"]
            transaction_params["maxPriorityFeePerGas"] = eip1559Gas[
                "maxPriorityFeePerGas"
            ]

        if gas is not None and gas.gas is not None:
            transaction_params["gas"] = gas.gas

        if gas is not None and gas.gas_price is not None:
            transaction_params["gasPrice"] = Wei(gas.gas_price)

        transaction_hash = await self.w3.eth.send_transaction(transaction_params)

        receipt = await self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        print(f"Receipt: {receipt}")

        if receipt["status"] != 1:
            try:
                await self.w3.eth.call(
                    transaction_params,
                    block_identifier=receipt["blockNumber"],
                )
            except Exception as e:
                print(f"Transaction failed: {e}")
                raise TransactionFailure() from e
            print("Transaction failed.")
            raise TransactionFailure()
        return receipt

    async def __compute_eip1559_gas_estimate(self):
        """Compute gas estimate for EIP-1559 transactions."""
        latest_block = await self.w3.eth.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas", 0)
        max_priority_fee = self.w3.to_wei(2, "gwei")  # miner "tip"
        max_fee_per_gas = Wei(base_fee * 2 + max_priority_fee)

        return Eip1559Gas(
            type=2,
            maxFeePerGas=max_fee_per_gas,
            maxPriorityFeePerGas=max_priority_fee,
        )
