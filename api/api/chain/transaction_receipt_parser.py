from abc import ABC, abstractmethod
from api.protocol.asset import Asset
from api.chain.chain import ParsedReceipt


class TransactionReceiptParser(ABC):
    @abstractmethod
    async def parse_receipt(
        self,
        address: str,
        sell_asset: Asset,
        buy_asset: Asset,
        transaction_hash: str,
    ) -> ParsedReceipt:
        raise NotImplementedError
