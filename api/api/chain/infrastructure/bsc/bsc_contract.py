from decimal import Decimal
import json
from typing import Any
from async_lru import alru_cache
from api.chain.contract import Contract
from web3 import AsyncWeb3


class BscContract(Contract):
    def __init__(self, w3: AsyncWeb3):
        self.w3 = w3

        with open(
            "./api/chain/infrastructure/bsc/erc20_token_abi.json",
            "r",
            encoding="utf-8",
        ) as f:
            self.erc20_token_abi = json.load(f)

    @alru_cache
    async def get_decimals(self, token_address: str) -> Decimal:  # type: ignore
        token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token_address),
            abi=self.erc20_token_abi,
        )

        return Decimal(await token_contract.functions.decimals().call())

    def make_approve_transaction_input(
        self,
        token_address: str,
        spender_address: str,
        amount: Decimal,
    ) -> Any:
        """Generate an approve transaction for the given token."""
        token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token_address),
            abi=self.erc20_token_abi,
        )

        return token_contract.functions.approve(
            self.w3.to_checksum_address(spender_address), int(amount)
        )._encode_transaction_data()  # type: ignore
