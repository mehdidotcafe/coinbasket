from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Any, Dict, Literal, Optional, cast

import aiosqlite
from api.asset.get_asset_by_id_use_case import GetAssetByIdUseCase
from api.asset.get_asset_swap_price_use_case import (
    AssetSwapPriceInfo,
    ConvertedBalance,
    GetAssetSwapPriceUseCase,
)
from api.conversation.conversation_use_case import ConversationUseCase
from api.conversation.get_conversation_messages_use_case import (
    GetConversationMessagesUseCase,
)
from api.ingestion.data_source.infrastructure.bsc.ai_basket_data_source import (
    AiBasketDataSource,
)
from api.ingestion.data_source.infrastructure.bsc.big4_basket_data_source import (
    Big4BasketDataSource,
)
from api.ingestion.data_source.infrastructure.bsc.cmc_top_10_2025 import (
    CmcTop102025BasketDataSource,
)
from api.ingestion.data_source.infrastructure.bsc.coingecko_live_tokens_data_source import (
    CoingeckoLiveTokenListDataSource,
)
from api.ingestion.data_source.infrastructure.bsc.cryptoummah_halal_basket_data_source import (
    CryptoUmmahHalalBasketDataSource,
)
from api.ingestion.data_source.infrastructure.bsc.memecoin_mania_basket_data_source import (
    MemecoinManiaBasketDataSource,
)
from api.ingestion.ingest_data_use_case import IngestDataUseCase
from api.investment.build_priced_investment_plan_use_case import (
    BuildPricedInvestmentPlanUseCase,
)
from api.investment.execute_investment_plan_use_case import (
    ExecuteInvestmentPlanUseCase,
)
from api.investment.fees import Fees
from api.investment.investment_planner.intent_investment_plan import (
    IntentInvestmentPlan,
    IntentInvestmentPlanStep,
    IntentInvestmentPlanBalance,
)
from api.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from api.investment.order.order import (
    ChainTransaction,
    ChainTransactionStatus,
    ChainTransactionType,
    Order,
    OrderStatus,
    OrderTrigger,
    OrderType,
    Try,
)
from api.portfolio.get_portfolio_asset_balance_use_case import (
    GetPortfolioAssetBalanceUseCase,
    PortfolioAssetBalance,
)
from api.portfolio.get_portfolio_use_case import (
    GetPortfolioUseCase,
    Portfolio,
    PortfolioBalance,
)
from api.similarity.basket.get_all_baskets_use_case import GetAllBasketsUseCase
from api.similarity.get_similar_assets_use_case import GetSimilarAssetsUseCase
from api.protocol.basket import Basket
from api.protocol.fixture.basket import big4_basket, memecoinmania_basket
from api.protocol.fixture.token import (
    wbnb_token,
    eth_token,
    btc_token,
    sol_token,
    shib_token,
    cake_token,
)
from apispec import APISpec
from api.registry import (
    chain,
    configuration,
    conversation_repository,
    date_time,
    exchange,
    id_generator,
    order_repository,
    posting_repository,
    order_submitter,
    langgraph_db_path,
    nonce_manager,
    asset_balance_converter,
    small_balance_policy,
    similarity_storage,
    token_repository,
)
from api.authentication.authentication import authentication
from api.chain.balance import Balance, BalanceAtomic
from api.conversation.message import Message, QueryMessage
from api.documentation.response.invalid_authentication_key import (
    invalid_authentication_key,
)

from api.documentation.openapi import openapi
from api.protocol.token import Token
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, RootModel
from pydantic.v1 import root_validator, validator

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from api.protocol import (
    AssetResponse,
    BasketResponse,
    TokenResponse,
)
from api.protocol.fixture.token import usdt_token

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.types import interrupt

print(f"Thread ID: {configuration.langchain_thread_id}")
print(f"Agent Env: {configuration.app_env}")

get_portfolio_use_case = GetPortfolioUseCase(
    order_repository=order_repository,
    posting_repository=posting_repository,
    exchange=exchange,
    chain=chain,
    asset_balance_converter=asset_balance_converter,
    small_balance_policy=small_balance_policy,
)

get_portfolio_asset_balance_use_case = GetPortfolioAssetBalanceUseCase(
    chain=chain, posting_repository=posting_repository
)

conversation_use_case = ConversationUseCase(
    date_time=date_time,
    id_generator=id_generator,
    configuration={
        "langchain_thread_id": configuration.langchain_thread_id,
    },
)

get_conversation_messages_use_case = GetConversationMessagesUseCase(
    conversation_repository=conversation_repository
)


