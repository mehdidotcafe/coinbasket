import asyncio
from decimal import Decimal
from typing import TypedDict, cast
from hexbytes import HexBytes
from invest_agent.chain.balance import Balance
from invest_agent.chain.chain import Chain, Gas
from invest_agent.chain.contract import Contract
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
from web3 import AsyncWeb3

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
        contract: Contract,
        configuration: Configuration,
        w3: AsyncWeb3,
    ):
        self.api_client = api_client
        self.chain = chain
        self.contract = contract
        self.bsc_rpc_url = configuration["bsc_rpc_url"]

        self.w3 = w3
        self.account: LocalAccount = self.w3.eth.account.from_key(
            private_key=configuration["private_key"]
        )

    async def execute_investment_plan(
        self,
        investment_plan: InvestmentPlan,
        investment_parameters: InvestmentParameters,
    ) -> list[Bid]:
        tasks = [
            self.__execute_investment_step(
                step=step,
                sell_token=investment_plan.sell_total_balance.token,
                investment_parameters=investment_parameters,
            )
            for step in investment_plan.steps
        ]

        bids: list[Bid] = []

        for task in tasks:
            try:
                bids.append(await task)
            except BaseException as e:
                print(f"Investment step failed: {e!r}")

        return bids

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), reraise=True)
    async def __execute_investment_step(
        self,
        step: InvestmentPlanStep,
        sell_token: Token,
        investment_parameters: InvestmentParameters,
    ) -> Bid:
        print(
            f"=== {step.token.display_name} - {step.token.address} ({step.sell_balance.amount}) ==="
        )

        amount = int(
            await self.__get_token_amount(
                token=sell_token,
                raw_amount=step.sell_balance.amount,
            )
        )

        quote_result = await self.api_client.get_quote(
            chain_id=await self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=sell_token.address,
            buy_token=step.token.address,
            amount=amount,
            slippage_bps=self.__compute_slippage_tolerance_in_bps(
                investment_parameters.slippage_tolerance_in_percentage
            ),
            investment_parameters=investment_parameters,
        )
        quote = quote_result.root

        if isinstance(quote, InsufficientLiquidityQuote):
            raise SwapInsufficientLiquidity()

        transaction_data = self.__make_transaction_data(quote)

        receipt = await self.chain.sign_send_wait_transaction(
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

        print(
            f"Receipt for {sell_token.display_name} -> {step.token.display_name}: {receipt}"
        )

        return await self.__make_bid(
            quote=quote,
            sell_token=sell_token,
            buy_token=step.token,
        )

    async def execute_divestment_plan(
        self,
        divestment_plan: InvestmentPlan,
        investment_parameters: InvestmentParameters,
    ) -> list[Bid]:
        tasks = [
            self.__execute_divestment_plan_step(
                step=step,
                buy_token=divestment_plan.sell_total_balance.token,
                investment_parameters=investment_parameters,
            )
            for step in divestment_plan.steps
        ]

        bids: list[Bid] = []
        for task in tasks:
            try:
                bids.append(await task)
            except BaseException as e:
                print(f"Divestment step failed: {e!r}")

        return bids

    @retry(stop=stop_after_attempt(RETRY_ATTEMPTS), reraise=True)
    async def __execute_divestment_plan_step(
        self,
        step: InvestmentPlanStep,
        buy_token: Token,
        investment_parameters: InvestmentParameters,
    ) -> Bid:
        sell_token = step.sell_balance.token

        print(
            f"=== {sell_token.display_name} - {sell_token.address} ({step.sell_balance.amount}) ==="
        )

        amount = int(
            await self.__get_token_amount(
                token=step.sell_balance.token,
                raw_amount=step.sell_balance.amount,
            )
        )

        price = await self.api_client.get_price(
            chain_id=await self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=step.sell_balance.token.address,
            amount=amount,
            buy_token=buy_token.address,
            sell_entire_balance=True,
            slippage_bps=self.__compute_slippage_tolerance_in_bps(
                investment_parameters.slippage_tolerance_in_percentage
            ),
            investment_parameters=investment_parameters,
        )

        await self.__approve_allowance(price=price, token=sell_token)

        quote_result = await self.api_client.get_quote(
            chain_id=await self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=sell_token.address,
            buy_token=buy_token.address,
            amount=amount,
            sell_entire_balance=True,
            slippage_bps=self.__compute_slippage_tolerance_in_bps(
                investment_parameters.slippage_tolerance_in_percentage
            ),
            investment_parameters=investment_parameters,
        )
        quote = quote_result.root

        if isinstance(quote, InsufficientLiquidityQuote):
            raise SwapInsufficientLiquidity()

        transaction_data = self.__make_transaction_data(quote)

        receipt = await self.chain.sign_send_wait_transaction(
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
        print(
            f"Receipt for {sell_token.display_name} -> {buy_token.display_name}: {receipt}"
        )

        return await self.__make_bid(
            quote=quote,
            buy_token=buy_token,
            sell_token=sell_token,
        )

    async def get_wallet_in_token(
        self,
        tokens_balance: list[Balance],
        token: Token,
        investment_parameters: InvestmentParameters,
    ) -> Wallet:
        balances: list[ConvertedBalance] = []

        tasks = [
            self.__convert_balance_to_token(
                balance=balance,
                token=token,
                investment_parameters=investment_parameters,
            )
            for balance in tokens_balance
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                print(f"Divestment step {i} failed: {result!r}")
            else:
                balances.append(result)

        return Wallet(
            balances=balances,
            total_balance=self.__sum_balances(balances, token),
        )

    async def __convert_balance_to_token(
        self,
        balance: Balance,
        token: Token,
        investment_parameters: InvestmentParameters,
    ):
        if self.__is_same_token(balance.token, token):
            return ConvertedBalance(
                sell_balance=Balance(
                    token=balance.token,
                    amount=balance.amount,
                ),
                buy_balance=Balance(
                    token=token,
                    amount=balance.amount,
                ),
            )

        amount = int(
            await self.__get_token_amount(
                token=balance.token,
                raw_amount=balance.amount,
            )
        )

        price = await self.api_client.get_price(
            chain_id=await self.chain.get_chain_id(),
            taker=self.account.address,
            sell_token=balance.token.address,
            buy_token=token.address,
            amount=amount,
            investment_parameters=investment_parameters,
        )

        return ConvertedBalance(
            sell_balance=Balance(
                token=balance.token,
                amount=await self.__get_raw_amount(
                    token=balance.token,
                    amount=Decimal(price.sellAmount),
                ),
            ),
            buy_balance=Balance(
                token=token,
                amount=await self.__get_raw_amount(
                    token=token,
                    amount=Decimal(price.buyAmount),
                ),
            ),
        )

    def __sum_balances(self, balances: list[ConvertedBalance], token: Token):
        return Balance(
            token=token,
            amount=cast(
                Decimal, sum([balance.buy_balance.amount for balance in balances])
            ),
        )

    async def __make_bid(
        self,
        quote: Quote,
        sell_token: Token,
        buy_token: Token,
    ) -> Bid:
        return Bid(
            token=buy_token,
            sell_balance=Balance(
                token=sell_token,
                amount=await self.__get_raw_amount(
                    sell_token, Decimal(quote.sellAmount)
                ),
            ),
            buy_balance=Balance(
                token=buy_token,
                amount=await self.__get_raw_amount(buy_token, Decimal(quote.buyAmount)),
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

    async def __approve_allowance(self, price: Price, token: Token):
        if self.chain.is_native_token(token) or price.issues.allowance is None:
            return

        encoded_input = self.contract.make_approve_transaction_input(
            token_address=token.address,
            spender_address=price.issues.allowance.spender,
            amount=Decimal(2**256 - 1),
        )

        receipt = await self.chain.sign_send_wait_transaction(
            amount=0,
            encoded_input=encoded_input,
            to_address=token.address,
        )

        return receipt

    async def __get_token_amount(self, token: Token, raw_amount: Decimal) -> Decimal:
        if self.chain.is_native_token(token):
            return Decimal(self.w3.to_wei(raw_amount, "ether"))

        decimals = await self.contract.get_decimals(token.address)

        return raw_amount * (10**decimals)

    async def __get_raw_amount(self, token: Token, amount: Decimal) -> Decimal:
        decimals = (
            18
            if self.chain.is_native_token(token)
            else await self.contract.get_decimals(token.address)
        )

        return amount / (10**decimals)

    def __compute_slippage_tolerance_in_bps(
        self, slippage_tolerance_in_percentage: Decimal
    ) -> Decimal:
        return slippage_tolerance_in_percentage * 100

    def __is_same_token(self, token1: Token, token2: Token) -> bool:
        return token1.address.lower() == token2.address.lower()
