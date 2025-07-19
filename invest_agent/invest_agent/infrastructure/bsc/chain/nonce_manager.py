import asyncio
from typing import TypedDict, cast
from web3 import AsyncWeb3
from eth_account.signers.local import LocalAccount
from web3.types import Nonce


class Configuration(TypedDict):
    private_key: str


class NonceManager:
    def __init__(self, w3: AsyncWeb3, configuration: Configuration):
        self.w3 = w3
        self.account: LocalAccount = w3.eth.account.from_key(
            configuration["private_key"]
        )
        self.lock = asyncio.Lock()
        self._synced = False
        self.nonce: Nonce | None = None

    async def _sync_nonce(self):
        self.nonce = await self.w3.eth.get_transaction_count(
            self.account.address, "pending"
        )
        self._synced = True

    async def get_and_increment(self):
        async with self.lock:
            if not self._synced:
                await self._sync_nonce()
            nonce = self.nonce
            self.nonce += 1  # type: ignore
            return cast(Nonce, nonce)

    async def resync(self):
        async with self.lock:
            await self._sync_nonce()