build_priced_investment_plan_use_case = BuildPricedInvestmentPlanUseCase(
    exchange=exchange,
    chain=chain,
    posting_repository=posting_repository,
    asset_balance_converter=asset_balance_converter,
)

execute_investment_plan_use_case = ExecuteInvestmentPlanUseCase(
    id_generator=id_generator,
    date_time=date_time,
    chain=chain,
    order_submitter=order_submitter,
    exchange=exchange,
    posting_repository=posting_repository,
    asset_balance_converter=asset_balance_converter,
)


get_asset_swap_price_use_case = GetAssetSwapPriceUseCase(
    chain=chain,
    posting_repository=posting_repository,
    asset_balance_converter=asset_balance_converter,
)


get_similar_assets_use_case = GetSimilarAssetsUseCase(similarity_storage)

get_all_baskets_use_case = GetAllBasketsUseCase(similarity_storage)

get_asset_by_id_use_case = GetAssetByIdUseCase(similarity_storage)

ingest_data_use_case = IngestDataUseCase(
    similarity_storage,
    data_sources=[
        CoingeckoLiveTokenListDataSource(
            id_generator,
            token_repository,
        ),
        Big4BasketDataSource(),
        AiBasketDataSource(),
        CmcTop102025BasketDataSource(),
        CryptoUmmahHalalBasketDataSource(),
        MemecoinManiaBasketDataSource(),
    ],
)

spec = APISpec(
    title=configuration.app_name,
    version="0.0.1",
    openapi_version="3.0.2",
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await nonce_manager.resync()
    await similarity_storage.start()

    if configuration.app_env != "test":
        await ingest_data_use_case.execute()

    print("API Ready.")

    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[configuration.frontend_url],
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST"],
    allow_headers=["*"],
)


class TokenRequest(BaseModel):
    id: str
    name: str
    display_name: str
    ticker: str
    address: str
    decimals: int
    categories: list[str]
    description: str
    logo_uri: str | None = None

    @staticmethod
    def from_domain(token: Token) -> "TokenRequest":
        """Convert a Token to a TokenRequest."""
        return TokenRequest(
            id=token.id,
            name=token.name,
            display_name=token.display_name,
            ticker=token.ticker,
            address=token.address,
            decimals=token.decimals,
            categories=token.categories,
            description=token.description,
            logo_uri=token.logo_uri,
        )

    def to_domain(self) -> Token:
        """Convert the request to a Token."""
        return Token(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            ticker=self.ticker,
            address=self.address,
            description=self.description,
            decimals=self.decimals,
            categories=self.categories,
            logo_uri=self.logo_uri,
        )


class BasketRequest(BaseModel):
    id: str
    name: str
    display_name: str
    ticker: str
    description: str
    denomination: str
    tokens: list[TokenRequest]

    @validator("tokens")
    @classmethod
    def at_least_one_token(cls, v):
        """Ensure at least one token in basket."""
        if not v or len(v) == 0:
            raise ValueError("At least one token must be provided.")
        return v

    def to_domain(self) -> Basket:
        """Convert the request to a Basket."""
        return Basket(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            ticker=self.ticker,
            description=self.description,
            denomination=Decimal(self.denomination),
            tokens=[token.to_domain() for token in self.tokens],
        )


AssetRequest = BasketRequest | TokenRequest


class ToolAssetRequest(BaseModel):
    asset: AssetRequest


@tool(parse_docstring=True)
async def get_tokens_from_query(query: str) -> list[TokenResponse | BasketResponse]:
    """
    Retrieve a list of available tokens to invest or from a given query.

    Args:
        query: The query to search for.

    Returns:
        A list of documents containing tokens.
        Each token has a name, display_name, ticker and address (contract address) property.
    """

    # TODO: Handle test case more elegantly
    if configuration.app_env == "test":
        return [
            TokenResponse.from_domain(wbnb_token),
            TokenResponse.from_domain(eth_token),
            TokenResponse.from_domain(btc_token),
            TokenResponse.from_domain(sol_token),
            TokenResponse.from_domain(shib_token),
            TokenResponse.from_domain(cake_token),
        ]

    assets = await get_similar_assets_use_case.execute(query, "TOKEN")

    return [
        (
            TokenResponse.from_domain(asset)
            if isinstance(asset, Token)
            else BasketResponse.from_domain(asset)
        )
        for asset in assets
    ]


