from decimal import Decimal
import json
from typing import cast
from eth_typing import ChecksumAddress
from invest_agent.investment.basket_investment import Bid
from invest_agent.investment.investment_parameters import InvestmentParameters
from protocol.token import Token
from web3 import Account, Web3, AsyncWeb3
from web3.contract import AsyncContract
from web3.types import TxReceipt, Wei
from uniswap_universal_router_decoder import FunctionRecipient, RouterCodec

from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain
from invest_agent.investment.exchange.exchange import (
    ConvertedBalance,
    Wallet,
    Exchange,
)
from invest_agent.investment.infrastructure.pancakeswap.universal_router.permit2 import (
    Permit2,
)
from invest_agent.investment.investment_plan import InvestmentPlan


# https://github.com/Uniswap/permit2/blob/main/src/interfaces/IAllowanceTransfer.sol
# https://github.com/Elnaril/uniswap-universal-router-decoder
class PancakeSwapUniversalRouter(Exchange):
    # TODO: handle multiple base tokens
    base_token = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

    def __init__(
        self,
        universal_router_address: str,
        v2_router_address: str,
        private_key: str,
        chain: Chain,
        permit2: Permit2,
        w3: AsyncWeb3,
    ):
        self.universal_router_address = universal_router_address
        self.v2_router_address = v2_router_address
        self.private_key = private_key
        self.chain = chain
        self.permit2 = permit2

        self.w3 = w3
        self.account = Account.from_key(private_key)
        self.codec = RouterCodec()

        with open(
            "./invest_agent/investment/infrastructure/pancakeswap/universal_router/universal_router_abi.json",
            "r",
        ) as f:
            self.universal_router_abi = json.load(f)

        with open(
            "./invest_agent/investment/infrastructure/pancakeswap/universal_router/v2_router_abi.json",
            "r",
        ) as f:
            self.v2_router_abi = json.load(f)

        with open(
            "./invest_agent/infrastructure/bsc/chain/erc20_token_abi.json",
            "r",
        ) as f:
            self.erc20_token_abi = json.load(f)

        self.universal_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(universal_router_address),
            abi=self.universal_router_abi,
        )
        self.v2_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(v2_router_address),
            abi=self.v2_router_abi,
        )

    async def execute_investment_plan(
        self,
        investment_plan: InvestmentPlan,
        investment_parameters: InvestmentParameters,
    ) -> list[Bid]:
        self.permit2.approve_permit2_contract(Web3.to_checksum_address(self.base_token))

        signed_message, permit_data, deadline = await self.permit2.sign_permit2_message(
            Web3.to_checksum_address(self.base_token),
            Web3.to_checksum_address(self.universal_router_address),
        )

        amount = self.w3.to_wei(investment_plan.sell_balance.amount, "ether")

        swap_chain = (
            self.codec.encode.chain()
            .permit2_permit(permit_data, signed_message)
            .wrap_eth(
                FunctionRecipient.ROUTER,
                amount,
            )
        )

        has_base_token_in_investment_plan = self.__has_base_token_in_investment_plan(
            investment_plan
        )

        for step in investment_plan.steps:
            if step.token.address == self.base_token:
                continue

            amount_in = self.w3.to_wei(step.sell_balance.amount, "ether")
            path = [
                Web3.to_checksum_address(self.base_token),
                Web3.to_checksum_address(step.token.address),
            ]
            amount_out_min = self.__compute_amount_out_min(
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

        if has_base_token_in_investment_plan:
            swap_chain = swap_chain.sweep(
                FunctionRecipient.SENDER,
                Web3.to_checksum_address(self.base_token),
                Wei(0),
            )
        else:
            swap_chain = swap_chain.unwrap_weth(FunctionRecipient.SENDER, Wei(0))

        encoded_input = swap_chain.build(
            self.permit2.get_default_deadline()  # 180 seconds
        )

        receipt = await self.chain.sign_send_wait_transaction(
            amount=amount,
            to_address=self.universal_router_address,
            encoded_input=encoded_input,
        )

        bids = self.__parse_bids_from_receipt(receipt, investment_plan)

        print(f"bids: {bids}")

        return bids

    async def execute_divestment_plan(
        self,
        divestment_plan: InvestmentPlan,
        investment_parameters: InvestmentParameters,
    ) -> list[Bid]:
        amount = 0
        swap_chain = self.codec.encode.chain()

        for step in divestment_plan.steps:
            print(f"token: {step.token.name}")

            if step.token.address == self.base_token:
                # If the base token is in the divestment plan, we need to send it to the router
                swap_chain = swap_chain.permit2_transfer_from(
                    FunctionRecipient.ROUTER,
                    Web3.to_checksum_address(step.token.address),
                    self.w3.to_wei(step.sell_balance.amount, "ether"),
                )
            else:
                contract = self.w3.eth.contract(
                    address=self.w3.to_checksum_address(step.token.address),
                    abi=self.erc20_token_abi,
                )

                await self.permit2.approve_permit2_contract(
                    Web3.to_checksum_address(step.token.address)
                )

                (
                    signed_message,
                    permit_data,
                    _deadline,
                ) = await self.permit2.sign_permit2_message(
                    Web3.to_checksum_address(step.token.address),
                    Web3.to_checksum_address(self.universal_router_address),
                )

                amount_in = await self.__get_raw_amount(
                    contract, step.sell_balance.amount
                )
                path = [
                    Web3.to_checksum_address(step.token.address),
                    Web3.to_checksum_address(self.base_token),
                ]
                amount_out_min = await self.__compute_amount_out_min(
                    amount_in,
                    path,
                )

                swap_chain = swap_chain.permit2_permit(
                    permit_data,
                    signed_message,
                    # TODO: check to use v3
                ).v2_swap_exact_in(
                    FunctionRecipient.ROUTER,
                    Wei(amount_in),
                    amount_out_min,
                    path,
                    payer_is_sender=True,
                )

        encoded_input = swap_chain.unwrap_weth(FunctionRecipient.SENDER, Wei(0)).build(
            self.permit2.get_default_deadline(),  # 180 seconds
        )

        print("Executing batch transaction")

        try:
            receipt = await self.chain.sign_send_wait_transaction(
                amount=amount,
                to_address=self.universal_router_address,
                encoded_input=encoded_input,
            )

            print(f"Receipt: {receipt}")

            # TODO: parse bids from receipt
            return []
        # TODO: handle gracefully errors
        except Exception as e:
            print(f"Error executing batch transaction: {e}")
            raise e

    async def get_wallet_in_token(
        self,
        tokens_balance: list[Balance],
        token: Token,
        investment_parameters: InvestmentParameters,
    ) -> Wallet:
        balances: list[ConvertedBalance] = []

        token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token.address),
            abi=self.erc20_token_abi,
        )

        for balance in tokens_balance:
            if balance.token.address == token.address:
                balances.append(
                    ConvertedBalance(
                        sell_balance=balance,
                        buy_balance=balance,
                    )
                )
            else:
                balance_token_contract = self.w3.eth.contract(
                    address=self.w3.to_checksum_address(balance.token.address),
                    abi=self.erc20_token_abi,
                )

                amounts_out = await self.v2_router.functions.getAmountsOut(
                    await self.__get_raw_amount(balance_token_contract, balance.amount),
                    [
                        Web3.to_checksum_address(balance.token.address),
                        Web3.to_checksum_address(token.address),
                    ],
                ).call()

                balances.append(
                    ConvertedBalance(
                        sell_balance=balance,
                        buy_balance=Balance(
                            token=token,
                            amount=await self.__get_token_amount(
                                token_contract, amounts_out[1]
                            ),
                        ),
                    )
                )

        return Wallet(
            balances=balances,
            total_balance=self.__sum_balances(balances, token),
        )

    def __sum_balances(self, balances: list[ConvertedBalance], token: Token):
        return Balance(
            token=token,
            amount=cast(
                Decimal, sum([balance.buy_balance.amount for balance in balances])
            ),
        )

    async def __compute_amount_out_min(
        self,
        amount_in: int,
        path: list[ChecksumAddress],
    ) -> Wei:
        slipping_tolerance = 0.05  # 5% slippage
        amounts_out = await self.v2_router.functions.getAmountsOut(
            amount_in, path
        ).call()
        amount_out_min = Wei(int(amounts_out[-1] * (1 - slipping_tolerance)))

        print(f"amount_out_min: {amount_out_min}")

        return amount_out_min

    def __has_base_token_in_investment_plan(
        self, investment_plan: InvestmentPlan
    ) -> bool:
        return any(
            step.token.address == self.base_token for step in investment_plan.steps
        )

    async def __parse_bids_from_receipt(
        self, receipt: TxReceipt, investment_plan: InvestmentPlan
    ) -> list[Bid]:
        bids: list[Bid] = []

        for step in investment_plan.steps:
            # Special case for base token that is not swapped hence not in transaction logs
            if step.token.address == self.base_token:
                base_token_balance = await self.chain.get_token_balance_amount(
                    self.base_token,
                )

                print(f"Base token special case, balance: {base_token_balance}")

                bids.append(
                    Bid(
                        token=step.token,
                        sell_balance=Balance(
                            token=step.token,
                            amount=step.sell_balance.amount,
                        ),
                        buy_balance=Balance(
                            token=step.token, amount=base_token_balance
                        ),
                    )
                )
            else:
                for log in receipt["logs"]:
                    if log["address"].lower() == step.token.address.lower():
                        try:
                            contract = self.w3.eth.contract(
                                address=self.w3.to_checksum_address(
                                    log["address"].lower()
                                ),
                                abi=self.erc20_token_abi,
                            )
                            decoded = contract.events.Transfer().process_log(log)

                            if (
                                decoded["args"]["to"].lower()
                                == self.account.address.lower()
                            ):
                                bids.append(
                                    Bid(
                                        token=step.token,
                                        sell_balance=Balance(
                                            token=self.chain.get_base_token(),
                                            amount=step.sell_balance.amount,
                                        ),
                                        buy_balance=Balance(
                                            token=step.token,
                                            amount=await self.__get_token_amount(
                                                contract, decoded["args"]["value"]
                                            ),
                                        ),
                                    )
                                )

                        except Exception as e:
                            print(f"Error decoding log: {e}")
                            continue

        return bids

    async def __get_token_amount(
        self, token_contract: AsyncContract, raw_amount: int | Decimal
    ) -> Decimal:
        decimals = await token_contract.functions.decimals().call()

        return Decimal(raw_amount) / Decimal(10**decimals)

    # TODO: See how to store the decimals in the Token class
    async def __get_raw_amount(
        self, token_contract: AsyncContract, amount: Decimal
    ) -> int:
        decimals = await token_contract.functions.decimals().call()
        return int(amount * Decimal(10**decimals))
