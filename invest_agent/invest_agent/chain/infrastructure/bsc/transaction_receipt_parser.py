from decimal import Decimal
import json

from invest_agent.chain.balance import BalanceAtomic
from invest_agent.chain.chain import ParsedReceipt
from protocol.token import Token
from web3 import AsyncWeb3
from typing import Optional

from hexbytes import HexBytes
from web3.types import LogReceipt, TxReceipt

WBNB_ADDRESS = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"


def keccak(text: str) -> str:
    return AsyncWeb3.keccak(text=text).hex()


TRANSFER_TOPIC = keccak("Transfer(address,address,uint256)")
DEPOSIT_TOPIC = keccak("Deposit(address,uint256)")  # WETH9/WBNB
WITHDRAWAL_TOPIC = keccak("Withdrawal(address,uint256)")  # WETH9/WBNB


class BscTransactionReceiptParser:
    def __init__(self, w3: AsyncWeb3):
        self.w3 = w3

        with open(
            "./invest_agent/chain/infrastructure/bsc/erc20_token_abi.json",
            "r",
            encoding="utf-8",
        ) as f:
            self.erc20_token_abi = json.load(f)

    async def parse_receipt(
        self,
        address: str,
        sell_token: Token,
        buy_token: Token,
        receipt: TxReceipt,
    ) -> ParsedReceipt:
        """
        Returns (sold_exact, bought_exact, rate).
        - Units: base units (wei for BNB; smallest unit for ERC-20s).
        - 'rate' is (bought_human / sold_human) as Decimal, or None if either side is zero.

        Works correctly even with multiple txs in the same block because it uses *only this tx's logs*.
        """
        logs: list[LogReceipt] = receipt.get("logs", []) or []

        user_lc = self._norm(address)
        sold_is_native = self._is_native(sell_token.address)
        bought_is_native = self._is_native(buy_token.address)
        sold_token_lc = None if sold_is_native else self._norm(sell_token.address)
        bought_token_lc = None if bought_is_native else self._norm(buy_token.address)
        wrapped_set = {self._norm(a) for a in [WBNB_ADDRESS]}
        # Accumulators
        sold_exact_erc20 = 0
        bought_exact_erc20 = 0
        native_wrapped_in = 0  # sum of WBNB Deposits (BNB spent)
        native_unwrapped = 0  # sum of WBNB Withdrawals (BNB delivered)

        for log in logs:
            addr_lc = self._norm(log["address"])
            topic0 = HexBytes(log["topics"][0]).hex().lower()

            # ERC-20 Transfers for user-edge amounts
            if topic0 == TRANSFER_TOPIC:
                token_addr_lc = addr_lc
                from_addr = self._addr_from_topic(log["topics"][1]).lower()
                to_addr = self._addr_from_topic(log["topics"][2]).lower()
                value = self._u256(log["data"])

                if (
                    sold_token_lc
                    and token_addr_lc == sold_token_lc
                    and from_addr == user_lc
                ):
                    sold_exact_erc20 += value
                if (
                    bought_token_lc
                    and token_addr_lc == bought_token_lc
                    and to_addr == user_lc
                ):
                    bought_exact_erc20 += value
                continue

            # WBNB wrap/unwrap for native attribution (per-tx, safe with many txs in same block)
            if addr_lc in wrapped_set:
                if topic0 == DEPOSIT_TOPIC:
                    native_wrapped_in += self._u256(log["data"])  # actual BNB consumed
                elif topic0 == WITHDRAWAL_TOPIC:
                    native_unwrapped += self._u256(log["data"])  # actual BNB delivered

        # Combine sides
        sold_exact = native_wrapped_in if sold_is_native else sold_exact_erc20
        bought_exact = native_unwrapped if bought_is_native else bought_exact_erc20

        s_dec = 0
        b_dec = 0
        sold_h = Decimal("0")
        bought_h = Decimal("0")

        # Rate in human units
        if sold_exact > 0 and bought_exact > 0:
            s_dec = await self._decimals(sell_token.address)
            b_dec = await self._decimals(buy_token.address)
            sold_h = Decimal(sold_exact) / (Decimal(10) ** s_dec)
            bought_h = Decimal(bought_exact) / (Decimal(10) ** b_dec)
            rate = (bought_h / sold_h) if sold_h != 0 else None
        else:
            rate = None

        return ParsedReceipt(
            executed_sell_balance=BalanceAtomic[Token](
                amount=sold_h,
                amount_atomic=sold_exact,
                asset=sell_token,
                decimals=s_dec,
            ),
            executed_buy_balance=BalanceAtomic[Token](
                amount=bought_h,
                amount_atomic=bought_exact,
                asset=buy_token,
                decimals=b_dec,
            ),
            rate=rate,
        )

    def _addr_from_topic(self, t: HexBytes | str) -> str:
        b = HexBytes(t)
        return "0x" + b.hex()[-40:]

    async def _decimals(self, token: str) -> int:
        if self._is_native(token):
            return 18
        c = self.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(token), abi=self.erc20_token_abi
        )
        # In odd cases (broken tokens), default to 18
        try:
            return int(await c.functions.decimals().call())
        except Exception:
            return 18

    def _is_native(self, x: Optional[str]) -> bool:
        return (x is None) or (
            x.lower() == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        )

    def _norm(self, addr: str) -> str:
        return AsyncWeb3.to_checksum_address(addr).lower()

    def _u256(self, data: HexBytes | str) -> int:
        return int(HexBytes(data).hex(), 16)