@tool(parse_docstring=True)
async def get_baskets_from_query(query: str) -> list[TokenResponse | BasketResponse]:
    """
    Retrieve a list of available baskets from a given query.

    Args:
        query: The query to search for.

    Returns:
        A list of documents containing baskets.
        Each basket is made of a name, a description and a list of tokens.
        Each token has a name, display_name, ticker and address (contract address) property.
    """

    # TODO: Handle test case more elegantly
    if configuration.app_env == "test":
        return [
            BasketResponse.from_domain(big4_basket),
            BasketResponse.from_domain(memecoinmania_basket),
        ]

    assets = await get_similar_assets_use_case.execute(query, "BASKET")

    return [
        (
            TokenResponse.from_domain(asset)
            if isinstance(asset, Token)
            else BasketResponse.from_domain(asset)
        )
        for asset in assets
    ]


@tool(parse_docstring=True)
async def get_all_available_baskets():
    """
    Retrieve a list of all available baskets.

    Returns:
        A list of baskets.
        Each basket is made of a name, a description and a list of tokens.
        Each token has a name, display_name, ticker and address (contract address) property.
    """

    # TODO: Handle test case more elegantly
    if configuration.app_env == "test":
        return [big4_basket, memecoinmania_basket]

    baskets = await get_all_baskets_use_case.execute()

    return [BasketResponse.from_domain(basket) for basket in baskets]


@tool()
def get_agent_address():
    """Retrieve agent's current wallet address."""
    return chain.get_address()


@tool(
    parse_docstring=True,
)
async def get_portfolio_summary(
    conversion_token: TokenRequest = TokenRequest.from_domain(usdt_token),
):
    """EXPENSIVE/SLOW. Retrieve the portfolio. Only use this tool when the user asks for his portfolio.
    The portfolio contains the list of assets held by the agent (holdings) and their balances both in asset token and in converted token (defaults to USDT).
    It also contains the available cash balance in BNB and the list of pending (processing) orders.
    IMPORTANT: Do not call another tool if this returns results.

    Args:
        conversion_token: The token to convert the portfolio asset balances to (defaults to USDT).

    Returns:
        The portfolio of the agent.
    """

    return PortfolioResponse.from_domain(
        await get_portfolio_use_case.execute(conversion_token.to_domain())
    ).model_dump_json()


@tool(
    parse_docstring=True,
)
async def get_token_or_basket_or_asset_holding_and_available_cash(
    request: ToolAssetRequest,
):
    """FAST. Retrieve ONLY the available cash and holding of a specific asset (token or basket) in the agent's wallet, including both held balance and available balance.

    Args:
        request: An object containing a field token to retrieve the available cash and holding for.

    Returns:
        The the available cash and holding balances of the asset in the agent's wallet.
    """
    asset_balance = await get_portfolio_asset_balance_use_case.execute(
        request.asset.to_domain()
    )

    return PortfolioAssetBalanceResponse.from_domain(asset_balance).model_dump_json()


@tool(
    parse_docstring=True,
)
async def get_token_or_basket_or_asset_holding(request: ToolAssetRequest):
    """FAST. Retrieve ONLY the holding balance of a specific asset (token or basket).
    Use this tool when the user asks for his asset holding.

    Args:
        request: An object containing a field token to retrieve the available cash and holding for.

    Returns:
        The holding balance of the asset in the agent's wallet.
    """
    asset_domain = request.asset.to_domain()
    decimals = await chain.get_token_decimals(asset_domain.get_pricing_token().address)

    holding = await posting_repository.get_holding_balance(
        asset_domain
        if not chain.is_native_token(asset_domain)
        else chain.get_wrapped_base_token(),
        decimals,
    )

    return BalanceAtomicResponse.from_domain(holding.balance).model_dump_json()


@tool(
    parse_docstring=True,
)
async def get_available_cash():
    """FAST. Retrieve ONLY the available cash of the agent's wallet.

    Args: None

    Returns:
        The balance of the available cash (in BNB) in the agent's wallet.
    """
    balance = await chain.get_native_token_balance()

    return BalanceAtomicResponse.from_domain(balance).model_dump_json()


class BalanceAtomicResponse(BaseModel):
    asset: AssetResponse
    amount: str
    amount_atomic: str
    decimals: int

    @staticmethod
    def from_domain(balance: BalanceAtomic) -> "BalanceAtomicResponse":
        """Convert the domain Balance to a BalanceResponse."""
        return BalanceAtomicResponse(
            amount=format(balance.amount, "f"),
            amount_atomic=str(balance.amount_atomic),
            asset=TokenResponse.from_domain(balance.asset)
            if isinstance(balance.asset, Token)
            else BasketResponse.from_domain(balance.asset),
            decimals=balance.decimals,
        )


class ChainTransactionResponse(BaseModel):
    id: str
    try_id: str
    order_id: str
    type: ChainTransactionType
    data: str
    hash: str | None
    status: ChainTransactionStatus

    @staticmethod
    def from_domain(domain: ChainTransaction) -> "ChainTransactionResponse":
        return ChainTransactionResponse(
            id=domain.id,
            try_id=domain.try_id,
            order_id=domain.order_id,
            type=domain.type,
            data=domain.data,
            hash=domain.hash,
            status=domain.status,
        )


