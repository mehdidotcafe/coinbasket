import json
from eth_typing import HexStr
from web3 import Account, Web3
from uniswap_universal_router_decoder import FunctionRecipient, RouterCodec

from coinbasket.chain.balance import Balance
from coinbasket.chain.chain import Chain
from coinbasket.investment_planner.exchange.exchange import Exchange
from coinbasket.investment_planner.investment_plan import InvestmentPlan
from coinbasket.investment_planner.investment_result import (
    InvestmentResult,
    InvestmentResultBid,
)


# https://github.com/Uniswap/permit2/blob/main/src/interfaces/IAllowanceTransfer.sol
class PancakeSwapUniversalRouter(Exchange):
    def __init__(
        self,
        bsc_rpc_url: str,
        universal_router_address: str,
        permit2_contract_address: str,
        v2_router_address: str,
        private_key: str,
        chain: Chain,
    ):
        self.universal_router_address = universal_router_address
        self.permit2_contract_address = permit2_contract_address
        self.v2_router_address = v2_router_address
        self.private_key = private_key
        self.chain = chain

        self.w3 = Web3(
            Web3.HTTPProvider(bsc_rpc_url),
        )
        self.account = Account.from_key(private_key)
        self.codec = RouterCodec()

        with open(
            "./coinbasket/investment_planner/exchange/pancakeswap/universal_router_abi.json",
            "r",
        ) as f:
            self.universal_router_abi = json.load(f)

        with open(
            "./coinbasket/investment_planner/exchange/pancakeswap/permit2_contract_abi.json",
            "r",
        ) as f:
            self.permit2_contract_abi = json.load(f)

        with open(
            "./coinbasket/investment_planner/exchange/pancakeswap/v2_router_abi.json",
            "r",
        ) as f:
            self.v2_router = json.load(f)

        with open(
            "./coinbasket/investment_planner/exchange/pancakeswap/erc20_token_abi.json",
            "r",
        ) as f:
            self.erc20_token_abi = json.load(f)

        self.universal_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(universal_router_address),
            abi=self.universal_router_abi,
        )
        self.permit2_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(permit2_contract_address),
            abi=self.permit2_contract_abi,
        )
        self.v2_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(v2_router_address),
            abi=self.v2_router,
        )

    def execute_investment_plan(
        self, investment_plan: InvestmentPlan
    ) -> InvestmentResult:
        # TODO: handle multiple base tokens
        base_token = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

        self.approve_permit2_contract(base_token)

        signed_message, permit_data, deadline = self.sign_permit2_message(base_token)

        amount = self.w3.to_wei(investment_plan.balance.amount, "ether")

        chain = (
            self.codec.encode.chain()
            .permit2_permit(permit_data, signed_message)
            .wrap_eth(
                FunctionRecipient.ROUTER,
                self.w3.to_wei(investment_plan.balance.amount, "ether"),
            )
        )

        for step in investment_plan.steps:
            amount_in = self.w3.to_wei(step.amount, "ether")
            path = [
                Web3.to_checksum_address(base_token),
                Web3.to_checksum_address(step.token.address),
            ]
            amount_out_min = self.compute_amount_out_min(
                amount_in,
                path,
            )

            # TODO: check to use v3
            chain = chain.v2_swap_exact_in(
                FunctionRecipient.SENDER,
                amount_in,
                amount_out_min,
                path,
                payer_is_sender=False,
            )

        encoded_input = chain.build(deadline)

        receipt = self.sign_send_wait_transaction(encoded_input, amount)

        bids = self.parse_bids_from_receipt(receipt, investment_plan)

        print(f"bids: {bids}")

        return InvestmentResult(
            bids,
        )

    def approve_permit2_contract(self, base_token: str):
        amount = 0
        permit2_allowance = 2**256 - 1

        base_token_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(base_token),
            abi=self.erc20_token_abi,
        )

        contract_function = base_token_contract.functions.approve(
            Web3.to_checksum_address(self.permit2_contract_address),
            permit2_allowance,
        )

        gas_estimate = self.compute_gas_estimation(amount=amount)

        transaction = contract_function.build_transaction(
            {
                "from": self.account.address,
                "gas": gas_estimate,
                "maxPriorityFeePerGas": self.w3.eth.max_priority_fee,
                "maxFeePerGas": 100 * 10**9,
                "type": "0x2",
                "chainId": self.w3.eth.chain_id,
                "value": amount,
                "nonce": self.w3.eth.get_transaction_count(
                    self.account.address, "pending"
                ),
            }
        )
        raw_transaction = self.w3.eth.account.sign_transaction(
            transaction, self.account.key
        ).raw_transaction
        transaction_hash = self.w3.eth.send_raw_transaction(raw_transaction)
        print(f"Permit2 Trx Hash: {transaction_hash.hex()}")

        receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        print(f"Permit2 Receipt: {receipt}")

    def get_permit2_nonce(self, token: str) -> int:
        _permit2_amount, _permit2_expiration, permit2_nonce = (
            self.codec.fetch_permit2_allowance(
                wallet=self.account.address,
                token=Web3.to_checksum_address(token),
                spender=Web3.to_checksum_address(self.universal_router_address),
                permit2=Web3.to_checksum_address(self.permit2_contract_address),
                permit2_abi=self.permit2_contract_abi,
            )
        )

        return permit2_nonce

    def sign_permit2_message(self, base_token: str):
        allowance_amount = 2**160 - 1  # max/infinite
        deadline = self.codec.get_default_deadline()  # 180 seconds
        permit2_nonce = self.get_permit2_nonce(base_token)

        permit_data, signable_message = self.codec.create_permit2_signable_message(
            token_address=Web3.to_checksum_address(base_token),
            amount=allowance_amount,
            expiration=self.codec.get_default_expiration(),  # 30 days
            nonce=permit2_nonce,
            spender=Web3.to_checksum_address(self.universal_router_address),
            deadline=deadline,
            chain_id=self.w3.eth.chain_id,
            verifying_contract=Web3.to_checksum_address(self.permit2_contract_address),
        )
        signed_message = self.account.sign_message(signable_message)

        return signed_message, permit_data, deadline

    def compute_amount_out_min(
        self,
        amount_in: int,
        path: list[str],
    ) -> int:
        slipping_tolerance = 0.05  # 5% slippage
        amounts_out = self.v2_router.functions.getAmountsOut(amount_in, path).call()
        amount_out_min = int(amounts_out[-1] * (1 - slipping_tolerance))

        print(f"amount_out_min: {amount_out_min}")

        return amount_out_min

    def compute_gas_estimation(
        self, amount: int, encoded_input: HexStr | None = None
    ) -> int:
        transaction_params = {
            "from": self.account.address,
            "to": Web3.to_checksum_address(self.universal_router_address),
            "value": amount,
        }

        if encoded_input is not None:
            transaction_params["data"] = encoded_input

        return int(self.w3.eth.estimate_gas(transaction_params) * 1.1)

    def sign_send_wait_transaction(self, encoded_input: HexStr, amount: int):
        latest_block = self.w3.eth.get_block("latest")
        base_fee = latest_block["baseFeePerGas"]
        max_priority_fee = self.w3.to_wei(2, "gwei")  # This is the miner "tip"
        max_fee_per_gas = base_fee * 2 + max_priority_fee

        gas_estimate = self.compute_gas_estimation(
            encoded_input=encoded_input,
            amount=amount,
        )

        transaction_params = {
            "from": self.account.address,
            "to": Web3.to_checksum_address(self.universal_router_address),
            "gas": gas_estimate,
            "maxPriorityFeePerGas": max_priority_fee,
            "maxFeePerGas": max_fee_per_gas,
            "chainId": self.w3.eth.chain_id,
            "type": "0x2",
            "value": amount,
            "nonce": self.w3.eth.get_transaction_count(self.account.address, "pending"),
            "data": encoded_input,
        }
        raw_transaction = self.w3.eth.account.sign_transaction(
            transaction_params, self.account.key
        ).raw_transaction
        transaction_hash = self.w3.eth.send_raw_transaction(raw_transaction)
        print(f"Trx Hash: {transaction_hash.hex()}")

        receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash)
        print(f"Receipt: {receipt}")

        return receipt

    def parse_bids_from_receipt(
        self, receipt, investment_plan: InvestmentPlan
    ) -> list[Balance]:
        bids = []

        for step in investment_plan.steps:
            for log in receipt.logs:
                if log.address.lower() == step.token.address.lower():
                    try:
                        decoded = (
                            self.w3.eth.contract(
                                address=self.w3.to_checksum_address(
                                    log.address.lower()
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
                                        amount=self.w3.from_wei(
                                            decoded["args"]["value"], "ether"
                                        ),
                                    ),
                                )
                            )

                    except Exception as e:
                        print(f"Error decoding log: {e}")
                        continue

        return bids
