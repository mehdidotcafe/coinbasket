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
from invest_agent.investment.investment_parameters import InvestmentParameters
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

    def execute_investment_plan(
        self,
        investment_plan: InvestmentPlan,
        investment_parameters: InvestmentParameters,
    ) -> list[Bid]:
        bids: list[Bid] = []

        sell_token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(
                investment_plan.sell_total_balance.token.address
            ),
            abi=self.erc20_token_abi,
        )

        for step in investment_plan.steps:
            try:
                bids.append(
                    self.__execute_investment_step(
                        step=step,
                        sell_token_contract=sell_token_contract,
                        sell_token=investment_plan.sell_total_balance.token,
                        investment_parameters=investment_parameters,
                    )
                )
            except Exception as e:
                print(f"Investment step failed: {e}")

        return bids

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), reraise=True)
    def __execute_investment_step(
        self,
        step: InvestmentPlanStep,
        sell_token_contract: Contract,
        sell_token: Token,
        investment_parameters: InvestmentParameters,
    ) -> Bid:
        print(
            f"=== {step.token.display_name} - {step.token.address} ({step.sell_balance.amount}) ==="
        )

        step_token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(step.token.address),
            abi=self.erc20_token_abi,
        )

        amount = int(
            self.__get_token_amount(
                token_contract=sell_token_contract,
                token=sell_token,
                raw_amount=step.sell_balance.amount,
            )
        )

        quote_result = self.api_client.get_quote(
            chain_id=self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=sell_token.address,
            buy_token=step.token.address,
            amount=amount,
            slippage_bps=self.__compute_slippage_tolerance_in_bps(
                investment_parameters.slippage_tolerance_in_percentage
            ),
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
            sell_token_contract=sell_token_contract,
            sell_token=sell_token,
            buy_token_contract=step_token_contract,
            buy_token=step.token,
        )

    def execute_divestment_plan(
        self,
        divestment_plan: InvestmentPlan,
        investment_parameters: InvestmentParameters,
    ) -> list[Bid]:
        bids: list[Bid] = []

        buy_token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(
                divestment_plan.sell_total_balance.token.address
            ),
            abi=self.erc20_token_abi,
        )

        for step in divestment_plan.steps:
            try:
                bids.append(
                    self.__execute_divestment_plan_step(
                        step=step,
                        buy_token_contract=buy_token_contract,
                        buy_token=divestment_plan.sell_total_balance.token,
                        investment_parameters=investment_parameters,
                    )
                )
            except Exception as e:
                print(f"Divestment step failed: {e}")

        return bids

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), reraise=True)
    def __execute_divestment_plan_step(
        self,
        step: InvestmentPlanStep,
        buy_token_contract: Contract,
        buy_token: Token,
        investment_parameters: InvestmentParameters,
    ) -> Bid:
        sell_token = step.sell_balance.token

        print(
            f"=== {sell_token.display_name} - {sell_token.address} ({step.sell_balance.amount}) ==="
        )

        sell_token_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(sell_token.address),
            abi=self.erc20_token_abi,
        )

        amount = int(
            self.__get_token_amount(
                token_contract=sell_token_contract,
                token=step.sell_balance.token,
                raw_amount=step.sell_balance.amount,
            )
        )

        price = self.api_client.get_price(
            chain_id=self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=step.sell_balance.token.address,
            amount=amount,
            buy_token=buy_token.address,
            sell_entire_balance=True,
            slippage_bps=self.__compute_slippage_tolerance_in_bps(
                investment_parameters.slippage_tolerance_in_percentage
            ),
        )

        self.__approve_allowance(
            price=price, token_contract=sell_token_contract, token=sell_token
        )

        quote_result = self.api_client.get_quote(
            chain_id=self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=sell_token.address,
            buy_token=buy_token.address,
            amount=amount,
            sell_entire_balance=True,
            slippage_bps=self.__compute_slippage_tolerance_in_bps(
                investment_parameters.slippage_tolerance_in_percentage
            ),
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
            buy_token_contract=buy_token_contract,
            buy_token=buy_token,
            sell_token_contract=sell_token_contract,
            sell_token=sell_token,
        )

    def get_wallet_in_token(
        self, tokens_balance: list[Balance], token: Token
    ) -> Wallet:
        balances: list[ConvertedBalance] = []

        buy_token_contract = self.w3.eth.contract(
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
                    sell_balance=Balance(
                        token=balance.token,
                        amount=self.__get_raw_amount(
                            token_contract=balance_token_contract,
                            token=balance.token,
                            amount=Decimal(price.sellAmount),
                        ),
                    ),
                    buy_balance=Balance(
                        token=token,
                        amount=self.__get_raw_amount(
                            token_contract=buy_token_contract,
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
                Decimal, sum([balance.buy_balance.amount for balance in balances])
            ),
        )

    def __make_bid(
        self,
        quote: Quote,
        sell_token_contract: Contract,
        sell_token: Token,
        buy_token_contract: Contract,
        buy_token: Token,
    ) -> Bid:
        return Bid(
            token=buy_token,
            sell_balance=Balance(
                token=sell_token,
                amount=self.__get_raw_amount(
                    sell_token_contract, sell_token, Decimal(quote.sellAmount)
                ),
            ),
            buy_balance=Balance(
                token=buy_token,
                amount=self.__get_raw_amount(
                    buy_token_contract, buy_token, Decimal(quote.buyAmount)
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

    def __compute_slippage_tolerance_in_bps(
        self, slippage_tolerance_in_percentage: Decimal
    ) -> Decimal:
        return slippage_tolerance_in_percentage * 100