class FeesResponse(BaseModel):
    chain_fee: int
    provider_fee: int | None = None
    service_fee: int | None = None

    @staticmethod
    def from_domain(domain: Fees) -> "FeesResponse":
        return FeesResponse(
            chain_fee=domain.chain_fee,
            provider_fee=domain.provider_fee,
            service_fee=domain.service_fee,
        )


class TryResponse(BaseModel):
    id: str
    order_id: str
    created_at: int
    chain_transactions: list[ChainTransactionResponse]
    provider: str
    buy_balance: BalanceAtomicResponse
    fees: FeesResponse | None = None

    @staticmethod
    def from_domain(domain: Try) -> "TryResponse":
        return TryResponse(
            id=domain.id,
            order_id=domain.order_id,
            created_at=domain.created_at,
            chain_transactions=[
                ChainTransactionResponse.from_domain(tx)
                for tx in domain.chain_transactions
            ],
            provider=domain.provider,
            buy_balance=BalanceAtomicResponse.from_domain(domain.buy_balance),
            fees=FeesResponse.from_domain(domain.fees) if domain.fees else None,
        )


class OrderResponse(BaseModel):
    id: str
    sell_balance: BalanceAtomicResponse
    buy_balance: BalanceAtomicResponse
    type: OrderType
    # Don't return tries to lighten the response payload
    # tries: list[TryResponse]
    created_at: int
    status: OrderStatus
    trigger: OrderTrigger

    @staticmethod
    def from_domain(domain: Order) -> "OrderResponse":
        return OrderResponse(
            id=domain.id,
            sell_balance=BalanceAtomicResponse.from_domain(domain.sell_balance),
            buy_balance=BalanceAtomicResponse.from_domain(domain.buy_balance),
            type=domain.type,
            # tries=[TryResponse.from_domain(try_) for try_ in domain.tries],
            created_at=domain.created_at,
            status=domain.status,
            trigger=domain.trigger,
        )


class OrdersResponse(BaseModel):
    orders: list[OrderResponse]

    @classmethod
    def from_domain(cls, orders: list[Order]) -> "OrdersResponse":
        return cls(orders=[OrderResponse.from_domain(order) for order in orders])


@tool(
    parse_docstring=True,
)
async def get_orders(
    status: OrderStatus | None = None, limit: int = 50, offset: int = 0
):
    """SLOW / EXPENSIVE. Retrieve the orders from an eventual status and an eventual pagination

    Args:
        status: The status of the orders to retrieve, either "PENDING", "SUCCESS" or "FAIL". If not provided, all orders are retrieved.
        limit: The maximum number of orders to retrieve.
        offset: The offset for pagination.

    Returns:
        The list of orders matching the criteria.
    """
    orders = await order_repository.get_orders(status, limit, offset)

    return OrdersResponse.from_domain(orders).model_dump_json()


@tool(
    parse_docstring=True,
)
async def get_order(
    order_id: str,
):
    """FAST. Retrieve an order from its id

    Args:
        order_id: The id of the order to retrieve.

    Returns:
        The order matching the id or None if the order has not been found.
    """
    order = await order_repository.get_order(order_id)

    return OrderResponse.from_domain(order).model_dump_json() if order else None


@tool()
def get_current_datetime():
    """Retrieve current datetime."""
    return date_time.now_str()


class BalanceRequest(BaseModel):
    asset: AssetRequest
    amount: str

    def to_domain(self) -> Balance:
        """Convert the request to a Balance."""
        return Balance(
            asset=self.asset.to_domain(),
            amount=Decimal(self.amount),
        )


class InvestmentPlanStepRequest(BaseModel):
    buy_balance: BalanceRequest
    sell_balance: BalanceRequest

    def to_domain(self) -> InvestmentPlanStep:
        """Convert the request to an InvestmentPlanStep."""
        return InvestmentPlanStep(
            buy_balance=self.buy_balance.to_domain(),
            sell_balance=self.sell_balance.to_domain(),
        )


class InvestmentPlanRequest(BaseModel):
    status: Literal["CONFIRM", "CANCEL"]
    steps: list[InvestmentPlanStepRequest]

    def to_domain(self) -> InvestmentPlan:
        steps = [step.to_domain() for step in self.steps]
        return InvestmentPlan(steps=steps)


