from decimal import Decimal
from api.chain.transaction_receipt_parser import TransactionReceiptParser
from api.chain.chain import ParsedReceipt
from api.protocol.asset import Asset
from api.chain.balance import BalanceAtomic


class TestTransactionReceiptParser(TransactionReceiptParser):
    async def parse_receipt(
        self,
        address: str,
        sell_asset: Asset,
        buy_asset: Asset,
        transaction_hash: str,
    ) -> ParsedReceipt:
        return ParsedReceipt(
            executed_sell_balance=BalanceAtomic(
                asset=sell_asset,
                amount=Decimal("1"),
                amount_atomic=1 * 10**18,
                decimals=1,
            ),
            executed_buy_balance=BalanceAtomic(
                asset=buy_asset,
                amount=Decimal("10"),
                amount_atomic=10 * 10**18,
                decimals=1,
            ),
            rate=Decimal("10"),
        )
