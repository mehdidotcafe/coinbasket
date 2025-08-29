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
        logs: list[LogReceipt] = receipt.get("logs", [])

        user_lc = self._norm(address)
        sold_is_native = self._is_native(sell_token.address)
        bought_is_native = self._is_native(buy_token.address)
        sold_token_lc = None if sold_is_native else self._norm(sell_token.address)  # type: ignore[arg-type]
        bought_token_lc = None if bought_is_native else self._norm(buy_token.address)  # type: ignore[arg-type]
        wrapped_set = {self._norm(a) for a in [WBNB_ADDRESS]}

        # Accumulators
        # ERC-20 edges at the user:
        user_transfers_in: dict[str, int] = {}  # token -> amount received by user
        user_transfers_out: dict[str, int] = {}  # token -> amount sent by user

        # Wrapper signals (per-tx, safe even with many txs in the same block):
        deposit_total = 0  # total native wrapped into *this* wrapper across the tx
        deposit_to_user = 0  # native wrapped where dst == user
        withdrawal_total = 0  # total native unwrapped from wrapper in this tx
        withdrawal_from_user = 0  # unwrapped where src == user

        for log in logs:
            addr_lc = self._norm(log["address"])
            topic0 = HexBytes(log["topics"][0]).hex().lower()

            # ERC-20 Transfers (catch fee-on-transfer and multi-hop by looking ONLY at the user edge)
            if topic0 == TRANSFER_TOPIC:
                token_addr = addr_lc
                from_addr = self._addr_from_topic(log["topics"][1]).lower()
                to_addr = self._addr_from_topic(log["topics"][2]).lower()
                value = self._u256(log["data"])

                if to_addr == user_lc:
                    user_transfers_in[token_addr] = (
                        user_transfers_in.get(token_addr, 0) + value
                    )
                if from_addr == user_lc:
                    user_transfers_out[token_addr] = (
                        user_transfers_out.get(token_addr, 0) + value
                    )
                continue

            # WBNB/WETH9 style wrappers for native (BNB) accounting
            if addr_lc in wrapped_set:
                # Deposit(address indexed dst, uint wad)
                if topic0 == DEPOSIT_TOPIC:
                    wad = self._u256(log["data"])
                    deposit_total += wad
                    dst = self._addr_from_topic(log["topics"][1]).lower()
                    if dst == user_lc:
                        deposit_to_user += wad

                # Withdrawal(address indexed src, uint wad)
                elif topic0 == WITHDRAWAL_TOPIC:
                    wad = self._u256(log["data"])
                    withdrawal_total += wad
                    src = self._addr_from_topic(log["topics"][1]).lower()
                    if src == user_lc:
                        withdrawal_from_user += wad

        # ---- Resolve executed amounts per side ----
        sold_exact = 0
        bought_exact = 0

        # --- Cases for sold side ---
        if sold_is_native:
            # Prefer the exact amount that was actually wrapped (BNB->WBNB) inside this tx.
            # This works for direct wrap and aggregator paths.
            sold_exact = deposit_total
        else:
            # ERC-20 sold: how much the user actually sent out of their wallet.
            sold_exact = (
                user_transfers_out.get(sold_token_lc, 0) if sold_token_lc else 0
            )

        # --- Cases for bought side ---
        if bought_is_native:
            # Prefer total native created by unwrapping in this tx.
            # Normally aggregators unwrap exactly what they will send to the user.
            bought_exact = withdrawal_total
        else:
            # ERC-20 bought: how much the user actually received.
            bought_exact = (
                user_transfers_in.get(bought_token_lc, 0) if bought_token_lc else 0
            )

            # --- SPECIAL CASE: native -> wrapper (e.g., BNB -> WBNB) "pure wrap"
            # If we see no ERC-20 Transfer into the user (some wrappers can be quirky),
            # fall back to Deposit minted directly to the user.
            if (
                bought_exact == 0
                and bought_token_lc in wrapped_set
                and deposit_to_user > 0
            ):
                bought_exact = deposit_to_user

        # Additionally, handle "pure unwrap" (WBNB -> BNB) oddity:
        # If user initiated a withdraw, we should at least see either:
        # - ERC20 Transfer out from user (to 0x0) OR
        # - Withdrawal from user
        if sold_exact == 0 and (not sold_is_native) and sold_token_lc in wrapped_set:
            sold_exact = max(
                user_transfers_out.get(sold_token_lc, 0), withdrawal_from_user
            )

        # --- Compute humanized rate (bought / sold) ---
        if sold_exact > 0 and bought_exact > 0:
            s_dec = await self._decimals(sell_token.address)
            b_dec = await self._decimals(buy_token.address)
            sold_h = Decimal(sold_exact) / (Decimal(10) ** s_dec)
            bought_h = Decimal(bought_exact) / (Decimal(10) ** b_dec)
            rate: Optional[Decimal] = (bought_h / sold_h) if sold_h != 0 else None
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