class IntentInvestmentPlanBalanceRequest(BaseModel):
    asset_id: str
    amount: str | None = None

    @validator("asset_id", pre=True)
    def normalize_asset_id(cls, v: Any):
        if not isinstance(v, str):
            return v
        # Always return lowercased, and if not bsc: prefix, use last part
        if v.startswith("bsc:"):
            return v.lower()
        return v.split(":")[-1].lower()

    async def to_domain(self):
        asset = None

        # TODO: Handle test case more elegantly
        if configuration.app_env == "test":
            asset = (
                btc_token
                if self.asset_id == "bsc:0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c"
                else memecoinmania_basket
            )

        elif self.asset_id == chain.base_token.id:
            asset = chain.base_token
        else:
            asset = await get_asset_by_id_use_case.execute(self.asset_id)

            if not asset:
                raise ValueError(f"Asset id {self.asset_id} not found")

        return IntentInvestmentPlanBalance(
            asset=asset,
            amount=Decimal(self.amount)
            if self.amount
            else None
            if self.amount is not None and self.amount != ""
            else None,
        )


class IntentInvestmentPlanStepRequest(BaseModel):
    buy_asset_with_amount: IntentInvestmentPlanBalanceRequest | None = None
    sell_asset_with_amount: IntentInvestmentPlanBalanceRequest | None = None

    @root_validator(pre=True)
    def at_least_one_asset(cls, values: dict[str, Any]):
        """
        Ensure at least one of buy_asset_with_amount or sell_asset_with_amount is provided.
        If asset_id is '' or 'None', set the corresponding field to None.
        """
        for field in ["buy_asset_with_amount", "sell_asset_with_amount"]:
            asset_req = values.get(field)
            if asset_req is not None:
                asset_id = getattr(asset_req, "asset_id", None)
                # Handle both dict and object cases
                if asset_id is None and isinstance(asset_req, dict):
                    asset_id = asset_req.get("asset_id")
                if asset_id == "" or asset_id == "None":
                    values[field] = None

        if not (
            values.get("buy_asset_with_amount") or values.get("sell_asset_with_amount")
        ):
            raise ValueError(
                "At least one of buy_asset_with_amount or sell_asset_with_amount must be provided."
            )
        return values

    async def to_domain(self):
        return IntentInvestmentPlanStep(
            buy_asset_with_amount=await self.buy_asset_with_amount.to_domain()
            if self.buy_asset_with_amount
            else None,
            sell_asset_with_amount=await self.sell_asset_with_amount.to_domain()
            if self.sell_asset_with_amount
            else None,
        )


class IntentInvestmentPlanRequest(BaseModel):
    steps: list[IntentInvestmentPlanStepRequest]

    async def to_domain(self) -> IntentInvestmentPlan:
        """Convert the IntentInvestmentPlan to a dictionary."""
        return IntentInvestmentPlan(
            steps=[await step.to_domain() for step in self.steps]
        )


class InvestmentPlanResponse(BaseModel):
    message: str
    orders: list[list[OrderResponse]]

    @staticmethod
    def from_domain(
        message: str, orders: list[list[Order]]
    ) -> "InvestmentPlanResponse":
        return InvestmentPlanResponse(
            message=message,
            orders=[
                [OrderResponse.from_domain(order) for order in order_group]
                for order_group in orders
            ],
        )


@tool(parse_docstring=True)
async def execute_intent_investment_plan_use_case(
    intent_investment_plan: IntentInvestmentPlanRequest,
):
    """Executes the intent investment plan.
    If no buy_asset, buy_asset_amount, sell_asset or sell_asset_amount is provided set the field to None.
    Pass asset_id as they are don't change them.
    IMPORTANT: You can make a swap by providing both a buy_asset_with_amount and a sell_asset_with_amount in the same step.
    IMPORTANT: You don't need to know the amount to buy or sell an asset in advance. You can leave the amount fields empty (set to None) and the agent will decide the amount to buy or sell based on the available cash and holdings.
    IMPORTANT: Do not call this tool more than once.
    IMPORTANT: Do not call another tool if this returns results.

    Args:
        intent_investment_plan (IntentInvestmentPlanRequest): The intent investment plan containing the assets to buy and/or sell eventually with their amounts for each step. A step can't have an amount defined if the related asset is not provided. A step can have an asset without an amount defined. A step can have a buy and sell asset defined.

    Returns:
        list[InvestmentPlanResponse]: A list of submitted orders for the assets in the investment plan. The list will be empty is user cancels the investment plan.

    Example:
        IntentInvestmentPlanRequest(
            steps=[
                IntentInvestmentPlanStepRequest(
                    buy_asset_with_amount=IntentInvestmentPlanBalanceRequest(
                        asset_id="2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
                        amount="5.33",
                    ),
                    sell_asset_with_amount=IntentInvestmentPlanBalanceRequest(
                        asset_id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                        amount="10.95",
                    ),
                ),
                IntentInvestmentPlanStepRequest(
                    buy_asset_with_amount=None,
                    sell_asset_with_amount=IntentInvestmentPlanBalanceRequest(
                        asset_id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                        amount=None,
                    ),
                ),
                IntentInvestmentPlanStepRequest(
                    buy_asset_with_amount=IntentInvestmentPlanBalanceRequest(
                        asset_id="bsc:0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                        amount="1028983",
                    ),
                    sell_asset_with_amount=None,
                ),
            ],
        )
    """

    priced_investment_plan = await build_priced_investment_plan_use_case.execute(
        await intent_investment_plan.to_domain()
    )

    investment_plan_as_dict = interrupt(
        {
            "ui": {
                "id": "prepare_investment_plan",
                "args": {
                    "priced_investment_plan": priced_investment_plan.to_dict(),
                },
            },
            "content": None,
        }
    )

    investment_plan = InvestmentPlanRequest.model_validate(
        investment_plan_as_dict["investment_plan"]
    )

    if investment_plan.status == "CANCEL":
        return InvestmentPlanResponse.from_domain(
            "Investment plan successfully cancelled by the user. Don't try to invest in the investment plan again.",
            [],
        ).model_dump_json()

    orders = await execute_investment_plan_use_case.execute(investment_plan.to_domain())

    return InvestmentPlanResponse.from_domain(
        "Investment plan and orders have been submitted successfully.", orders
    ).model_dump_json()


