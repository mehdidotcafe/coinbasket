import asyncio
from typing import TypedDict, cast
from web3 import AsyncWeb3
from eth_account.signers.local import LocalAccount
from web3.types import Nonce


class Configuration(TypedDict):
    private_key: str


class NonceManager:
    _nonce: Nonce | None = None
    _synced: bool = False
    _lock = asyncio.Lock()

    def __init__(self, w3: AsyncWeb3, configuration: Configuration):
        self.w3 = w3
        self.account: LocalAccount = w3.eth.account.from_key(
            configuration["private_key"]
        )

    async def _sync_nonce(self):
        type(self)._nonce = await self.w3.eth.get_transaction_count(
            self.account.address, "pending"
        )
        type(self)._synced = True

    async def get_and_increment(self):
        async with type(self)._lock:
            if not type(self)._synced:
                await self._sync_nonce()
            nonce = type(self)._nonce
            type(self)._nonce += 1  # type: ignore
            return cast(Nonce, nonce)

    async def resync(self):
        async with type(self)._lock:
            await self._sync_nonce()
