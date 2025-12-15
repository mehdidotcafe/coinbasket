from decimal import ROUND_DOWN, Decimal
import json
from typing import TypedDict, cast
from eth_typing import HexStr
from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from api.chain.exception.insufficient_balance import InsufficientBalance
from api.chain.infrastructure.bsc.nonce_manager import NonceManager
from api.chain.infrastructure.bsc.transaction_receipt_parser import (
    BscTransactionReceiptParser,
)
from api.protocol.asset import Asset
from tenacity import retry, stop_after_attempt, wait_fixed
from web3 import AsyncWeb3
from web3.middleware import SignAndSendRawMiddlewareBuilder, ExtraDataToPOAMiddleware  # type: ignore
from web3.types import TxParams, Wei

from api.protocol.token import Token
from api.protocol.fixture.token import bnb_token, wbnb_token
from api.chain.balance import (
    AmountAtomic,
    AmountReadable,
    BalanceAtomic,
)
from api.chain.chain import Chain, Gas, ParsedReceipt

from async_lru import alru_cache


class Eip1559Gas(TypedDict):
    type: int
    maxFeePerGas: Wei
    maxPriorityFeePerGas: Wei


class BscChain(Chain):
    def __init__(
        self,
        w3: AsyncWeb3,
        nonce_manager: NonceManager,
        transaction_receipt_parser: BscTransactionReceiptParser,
        private_key: str,
    ):
        self.w3 = w3
        self.nonce_manager = nonce_manager
        self.transaction_receipt_parser = transaction_receipt_parser
        self.private_key = private_key
        self.base_token = bnb_token
        self.wrapped_base_token = wbnb_token
        with open(
            "./api/chain/infrastructure/bsc/erc20_token_abi.json",
            "r",
            encoding="utf-8",
        ) as f:
            self.erc20_token_abi = json.load(f)

        self.account: LocalAccount = self.w3.eth.account.from_key(private_key)

        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)  # type: ignore
        self.w3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(self.account),  # type: ignore
            layer=0,
        )

    def is_native_token(self, asset: Asset) -> bool:
        return (
            isinstance(asset, Token)
            and asset.address.lower() == self.base_token.address.lower()
        )

    def is_wrapped_native_token(self, asset: Asset) -> bool:
        return (
            isinstance(asset, Token)
            and asset.address.lower() == self.wrapped_base_token.address.lower()
        )

    def __is_native_token_address(self, token_address: str) -> bool:
        return token_address.lower() == self.base_token.address.lower()

    @alru_cache
    async def get_chain_id(self):  # type: ignore
        """Get the chain ID of the BSC network."""
        return await self.w3.eth._chain_id()  # type: ignore

    def get_address(self) -> str:
        """Get the address of the agent wallet."""
        return self.account.address

    async def get_min_balance(self) -> BalanceAtomic[Token]:
        """Get the native token minimum balance required for the agent wallet."""
        gas_used = 200_000
        transaction_count = 20

        total_gas = gas_used * transaction_count
        gas_price = await self.w3.eth._gas_price()  # type: ignore
        total_gas_cost = gas_price * total_gas

        return BalanceAtomic[Token](
            asset=self.base_token,
            amount=Decimal(self.w3.from_wei(total_gas_cost, "ether")),
            amount_atomic=total_gas_cost,
            decimals=18,
        )

    async def get_native_token_balance(self) -> BalanceAtomic[Token]:
        """Get the native token balance of the agent address."""
        amount_atomic = await self.w3.eth.get_balance(self.account.address)
        amount = Decimal(self.w3.from_wei(amount_atomic, "ether"))

        return BalanceAtomic[Token](
            asset=self.base_token,
            amount=amount,
            amount_atomic=amount_atomic,
            decimals=18,
        )

    async def get_native_token_available_balance(self) -> BalanceAtomic[Token]:
        """Get the native token available balance of the agent address."""
        balance = await self.get_native_token_balance()
        min_balance = await self.get_min_balance()

        if balance.amount < min_balance.amount:
            raise InsufficientBalance(
                min_balance=min_balance,
            )

        return BalanceAtomic[Token](
            asset=self.base_token,
            amount=balance.amount - min_balance.amount,
            amount_atomic=balance.amount_atomic - min_balance.amount_atomic,
            decimals=18,
        )

    async def get_token_balance(self, token: Token) -> BalanceAtomic[Token]:
        """Get the balance of a specific token."""
        if self.is_native_token(token):
            return await self.get_native_token_balance()

        token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token.address),
            abi=self.erc20_token_abi,
        )
        amount_atomic = await token_contract.functions.balanceOf(
            self.account.address
        ).call()

        amount, decimals = await self.convert_amount_atomic_to_amount(
            token=token, amount_atomic=amount_atomic
        )

        return BalanceAtomic[Token](
            asset=token, amount=amount, amount_atomic=amount_atomic, decimals=decimals
        )

    async def get_address_native_token_balance(
        self, address: str
    ) -> BalanceAtomic[Token]:
        """Get the native token balance of the address."""
        amount_atomic = await self.w3.eth.get_balance(
            self.w3.to_checksum_address(address)
        )

        return BalanceAtomic[Token](
            asset=self.base_token,
            amount=Decimal(self.w3.from_wei(amount_atomic, "ether")),
            amount_atomic=amount_atomic,
            decimals=18,
        )

    async def get_address_token_balance(
        self, address: str, token: Token
    ) -> BalanceAtomic[Token]:
        """Get the balance of a specific token."""
        token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token.address),
            abi=self.erc20_token_abi,
        )
        amount_atomic = await token_contract.functions.balanceOf(
            self.w3.to_checksum_address(address)
        ).call()
        amount, decimals = await self.convert_amount_atomic_to_amount(
            token=token, amount_atomic=amount_atomic
        )

        return BalanceAtomic[Token](
            asset=token, amount=amount, amount_atomic=amount_atomic, decimals=decimals
        )

    def get_base_token(self):
        return self.base_token

    def get_wrapped_base_token(self):
        return self.wrapped_base_token

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(5),
        reraise=True,
    )
    async def sign_send_transaction(
        self,
        amount: int,
        gas: Gas | None = None,
        to_address: str | None = None,
        encoded_input: HexStr | None = None,
    ) -> str:
        nonce = await self.nonce_manager.get_and_increment()

        print(f"Nonce: {nonce}")

        transaction_params: TxParams = {
            "from": self.account.address,
            "chainId": await self.get_chain_id(),
            "value": Wei(amount),
            "nonce": nonce,
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

        try:
            transaction_hash = await self.w3.eth.send_transaction(transaction_params)

            return transaction_hash.to_0x_hex()
        except Exception as e:
            error_message = str(e).lower()

            if "nonce too low" in error_message or "already used" in error_message:
                await self.nonce_manager.resync()
                raise e
            raise e

    async def wait_transaction(
        self,
        transaction_hash: str,
    ) -> bool:
        try:
            receipt = await self.w3.eth.wait_for_transaction_receipt(
                HexBytes(transaction_hash),
                timeout=1200,
            )

            if receipt["status"] == 0:
                print(
                    f"Transaction failed: {transaction_hash} {await self.__simulate_transaction(transaction_hash, receipt['blockNumber'])}"
                )

            print(f"Receipt: {receipt}")

            return receipt["status"] == 1
        except Exception as e:
            print(f"Error waiting for transaction {transaction_hash}: {e}")
            return False

    async def parse_transaction_receipt(
        self, sell_token: Token, buy_token: Token, transaction_hash: str
    ) -> ParsedReceipt:
        receipt = await self.w3.eth.get_transaction_receipt(HexBytes(transaction_hash))

        return await self.transaction_receipt_parser.parse_receipt(
            address=self.account.address,
            sell_token=sell_token,
            buy_token=buy_token,
            receipt=receipt,
        )

    async def convert_amount_to_amount_atomic(
        self, token: Token, amount_readable: AmountReadable
    ) -> tuple[AmountAtomic, int]:
        decimals = await self.get_token_decimals(token.address)

        return int(
            (Decimal(amount_readable) * Decimal(10**decimals)).to_integral_exact(
                rounding=ROUND_DOWN
            )
        ), decimals

    async def convert_amount_atomic_to_amount(
        self, token: Token, amount_atomic: AmountAtomic
    ) -> tuple[AmountReadable, int]:
        decimals = await self.get_token_decimals(token.address)

        return amount_atomic / Decimal(10**decimals), decimals

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

    async def __simulate_transaction(self, transaction_hash: str, block_number: int):
        tx = await self.w3.eth.get_transaction(cast(HexBytes, transaction_hash))

        tx_params_2: TxParams = {}

        if "from" in tx:
            tx_params_2["from"] = tx["from"]
        if "chainId" in tx:
            tx_params_2["chainId"] = tx["chainId"]
        if "to" in tx:
            tx_params_2["to"] = tx["to"]
        if "input" in tx:
            tx_params_2["data"] = tx["input"]
        if "value" in tx:
            tx_params_2["value"] = tx["value"]
        if "gas" in tx:
            tx_params_2["gas"] = tx["gas"]
        if "gasPrice" in tx:
            tx_params_2["gasPrice"] = tx["gasPrice"]

        try:
            await self.w3.eth.call(tx_params_2, block_identifier=block_number)
        except Exception as e:
            return str(e)

        return None

    @alru_cache
    async def get_token_decimals(self, token_address: str) -> int:  # type: ignore
        token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token_address),
            abi=self.erc20_token_abi,
        )

        try:
            return (
                await token_contract.functions.decimals().call()
                if not self.__is_native_token_address(token_address)
                else 18
            )
        except Exception as e:
            print(f"Error getting decimals for {token_address}: {e}")
            return 18