coinbasket_tools = [
    get_baskets_from_query,
    get_tokens_from_query,
    get_all_available_baskets,
    execute_intent_investment_plan_use_case,
    get_agent_address,
    get_available_cash,
    get_token_or_basket_or_asset_holding,
    get_token_or_basket_or_asset_holding_and_available_cash,
    get_portfolio_summary,
    get_orders,
    get_order,
    get_current_datetime,
]


class QueryMessageRequest(BaseModel):
    id: str
    is_resuming: bool
    role: Literal["user"]
    content: str
    created_at: Optional[str]


class PromptRequest(BaseModel):
    message: QueryMessageRequest
    app_key: str


class MessageUiResponse(BaseModel):
    id: str
    args: Dict[str, Any]


class MessageResponse(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    is_interrupting: bool
    ui: MessageUiResponse | None
    content: str | None
    created_at: Optional[str]

    @staticmethod
    def from_domain(message: Message) -> "MessageResponse":
        """Convert a Message to a MessageResponse."""
        return MessageResponse(
            id=message.id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
            is_interrupting=message.is_interrupting,
            ui=MessageUiResponse(id=message.ui.id, args=message.ui.args)
            if message.ui
            else None,
        )


@openapi(
    spec=spec,
    schemas=[QueryMessageRequest, PromptRequest, MessageUiResponse, MessageResponse],
    path="/conversation",
    operations={
        "post": {
            "summary": "Send message to the Agent",
            "tags": ["Conversation"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/PromptRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Agent response message",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/MessageResponse"},
                        }
                    },
                },
                "500": invalid_authentication_key,
            },
        }
    },
)
@app.post("/conversation")
@authentication(configuration.app_key)
async def conversation(req: PromptRequest) -> MessageResponse:
    async with aiosqlite.connect(langgraph_db_path) as conn:
        agent_executor = await __create_agent_executor(conn)

        message = await conversation_use_case.execute(
            agent_executor=agent_executor,
            message=QueryMessage(
                id=req.message.id,
                is_resuming=req.message.is_resuming,
                role=req.message.role,
                content=req.message.content,
                created_at=req.message.created_at or date_time.now_str(),
            ),
        )

    return MessageResponse.from_domain(message)


async def __create_agent_executor(conn: aiosqlite.Connection):
    sqlite_memory = AsyncSqliteSaver(conn)

    mcp_clients_tools = []
    # mcp_clients_tools = await mcp_clients.get_tools()

    agent_executor = create_react_agent(
        init_chat_model(
            model=configuration.chat_model,
            model_provider=configuration.chat_provider,
            api_key=configuration.chat_provider_api_key,
            reasoning={"effort": "minimal"},
        ),
        tools=coinbasket_tools + mcp_clients_tools,
        checkpointer=sqlite_memory,
        prompt=SystemMessage(
            "\n".join(
                [
                    "Your goal is to manage a portfolio made of assets. An asset is either a token or a basket of tokens.  ",
                    "Users can buy, sell, or swap assets in their portfolio.  ",
                    "Before buying, selling or swapping assets, ALWAYS show the user the intent investment plan you are creating by showing the list of assets to buy, sell or swap.  ",
                    "When you display a token, ALWAYS display its display name, ticker and address by using this link 'https://bscscan.com/token/[token_address]'. Don't use a link when displaying a basket.  ",
                    "ALWAYS use a tool to fetch a token address when you need it.  ",
                    "ALWAYS display amount with 4 decimals, don't use scientific notation.  ",
                    "When asked for token, portfolio, order, asset or balance information, ALWAYS use a tool to fetch the data.  ",
                    "When an order has a status 'PENDING', it means the order is being processed.  ",
                    "After each answer, ask the user if he wants to add or remove any asset from the portfolio or if he wants to proceed.  ",
                    "Formatting re-enabled — please use Markdown **bold**, links and header tags to **improve the readability** of your responses.",
                    "Consider all tool parameters optional unless explicitly stated otherwise.",
                    "If you don't know the answer, just say that you don't know and mention what you can do, don't try to make up an answer.  ",
                ]
            )
        ),
    )

    return agent_executor


