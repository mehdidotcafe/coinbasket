from decimal import Decimal
import json
from eth_typing import ChecksumAddress
from web3 import Account, Web3
from web3.types import TxReceipt, Wei
from uniswap_universal_router_decoder import FunctionRecipient, RouterCodec  # type: ignore

from coinbasket.chain.balance import Balance
from coinbasket.chain.chain import Chain
from coinbasket.investment.exchange.exchange import Exchange
from coinbasket.investment.infrastructure.pancakeswap.exchange.permit2 import Permit2
from coinbasket.investment.investment_plan import InvestmentPlan
from coinbasket.investment.investment_result import (
    InvestmentResult,
    InvestmentResultBid,
)


# https://github.com/Uniswap/permit2/blob/main/src/interfaces/IAllowanceTransfer.sol
# https://github.com/Elnaril/uniswap-universal-router-decoder
class PancakeSwapUniversalRouter(Exchange):
    # TODO: handle multiple base tokens
    base_token = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

    def __init__(
        self,
        bsc_rpc_url: str,
        universal_router_address: str,
        v2_router_address: str,
        private_key: str,
        chain: Chain,
        permit2: Permit2,
    ):
        self.universal_router_address = universal_router_address
        self.v2_router_address = v2_router_address
        self.private_key = private_key
        self.chain = chain
        self.permit2 = permit2

        self.w3 = Web3(
            Web3.HTTPProvider(bsc_rpc_url),
        )
        self.account = Account.from_key(private_key)
        self.codec = RouterCodec()

        with open(
            "./coinbasket/investment/infrastructure/pancakeswap/exchange/universal_router_abi.json",
            "r",
        ) as f:
            self.universal_router_abi = json.load(f)

        with open(
            "./coinbasket/investment/infrastructure/pancakeswap/exchange/v2_router_abi.json",
            "r",
        ) as f:
            self.v2_router = json.load(f)

        with open(
            "./coinbasket/infrastructure/bsc/chain/erc20_token_abi.json",
            "r",
        ) as f:
            self.erc20_token_abi = json.load(f)

        self.universal_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(universal_router_address),
            abi=self.universal_router_abi,
        )
        self.v2_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(v2_router_address),
            abi=self.v2_router,
        )

    def execute_investment_plan(
        self, investment_plan: InvestmentPlan
    ) -> InvestmentResult:
        self.permit2.approve_permit2_contract(Web3.to_checksum_address(self.base_token))

        signed_message, permit_data, deadline = self.permit2.sign_permit2_message(
            Web3.to_checksum_address(self.base_token),
            Web3.to_checksum_address(self.universal_router_address),
        )

        amount = self.w3.to_wei(investment_plan.balance.amount, "ether")

        swap_chain = (
            self.codec.encode.chain()
            .permit2_permit(permit_data, signed_message)
            .wrap_eth(
                FunctionRecipient.ROUTER,
                amount,
            )
        )

        for step in investment_plan.steps:
            amount_in = self.w3.to_wei(step.amount, "ether")
            path = [
                Web3.to_checksum_address(self.base_token),
                Web3.to_checksum_address(step.token.address),
            ]
            amount_out_min = self.compute_amount_out_min(
                amount_in,
                path,
            )

            # TODO: check to use v3
            swap_chain = swap_chain.v2_swap_exact_in(
                FunctionRecipient.SENDER,
                amount_in,
                amount_out_min,
                path,
                payer_is_sender=False,
            )

        encoded_input = swap_chain.build(deadline)

        receipt = self.chain.sign_send_wait_transaction(
            amount,
            Web3.to_checksum_address(self.universal_router_address),
            encoded_input,
        )

        bids = self.parse_bids_from_receipt(receipt, investment_plan)

        print(f"bids: {bids}")

        return InvestmentResult(
            bids,
        )

    def execute_divestment_plan(
        self, divestment_plan: InvestmentPlan
    ) -> InvestmentResult:
        amount = 0
        swap_chain = self.codec.encode.chain()

        for step in divestment_plan.steps:
            self.permit2.approve_permit2_contract(
                Web3.to_checksum_address(step.token.address)
            )

            signed_message, permit_data, _deadline = self.permit2.sign_permit2_message(
                Web3.to_checksum_address(step.token.address),
                Web3.to_checksum_address(self.universal_router_address),
            )

            amount_in = self.w3.to_wei(step.amount, "ether")
            path = [
                Web3.to_checksum_address(step.token.address),
                Web3.to_checksum_address(self.base_token),
            ]
            amount_out_min = self.compute_amount_out_min(
                amount_in,
                path,
            )

            swap_chain = swap_chain.permit2_permit(
                permit_data,
                signed_message,
                # TODO: check to use v3
            ).v2_swap_exact_in(
                FunctionRecipient.ROUTER,
                amount_in,
                amount_out_min,
                path,
                payer_is_sender=True,
            )

        encoded_input = swap_chain.unwrap_weth(FunctionRecipient.SENDER, Wei(0)).build(
            self.permit2.get_default_deadline(),  # 180 seconds
        )

        receipt = self.chain.sign_send_wait_transaction(
            amount,
            Web3.to_checksum_address(self.universal_router_address),
            encoded_input,
        )

        print(f"Receipt: {receipt}")

        return InvestmentResult(bids=[])

    def compute_amount_out_min(
        self,
        amount_in: int,
        path: list[ChecksumAddress],
    ) -> Wei:
        slipping_tolerance = 0.05  # 5% slippage
        amounts_out = self.v2_router.functions.getAmountsOut(amount_in, path).call()
        amount_out_min = Wei(int(amounts_out[-1] * (1 - slipping_tolerance)))

        print(f"amount_out_min: {amount_out_min}")

        return amount_out_min

    def parse_bids_from_receipt(
        self, receipt: TxReceipt, investment_plan: InvestmentPlan
    ) -> list[InvestmentResultBid]:
        bids: list[InvestmentResultBid] = []

        for step in investment_plan.steps:
            for log in receipt["logs"]:
                if log["address"].lower() == step.token.address.lower():
                    try:
                        decoded = (
                            self.w3.eth.contract(
                                address=self.w3.to_checksum_address(
                                    log["address"].lower()
                                ),
                                abi=self.erc20_token_abi,
                            )
                            .events.Transfer()
                            .process_log(log)
                        )
                        if (
                            decoded["args"]["to"].lower()
                            == self.account.address.lower()
                        ):
                            bids.append(
                                InvestmentResultBid(
                                    token=step.token,
                                    balance_in=Balance(
                                        token=self.chain.get_base_token(),
                                        amount=step.amount,
                                    ),
                                    balance_out=Balance(
                                        token=step.token,
                                        amount=Decimal(
                                            self.w3.from_wei(
                                                decoded["args"]["value"], "ether"
                                            )
                                        ),
                                    ),
                                )
                            )

                    except Exception as e:
                        print(f"Error decoding log: {e}")
                        continue

        return bids
