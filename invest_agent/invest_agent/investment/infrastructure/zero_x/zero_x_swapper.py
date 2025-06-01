from decimal import Decimal
import json
from typing import TypedDict, cast
from hexbytes import HexBytes
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain, Gas
from invest_agent.investment.basket_investment import Bid
from invest_agent.investment.exchange.exchange import ConvertedBalance, Exchange, Wallet
from invest_agent.investment.infrastructure.zero_x.exception.swap_insufficient_liquidity import (
    SwapInsufficientLiquidity,
)
from invest_agent.investment.infrastructure.zero_x.price import Price
from invest_agent.investment.infrastructure.zero_x.quote import (
    InsufficientLiquidityQuote,
    Quote,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from invest_agent.investment.investment_plan import InvestmentPlan, InvestmentPlanStep
from protocol.token import Token
from tenacity import retry, stop_after_attempt
from web3 import Web3
from web3.contract import Contract

from eth_account.signers.local import LocalAccount
from eth_account.datastructures import (
    SignedMessage,
)

RETRY_ATTEMPTS = 5


class Configuration(TypedDict):
    bsc_rpc_url: str
    private_key: str


# LINK: https://0x.org/docs/api#tag/Swap/operation/swap::permit2::getPrice
# LINK: https://0x.org/docs/0x-swap-api/guides/swap-tokens-with-0x-swap-api
class ZeroXSwapper(Exchange):
    def __init__(
        self,
        api_client: ZeroXApiClient,
        chain: Chain,
        configuration: Configuration,
        w3: Web3,
    ):
        self.api_client = api_client
        self.chain = chain
        self.bsc_rpc_url = configuration["bsc_rpc_url"]

        self.w3 = w3
        self.account: LocalAccount = self.w3.eth.account.from_key(
            private_key=configuration["private_key"]
        )

        with open(
            "./invest_agent/infrastructure/bsc/chain/erc20_token_abi.json",
            "r",
            encoding="utf-8",
        ) as f:
            self.erc20_token_abi = json.load(f)

    def execute_investment_plan(self, investment_plan: InvestmentPlan) -> list[Bid]:
        bids: list[Bid] = []

        base_token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(investment_plan.balance.token.address),
            abi=self.erc20_token_abi,
        )

        for step in investment_plan.steps:
            try:
                bids.append(
                    self.__execute_investment_step(
                        step=step,
                        base_token_contract=base_token_contract,
                        base_token=investment_plan.balance.token,
                    )
                )
            except Exception as e:
                print(f"Investment step failed: {e}")

        return bids

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), reraise=True)
    def __execute_investment_step(
        self,
        step: InvestmentPlanStep,
        base_token_contract: Contract,
        base_token: Token,
    ) -> Bid:
        print(
            f"=== {step.token.display_name} - {step.token.address} ({step.amount}) ==="
        )

        step_token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(step.token.address),
            abi=self.erc20_token_abi,
        )

        amount = int(
            self.__get_token_amount(
                token_contract=base_token_contract,
                token=base_token,
                raw_amount=step.amount,
            )
        )

        quote_result = self.api_client.get_quote(
            chain_id=self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=base_token.address,
            buy_token=step.token.address,
            amount=amount,
        )
        quote = quote_result.root

        if isinstance(quote, InsufficientLiquidityQuote):
            raise SwapInsufficientLiquidity()

        transaction_data = self.__make_transaction_data(quote)

        self.chain.sign_send_wait_transaction(
            gas=Gas(
                gas=int(quote.transaction.gas) if quote.transaction.gas else None,
                gas_price=int(quote.transaction.gasPrice)
                if quote.transaction.gasPrice
                else None,
            ),
            to_address=quote.transaction.to,
            encoded_input=transaction_data,
            amount=int(quote.transaction.value) if quote.transaction.value else 0,
        )

        return self.__make_bid(
            quote=quote,
            token_in_contract=base_token_contract,
            token_in=base_token,
            token_out_contract=step_token_contract,
            token_out=step.token,
        )

    def execute_divestment_plan(self, divestment_plan: InvestmentPlan) -> list[Bid]:
        bids: list[Bid] = []

        base_token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(divestment_plan.balance.token.address),
            abi=self.erc20_token_abi,
        )

        for step in divestment_plan.steps:
            try:
                bids.append(
                    self.__execute_divestment_plan_step(
                        step=step,
                        base_token_contract=base_token_contract,
                        base_token=divestment_plan.balance.token,
                    )
                )
            except Exception as e:
                print(f"Divestment step failed: {e}")

        return bids

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), reraise=True)
    def __execute_divestment_plan_step(
        self,
        step: InvestmentPlanStep,
        base_token_contract: Contract,
        base_token: Token,
    ) -> Bid:
        print(
            f"=== {step.token.display_name} - {step.token.address} ({step.amount}) ==="
        )

        step_token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(step.token.address),
            abi=self.erc20_token_abi,
        )

        amount = int(
            self.__get_token_amount(
                token_contract=step_token_contract,
                token=step.token,
                raw_amount=step.amount,
            )
        )

        price = self.api_client.get_price(
            chain_id=self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=step.token.address,
            amount=amount,
            buy_token=base_token.address,
            sell_entire_balance=True,
        )

        self.__approve_allowance(
            price=price, token_contract=step_token_contract, token=step.token
        )

        quote_result = self.api_client.get_quote(
            chain_id=self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=step.token.address,
            buy_token=base_token.address,
            amount=amount,
            sell_entire_balance=True,
        )
        quote = quote_result.root

        if isinstance(quote, InsufficientLiquidityQuote):
            raise SwapInsufficientLiquidity()

        transaction_data = self.__make_transaction_data(quote)

        self.chain.sign_send_wait_transaction(
            gas=Gas(
                gas=int(quote.transaction.gas) if quote.transaction.gas else None,
                gas_price=int(quote.transaction.gasPrice)
                if quote.transaction.gasPrice
                else None,
            ),
            to_address=quote.transaction.to,
            encoded_input=transaction_data,
            amount=int(quote.transaction.value) if quote.transaction.value else 0,
        )

        print(f"==================")

        return self.__make_bid(
            quote=quote,
            token_in_contract=base_token_contract,
            token_in=base_token,
            token_out_contract=step_token_contract,
            token_out=step.token,
        )

    def get_wallet_in_token(
        self, tokens_balance: list[Balance], token: Token
    ) -> Wallet:
        balances: list[ConvertedBalance] = []

        base_token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token.address),
            abi=self.erc20_token_abi,
        )

        for balance in tokens_balance:
            balance_token_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(balance.token.address),
                abi=self.erc20_token_abi,
            )

            amount = int(
                self.__get_token_amount(
                    token_contract=balance_token_contract,
                    token=balance.token,
                    raw_amount=balance.amount,
                )
            )

            price = self.api_client.get_price(
                chain_id=self.chain.get_chain_id(),
                taker=self.account.address,
                sell_token=balance.token.address,
                buy_token=token.address,
                amount=amount,
            )

            balances.append(
                ConvertedBalance(
                    balance_in=Balance(
                        token=balance.token,
                        amount=self.__get_raw_amount(
                            token_contract=balance_token_contract,
                            token=balance.token,
                            amount=Decimal(price.sellAmount),
                        ),
                    ),
                    balance_out=Balance(
                        token=token,
                        amount=self.__get_raw_amount(
                            token_contract=base_token_contract,
                            token=token,
                            amount=Decimal(price.buyAmount),
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
                Decimal, sum([balance.balance_out.amount for balance in balances])
            ),
        )

    def __make_bid(
        self,
        quote: Quote,
        token_in_contract: Contract,
        token_in: Token,
        token_out_contract: Contract,
        token_out: Token,
    ) -> Bid:
        return Bid(
            token=token_out,
            balance_in=Balance(
                token=token_in,
                amount=self.__get_raw_amount(
                    token_in_contract, token_in, Decimal(quote.sellAmount)
                ),
            ),
            balance_out=Balance(
                token=token_out,
                amount=self.__get_raw_amount(
                    token_out_contract, token_out, Decimal(quote.buyAmount)
                ),
            ),
        )

    def __make_transaction_data(self, quote: Quote):
        if quote.permit2 is None:
            return quote.transaction.data

        signature: SignedMessage = self.w3.eth.account.sign_typed_data(
            full_message=quote.permit2.eip712,
            private_key=self.account.key,
        )

        signature_hex = signature.signature.to_0x_hex()

        signature_length_hex = self.__compute_signature_length_in_hex(
            signature.signature
        )

        transaction_data = quote.transaction.data

        return "0x" + "".join(
            [
                h[2:]
                for h in [
                    transaction_data,
                    signature_length_hex,
                    signature_hex,
                ]
            ]
        )

    def __compute_signature_length_in_hex(self, signature: HexBytes) -> str:
        sig_len = len(signature)

        sig_len_hex = "0x" + sig_len.to_bytes(32, "big").hex()
        return sig_len_hex

    def __approve_allowance(self, price: Price, token_contract: Contract, token: Token):
        if self.chain.is_native_token(token) or price.issues.allowance is None:
            return

        contract_function = token_contract.functions.approve(
            self.w3.to_checksum_address(price.issues.allowance.spender), 2**256 - 1
        )

        encoded_input = contract_function._encode_transaction_data()

        receipt = self.chain.sign_send_wait_transaction(
            amount=0,
            encoded_input=encoded_input,
            to_address=token.address,
        )

        return receipt

    def __get_token_amount(
        self, token_contract: Contract, token: Token, raw_amount: Decimal
    ) -> Decimal:
        if self.chain.is_native_token(token):
            return Decimal(self.w3.to_wei(raw_amount, "ether"))

        decimals = token_contract.functions.decimals().call()

        return raw_amount * (10**decimals)

    def __get_raw_amount(
        self, token_contract: Contract, token: Token, amount: Decimal
    ) -> Decimal:
        decimals = (
            18
            if self.chain.is_native_token(token)
            else token_contract.functions.decimals().call()
        )

        return amount / (10**decimals)