class MessagesRequest(BaseModel):
    app_key: str


class MessagesResponse(BaseModel):
    messages: list[MessageResponse]

    @staticmethod
    def from_domain(messages: list[Message]) -> "MessagesResponse":
        """Convert a list of Message domain objects to a MessagesResponse."""
        return MessagesResponse(
            messages=[MessageResponse.from_domain(message) for message in messages]
        )


@openapi(
    spec=spec,
    schemas=[MessagesRequest],
    path="/conversation/messages",
    operations={
        "post": {
            "summary": "Get Agent messages history",
            "tags": ["Conversation"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/MessagesRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Agent message history",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/MessageResponse"
                                },
                            },
                        }
                    },
                },
                "500": invalid_authentication_key,
            },
        }
    },
)
@app.post("/conversation/messages")
@authentication(configuration.app_key)
async def get_conversation_messages(
    _req: MessagesRequest,
) -> MessagesResponse:
    """Retrieve the conversation messages."""
    async with aiosqlite.connect(langgraph_db_path) as conn:
        agent_executor = await __create_agent_executor(conn)

        messages = await get_conversation_messages_use_case.execute(
            thread_id=configuration.langchain_thread_id, agent_executor=agent_executor
        )

        return MessagesResponse.from_domain(messages)


class AssetSwapPriceInfoRequest(BaseModel):
    app_key: str
    sell_asset: TokenRequest | BasketRequest
    sell_asset_amount: str
    buy_asset: TokenRequest | BasketRequest

    def to_domain(self) -> AssetSwapPriceInfo:
        """Convert the request to an AssetSwapPriceInfo."""
        return AssetSwapPriceInfo(
            sell_asset=self.sell_asset.to_domain(),
            sell_asset_amount=Decimal(self.sell_asset_amount),
            buy_asset=self.buy_asset.to_domain(),
        )


class BalanceResponse(BaseModel):
    amount: str
    asset: AssetResponse

    @staticmethod
    def from_domain(balance: Balance) -> "BalanceResponse":
        """Convert the domain Balance to a BalanceResponse."""
        return BalanceResponse(
            amount=format(balance.amount, "f"),
            asset=TokenResponse.from_domain(balance.asset)
            if isinstance(balance.asset, Token)
            else BasketResponse.from_domain(balance.asset),
        )


class ConvertedBalanceResponse(BaseModel):
    sell_balance: BalanceResponse
    buy_balance: BalanceResponse

    @staticmethod
    def from_domain(
        converted_balance: ConvertedBalance,
    ) -> "ConvertedBalanceResponse":
        return ConvertedBalanceResponse(
            sell_balance=BalanceResponse.from_domain(converted_balance.sell_balance),
            buy_balance=BalanceResponse.from_domain(converted_balance.buy_balance),
        )


@openapi(
    spec=spec,
    schemas=[
        AssetSwapPriceInfoRequest,
        TokenResponse,
        BasketResponse,
        BalanceResponse,
        ConvertedBalanceResponse,
    ],
    path="/asset/swap/price",
    operations={
        "post": {
            "summary": "Get price for asset swap",
            "tags": ["Asset"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/AssetSwapPriceInfoRequest"
                        }
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Asset swap price information",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ConvertedBalanceResponse"
                            }
                        }
                    },
                },
                "500": invalid_authentication_key,
            },
        }
    },
)
@app.post(
    "/asset/swap/price",
)
@authentication(configuration.app_key)
async def get_asset_swap_price(req: AssetSwapPriceInfoRequest):
    """Test authentication to the Agent."""

    converted_balance = await get_asset_swap_price_use_case.execute(req.to_domain())

    return ConvertedBalanceResponse.from_domain(converted_balance)


class AuthRequest(BaseModel):
    app_key: str


class AuthResponse(BaseModel):
    status: str


@openapi(
    spec=spec,
    schemas=[AuthRequest, AuthResponse],
    path="/auth",
    operations={
        "post": {
            "summary": "Test authentication to the Agent",
            "tags": ["Authentication"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AuthRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Authentication status",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AuthResponse"}
                        }
                    },
                },
                "500": invalid_authentication_key,
            },
        }
    },
)
@app.post("/auth")
@authentication(configuration.app_key)
async def auth_request(_req: AuthRequest) -> AuthResponse:
    return AuthResponse(status="OK")


class HealthResponse(BaseModel):
    status: str


@openapi(
    spec=spec,
    schemas=[HealthResponse],
    path="/health",
    operations={
        "get": {
            "summary": "Get agent health",
            "tags": ["Health"],
            "responses": {
                "200": {
                    "description": "Agent health status",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/HealthResponse"}
                        }
                    },
                }
            },
        }
    },
)
@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="OK")


class PortfolioRequest(BaseModel):
    app_key: str
    token: TokenRequest

    def to_domain(self):
        return Token(
            id=self.token.id,
            name=self.token.name,
            display_name=self.token.display_name,
            ticker=self.token.ticker,
            address=self.token.address,
            decimals=self.token.decimals,
            categories=self.token.categories,
            description=self.token.description,
        )


class PortfolioBalanceResponse(BaseModel):
    native_balance: BalanceAtomicResponse
    converted_balance: BalanceAtomicResponse

    @staticmethod
    def from_domain(domain: PortfolioBalance) -> "PortfolioBalanceResponse":
        return PortfolioBalanceResponse(
            native_balance=BalanceAtomicResponse.from_domain(domain.native_balance),
            converted_balance=BalanceAtomicResponse.from_domain(
                domain.converted_balance
            ),
        )


class PortfolioResponse(BaseModel):
    available_balance: PortfolioBalanceResponse
    holding_balances: list[PortfolioBalanceResponse]
    total_balance: BalanceAtomicResponse
    pending_orders: list[OrderResponse]

    @staticmethod
    def from_domain(domain: Portfolio) -> "PortfolioResponse":
        return PortfolioResponse(
            available_balance=PortfolioBalanceResponse.from_domain(
                domain.available_balance
            ),
            holding_balances=[
                PortfolioBalanceResponse.from_domain(balance)
                for balance in domain.holding_balances
            ],
            total_balance=BalanceAtomicResponse.from_domain(domain.total_balance),
            pending_orders=[
                OrderResponse.from_domain(order) for order in domain.pending_orders
            ],
        )


class PortfolioAssetBalanceResponse(BaseModel):
    holding_balance: BalanceAtomicResponse
    available_balance: BalanceAtomicResponse | None = None

    @staticmethod
    def from_domain(domain: PortfolioAssetBalance) -> "PortfolioAssetBalanceResponse":
        return PortfolioAssetBalanceResponse(
            holding_balance=BalanceAtomicResponse.from_domain(domain.holding_balance),
            available_balance=BalanceAtomicResponse.from_domain(
                domain.available_balance
            )
            if domain.available_balance
            else None,
        )


@openapi(
    spec=spec,
    schemas=[
        TokenRequest,
        OrderResponse,
        FeesResponse,
        ChainTransactionResponse,
        TryResponse,
        BalanceAtomicResponse,
        PortfolioBalanceResponse,
        PortfolioRequest,
        PortfolioResponse,
    ],
    path="/portfolio",
    operations={
        "post": {
            "summary": "Get Agent Portfolio in a specific token",
            "tags": ["Portfolio"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/PortfolioRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Agent Portfolio in the specified token",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/PortfolioResponse"
                                },
                            },
                        }
                    },
                },
                "500": invalid_authentication_key,
            },
        }
    },
)
@app.post("/portfolio")
@authentication(configuration.app_key)
async def get_converted_portfolio(req: PortfolioRequest):
    converted_token_balances = await get_portfolio_use_case.execute(req.to_domain())

    return PortfolioResponse.from_domain(converted_token_balances)


class OpenApiResponse(RootModel[dict[str, Any]]):
    pass


@openapi(
    spec=spec,
    schemas=[OpenApiResponse],
    path="/openapi",
    operations={
        "get": {
            "summary": "Generate JSON OpenAPI documentation",
            "tags": ["Documentation"],
            "responses": {
                "200": {
                    "description": "JSON OpenAPI documentation",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/OpenApiResponse"},
                        }
                    },
                },
            },
        }
    },
)
@app.get("/openapi")
async def generate_openapi_documentation():
    return cast(OpenApiResponse, spec.to_dict())
