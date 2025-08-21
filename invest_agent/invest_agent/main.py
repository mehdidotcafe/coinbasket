from decimal import Decimal
import os
from typing import Any, Dict, Literal, Optional, cast

import aiosqlite
from invest_agent.asset.get_asset_swap_price_use_case import (
    AssetSwapPriceInfo,
    GetAssetSwapPriceUseCase,
    ConvertedBalance,
)
from invest_agent.chain.infrastructure.bsc.transaction_receipt_parser import (
    BscTransactionReceiptParser,
)
from invest_agent.investment.fees import Fees
from invest_agent.investment.investment_parameters import InvestmentParameters
from invest_agent.investment.investment_planner.intent_investment_plan import (
    IntentInvestmentPlan,
    IntentInvestmentPlanStep,
    IntentInvestmentPlanBalance,
)
from invest_agent.investment.investment_planner.investment_plan import (
    InvestmentPlan,
    InvestmentPlanStep,
)
from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    SqlAlchemyOrderRepository,
)
from invest_agent.investment.order.order import (
    ChainTransaction,
    ChainTransactionStatus,
    ChainTransactionType,
    Order,
    OrderStatus,
    OrderTrigger,
    OrderType,
    Try,
)
from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    SqlAlchemyTransactionRepository,
)
from invest_agent.portfolio.get_portfolio_use_case import (
    GetPortfolioUseCase,
    Portfolio,
    PortfolioBalance,
)
from invest_agent.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    SqlAlchemyPostingRepository,
)
from protocol.basket import Basket
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from apispec import APISpec
from invest_agent.authentication.authentication import authentication
from invest_agent.chain.balance import Balance, BalanceAtomic
from invest_agent.conversation.get_conversation_messages_use_case import (
    GetConversationMessagesUseCase,
)
from invest_agent.conversation.message import Message, QueryMessage
from invest_agent.conversation.repository.infrastructure.langchain_sqlite_conversation_repository import (
    LangchainSqliteConversationRepository,
)
from invest_agent.datetime.infrastructure.python_date_time import PythonDateTime
from invest_agent.documentation.response.invalid_authentication_key import (
    invalid_authentication_key,
)
from invest_agent.http.agent_to_agent.infrastructure.aiohttp_agent_to_agent_client import (
    AiohttpAgentToAgentClient,
)
from invest_agent.conversation.conversation_use_case import ConversationUseCase
from invest_agent.chain.infrastructure.bsc.nonce_manager import NonceManager
from invest_agent.investment.execute_pending_orders_use_case import (
    ExecutePendingOrdersUseCase,
)
from invest_agent.investment.execute_investment_plan_use_case import (
    ExecuteInvestmentPlanUseCase,
)
from invest_agent.investment.order.order_submitter import OrderSubmitter
from shared.http_request.infrastructure.aiohttp_http_request import AiohttpHttpRequest
from shared.http_request.infrastructure.requests_http_request import RequestsHttpRequest
from shared.id_generator.id_generator import IdGenerator
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_swapper import ZeroXSwapper

from invest_agent.documentation.openapi import openapi
from protocol.token import Token
from pydantic import RootModel
from pydantic.v1 import root_validator, validator
from uagents import Agent, Context, Model
from uagents.storage import KeyValueStore

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from web3 import AsyncWeb3, AsyncHTTPProvider

from invest_agent.chain.infrastructure.bsc.bsc_chain import BscChain
from invest_agent.chain.infrastructure.bsc.bsc_contract import BscContract
from invest_agent.configuration import Configuration
from invest_agent.infrastructure.fetch_ai.storage.fetch_ai_storage import (
    FetchAiStorage,
)

from protocol import (
    AssetResponse,
    BasketResponse,
    SimilarAssetsQuery,
    SimilarAssetsResponse,
    TokenResponse,
)
from protocol.fixture.token import usdt_token

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.types import interrupt


date_time = PythonDateTime()


configuration = Configuration()

print(f"Thread ID: {configuration.langchain_thread_id}")


if configuration.langsmith_tracing:
    os.environ["LANGSMITH_TRACING"] = str(configuration.langsmith_tracing)
    os.environ["LANGSMITH_API_KEY"] = configuration.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = configuration.langsmith_project


spec = APISpec(
    title=configuration.agent_name,
    version="0.0.1",
    openapi_version="3.0.2",
)

invest_agent = Agent(
    name=configuration.agent_name,
    seed=configuration.agent_seed,
    port=configuration.agent_port,
    endpoint=f"http://localhost:{configuration.agent_port}/submit",
)
w3 = AsyncWeb3(AsyncHTTPProvider(configuration.bsc_rpc_url))

nonce_manager = NonceManager(
    w3=w3,
    configuration={
        "private_key": configuration.bsc_private_key,
    },
)
transaction_receipt_parser = BscTransactionReceiptParser(w3=w3)

chain = BscChain(
    w3=w3,
    nonce_manager=nonce_manager,
    private_key=configuration.bsc_private_key,
    transaction_receipt_parser=transaction_receipt_parser,
)

contract = BscContract(w3=w3)

requests_http_request = RequestsHttpRequest()

aiohttp_http_request = AiohttpHttpRequest()

id_generator = IdGenerator()

api_client = ZeroXApiClient(
    configuration={
        "zero_x_api_url": configuration.zero_x_api_url,
        "zero_x_api_key": configuration.zero_x_api_key,
    },
    http_request=requests_http_request,
)

exchange = ZeroXSwapper(
    api_client=api_client,
    chain=chain,
    contract=contract,
    w3=w3,
    configuration={
        "bsc_rpc_url": configuration.bsc_rpc_url,
        "private_key": configuration.bsc_private_key,
    },
)
storage = FetchAiStorage[Any](
    configuration.langchain_thread_id,
    store=KeyValueStore(configuration.agent_name, "./database"),
)
agent_to_agent_client = AiohttpAgentToAgentClient(
    configuration={"agent_url": configuration.data_agent_url},
    aiohttp_http_request=aiohttp_http_request,
)

db_path = f"./database/{configuration.agent_env}/{configuration.agent_name}.db"
langgraph_db_path = (
    f"./database/{configuration.agent_env}/{configuration.agent_name}.langgraph.db"
)

engine = create_async_engine(
    f"postgresql+asyncpg://{configuration.database_user}:{configuration.database_password}@{configuration.database_host}:{configuration.database_port}/{configuration.agent_name}",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
AsyncSessionLocal = cast(
    type[AsyncSession], sessionmaker(expire_on_commit=False, class_=AsyncSession)
)

order_repository = SqlAlchemyOrderRepository(
    AsyncSessionLocal=AsyncSessionLocal, engine=engine
)
transaction_repository = SqlAlchemyTransactionRepository(
    AsyncSessionLocal=AsyncSessionLocal, engine=engine
)
posting_repository = SqlAlchemyPostingRepository(
    AsyncSessionLocal=AsyncSessionLocal, engine=engine
)


get_portfolio_use_case = GetPortfolioUseCase(
    order_repository=order_repository,
    posting_repository=posting_repository,
    exchange=exchange,
    chain=chain,
)

conversation_use_case = ConversationUseCase(
    date_time=date_time,
    id_generator=id_generator,
    configuration={
        "langchain_thread_id": configuration.langchain_thread_id,
    },
)

conversation_repository = LangchainSqliteConversationRepository(
    db_path=langgraph_db_path, date_time=date_time, id_generator=id_generator
)

get_conversation_messages_use_case = GetConversationMessagesUseCase(
    conversation_repository=conversation_repository
)

order_submitter = OrderSubmitter(
    chain=chain,
    exchange=exchange,
    id_generator=id_generator,
    date_time=date_time,
    order_repository=order_repository,
    transaction_repository=transaction_repository,
    posting_repository=posting_repository,
)

execute_investment_plan_use_case = ExecuteInvestmentPlanUseCase(
    id_generator=id_generator,
    date_time=date_time,
    chain=chain,
    order_submitter=order_submitter,
    exchange=exchange,
)
execute_pending_orders_use_case = ExecutePendingOrdersUseCase(
    order_submitter=order_submitter,
    order_repository=order_repository,
)


get_asset_swap_price_use_case = GetAssetSwapPriceUseCase(exchange=exchange, chain=chain)


@tool(response_format="content_and_artifact")
async def get_token_info(query: str):
    """
    Retrieve a list of available tokens / coins to invest or.

    Args:
        query: The query to search for.

    Returns:
        A list of documents containing tokens / coins.
        Each token has a name, display_name, ticker and address (contract address) property.
    """

    # TODO: Use fetch ai send_and_receive when fixed with multiple concurrent requests
    res = await agent_to_agent_client.send_and_receive_message(
        SimilarAssetsQuery(
            query=f"{query} type: token", agent_key=configuration.data_agent_key
        ),
        SimilarAssetsResponse,
    )

    if isinstance(res.data, str):
        raise ValueError(f"Response is not a valid response: {res.data}")

    return "\n\n".join(
        [str(asset.to_domain()) for asset in res.data.assets]
    ), res.data.assets


@tool(response_format="content_and_artifact")
async def get_basket_info(query: str):
    """
    Retrieve a list of available baskets.

    Args:
        query: The query to search for.

    Returns:
        A list of documents containing baskets.
        Each basket is made of a name, a description and a list of tokens.
        Each token has a name, display_name, ticker and address (contract address) property.
    """

    # TODO: Use fetch ai send_and_receive when fixed with multiple concurrent requests
    res = await agent_to_agent_client.send_and_receive_message(
        SimilarAssetsQuery(
            query=f"{query} type: basket", agent_key=configuration.data_agent_key
        ),
        SimilarAssetsResponse,
    )

    if isinstance(res.data, str):
        raise ValueError(f"Response is not a valid response: {res.data}")

    return "\n\n".join(
        [str(asset.to_domain()) for asset in res.data.assets]
    ), res.data.assets


@tool()
def get_agent_address():
    """Retrieve agent's current wallet address."""
    return chain.get_address()


@tool()
def get_invested_basket():
    """Retrieve the invested basket in native value only.

    Returns:
        The invested basket made of the bids that were made by the agent when investing in the basket.
        Each bid has a token and a balance_in and balance_out property.
        The token has a name, display_name, ticker and address (contract address) property.
    """
    return None


@tool()
async def get_portfolio_tool(token: Token = usdt_token):
    """Retrieve the portfolio."""
    return await get_portfolio_use_case.execute(token)


@tool()
async def get_token_balance(token: Token):
    """Retrieve the balance of a specific token in the agent's wallet.

    Args:
        token: The token to retrieve the balance for.

    Returns:
        The balance of the token in the agent's wallet.
    """
    balance = await chain.get_token_balance(token)

    return balance


@tool()
async def get_available_balance():
    """Retrieve the available balance.

    Returns:
        The balance of the token in the agent's wallet.
    """
    balance = await chain.get_native_token_balance()

    return balance


@tool()
def get_agent_name():
    """Retrieve agent's name."""
    return configuration.agent_name


@tool()
def get_current_datetime():
    """Retrieve current datetime."""
    return date_time.now_str()


class TokenRequest(Model):
    id: str
    name: str
    display_name: str
    ticker: str
    address: str

    def to_domain(self) -> Token:
        """Convert the request to a Token."""
        return Token(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            ticker=self.ticker,
            address=self.address,
        )


class BasketRequest(Model):
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


class BalanceRequest(Model):
    asset: AssetRequest
    amount: str

    def to_domain(self) -> Balance:
        """Convert the request to a Balance."""
        return Balance(
            asset=self.asset.to_domain(),
            amount=Decimal(self.amount),
        )


class InvestmentPlanStepRequest(Model):
    buy_balance: BalanceRequest
    sell_balance: BalanceRequest

    def to_domain(self) -> InvestmentPlanStep:
        """Convert the request to an InvestmentPlanStep."""
        return InvestmentPlanStep(
            buy_balance=self.buy_balance.to_domain(),
            sell_balance=self.sell_balance.to_domain(),
        )


class InvestmentPlanRequest(Model):
    status: Literal["CONFIRM", "CANCEL"]
    steps: list[InvestmentPlanStepRequest]

    def to_domain(self) -> InvestmentPlan:
        steps = [step.to_domain() for step in self.steps]
        return InvestmentPlan(steps=steps)


class IntentInvestmentPlanBalanceRequest(Model):
    asset: AssetRequest
    amount: str | None = None

    def to_domain(self):
        return IntentInvestmentPlanBalance(
            asset=self.asset.to_domain(),
            amount=Decimal(self.amount)
            if self.amount is not None and self.amount != ""
            else None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the IntentInvestmentPlanBalance to a dictionary."""
        return {
            "asset": self.asset.to_domain().to_dict(),
            "amount": str(self.amount) if self.amount is not None else None,
        }


class IntentInvestmentPlanStepRequest(Model):
    buy_asset_with_amount: IntentInvestmentPlanBalanceRequest | None = None
    sell_asset_with_amount: IntentInvestmentPlanBalanceRequest | None = None

    @root_validator(pre=True)
    def at_least_one_asset(cls, values: dict[str, Any]):
        """Ensure at least one of buy_asset_with_amount or sell_asset_with_amount is provided."""
        if not (
            values.get("buy_asset_with_amount") or values.get("sell_asset_with_amount")
        ):
            raise ValueError(
                "At least one of buy_asset_with_amount or sell_asset_with_amount must be provided."
            )

        return values

    def to_domain(self):
        return IntentInvestmentPlanStep(
            buy_asset_with_amount=self.buy_asset_with_amount.to_domain()
            if self.buy_asset_with_amount
            else None,
            sell_asset_with_amount=self.sell_asset_with_amount.to_domain()
            if self.sell_asset_with_amount
            else None,
        )


class IntentInvestmentPlanRequest(Model):
    steps: list[IntentInvestmentPlanStepRequest]

    def to_domain(self) -> IntentInvestmentPlan:
        """Convert the IntentInvestmentPlan to a dictionary."""
        return IntentInvestmentPlan(steps=[step.to_domain() for step in self.steps])


# TODO: Handle basket
async def _fill_intent_investment_plan_with_default(
    intent_investment_plan: IntentInvestmentPlan,
):
    steps: list[IntentInvestmentPlanStep] = []

    for step in intent_investment_plan.steps:
        sell_asset = (
            step.sell_asset_with_amount.asset
            if step.sell_asset_with_amount
            else chain.get_base_token()
        )
        sell_token = sell_asset.get_pricing_token()

        buy_asset = (
            step.buy_asset_with_amount.asset
            if step.buy_asset_with_amount
            else chain.get_base_token()
        )
        buy_token = buy_asset.get_pricing_token()

        if sell_asset == buy_asset:
            continue

        if step.sell_asset_with_amount and step.sell_asset_with_amount.amount:
            sell_amount = (
                step.sell_asset_with_amount.amount * sell_asset.get_denomination()
            )

            (
                sell_balance_amount_atomic,
                sell_balance_decimals,
            ) = await chain.convert_amount_to_amount_atomic(
                token=sell_token,
                amount_readable=sell_amount,
            )
            sell_balance = BalanceAtomic[Token](
                asset=sell_token,
                amount=sell_amount,
                amount_atomic=sell_balance_amount_atomic,
                decimals=sell_balance_decimals,
            )

            converted_balance = await exchange.convert_balance_to_token(
                balance=sell_balance,
                token=buy_token,
                investment_parameters=InvestmentParameters(
                    slippage_tolerance_in_percentage=Decimal(1)
                ),
            )

            steps.append(
                IntentInvestmentPlanStep(
                    sell_asset_with_amount=IntentInvestmentPlanBalance(
                        asset=sell_asset,
                        amount=converted_balance.sell_balance.amount
                        / sell_asset.get_denomination(),
                    ),
                    buy_asset_with_amount=IntentInvestmentPlanBalance(
                        asset=buy_asset,
                        amount=converted_balance.buy_balance.amount
                        / buy_asset.get_denomination(),
                    ),
                )
            )
            continue

        if step.buy_asset_with_amount and step.buy_asset_with_amount.amount:
            buy_token_amount = (
                step.buy_asset_with_amount.amount * buy_asset.get_denomination()
            )
            (
                buy_balance_amount_atomic,
                buy_balance_decimals,
            ) = await chain.convert_amount_to_amount_atomic(
                token=buy_token,
                amount_readable=buy_token_amount,
            )
            buy_balance = BalanceAtomic[Token](
                asset=buy_token,
                amount=buy_token_amount,
                amount_atomic=buy_balance_amount_atomic,
                decimals=buy_balance_decimals,
            )

            converted_balance = await exchange.convert_balance_to_token(
                balance=buy_balance,
                token=sell_token,
                investment_parameters=InvestmentParameters(
                    slippage_tolerance_in_percentage=Decimal(1)
                ),
            )

            steps.append(
                IntentInvestmentPlanStep(
                    sell_asset_with_amount=IntentInvestmentPlanBalance(
                        asset=sell_asset,
                        amount=converted_balance.buy_balance.amount
                        / sell_asset.get_denomination(),
                    ),
                    buy_asset_with_amount=IntentInvestmentPlanBalance(
                        asset=buy_asset,
                        amount=converted_balance.sell_balance.amount
                        / buy_asset.get_denomination(),
                    ),
                )
            )
            continue

        if step.sell_asset_with_amount:
            steps.append(
                IntentInvestmentPlanStep(
                    sell_asset_with_amount=IntentInvestmentPlanBalance(
                        asset=sell_asset, amount=step.sell_asset_with_amount.amount
                    ),
                    buy_asset_with_amount=IntentInvestmentPlanBalance(
                        asset=buy_asset,
                        amount=step.buy_asset_with_amount.amount
                        if step.buy_asset_with_amount
                        else None,
                    ),
                )
            )
            continue

        if step.buy_asset_with_amount:
            steps.append(
                IntentInvestmentPlanStep(
                    sell_asset_with_amount=IntentInvestmentPlanBalance(
                        asset=sell_asset,
                        amount=step.sell_asset_with_amount.amount
                        if step.sell_asset_with_amount
                        else None,
                    ),
                    buy_asset_with_amount=IntentInvestmentPlanBalance(
                        asset=buy_asset,
                        amount=step.buy_asset_with_amount.amount,
                    ),
                )
            )
            continue

    # If no sell_asset and buy_asset is provided we don't include the step for now
    return IntentInvestmentPlan(
        steps=steps,
    )


@tool(
    parse_docstring=True,
)
async def invest_in_intent_investment_plan_use_case(
    intent_investment_plan: IntentInvestmentPlanRequest,
) -> dict[str, Any]:
    """Invest in the intent investment plan.

    Args:
        intent_investment_plan (IntentInvestmentPlanRequest): The intent investment plan containing the assets to buy and/or sell eventually with their amounts for each step. A step can't have an amount defined if the related asset is not provided. A step can have an asset without an amount defined. A step can have a buy and sell asset defined.

    Returns:
        list[Order]: A list of submitted orders for the assets in the investment plan.

    Example:
        IntentInvestmentPlanRequest(
            steps=[
                IntentInvestmentPlanStepRequest(
                    buy_asset=AssetRequest(
                        id="bsc:0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                        name="Binance Pegged Ethereum",
                        display_name="Ethereum",
                        ticker="ETH",
                        address="0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
                    ),
                    buy_asset_amount="5.33",
                    sell_asset=AssetRequest(
                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                        name="Binance Coin",
                        display_name="Binance Coin",
                        ticker="BNB",
                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeEEeE",
                    ),
                    sell_asset_amount="10.95",
                ),
                IntentInvestmentPlanStepRequest(
                    buy_asset=None,
                    buy_asset_amount=None,
                    sell_asset=AssetRequest(
                        id="bsc:0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                        name="Binance Coin",
                        display_name="Binance Coin",
                        ticker="BNB",
                        address="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeEEeE",
                    ),
                    sell_asset_amount=None,
                ),
                IntentInvestmentPlanStepRequest(
                    buy_asset=AssetRequest(
                        id="bsc:0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                        name="Dogecoin",
                        display_name="Dogecoin",
                        ticker="DOGE",
                        address="0xbA2aE424d960c26247Dd6c32edC70B295c744C43",
                    ),
                    buy_asset_amount="1028983",
                    sell_asset=None,
                    sell_asset_amount=None,
                ),
            ],
        )
    """

    filled_intent_investment_plan = await _fill_intent_investment_plan_with_default(
        intent_investment_plan.to_domain()
    )

    print(f"filled_intent_investment_plan: {filled_intent_investment_plan}")

    investment_plan_as_dict = interrupt(
        {
            "ui": {
                "id": "prepare_investment_plan",
                "args": {
                    "intent_investment_plan": filled_intent_investment_plan.to_dict(),
                },
            },
            "content": None,
        }
    )

    investment_plan = InvestmentPlanRequest.model_validate(
        investment_plan_as_dict["investment_plan"]
    )

    if investment_plan.status == "CANCEL":
        return {
            "message": "Investment plan successfully cancelled by the user.",
        }

    orders = await execute_investment_plan_use_case.execute(investment_plan.to_domain())

    return {
        "message": "Orders have been submitted successfully.",
        "orders": orders,
    }


tools = [
    get_basket_info,
    get_token_info,
    invest_in_intent_investment_plan_use_case,
    get_agent_address,
    get_available_balance,
    get_token_balance,
    get_portfolio_tool,
    get_agent_name,
    get_current_datetime,
]


@invest_agent.on_event("startup")
async def on_startup(_ctx: Context):
    await nonce_manager.resync()
    await execute_pending_orders_use_case.execute()


class QueryMessageRequest(Model):
    id: str
    is_resuming: bool
    role: Literal["user"]
    content: str
    created_at: Optional[str]


class PromptRequest(Model):
    message: QueryMessageRequest
    agent_key: str


class MessageUiResponse(Model):
    id: str
    args: Dict[str, Any]


class MessageResponse(Model):
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
@invest_agent.on_rest_post("/conversation", PromptRequest, MessageResponse)
@authentication(configuration.agent_key)
async def conversation(_ctx: Context, req: PromptRequest) -> MessageResponse:
    async with aiosqlite.connect(langgraph_db_path) as conn:
        agent_executor = __create_agent_executor(conn)

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


def __create_agent_executor(conn: aiosqlite.Connection):
    sqlite_memory = AsyncSqliteSaver(conn)

    agent_executor = create_react_agent(
        init_chat_model(
            model=configuration.chat_model,
            model_provider=configuration.chat_provider,
            api_key=configuration.chat_provider_api_key,
        ),
        tools,
        checkpointer=sqlite_memory,
        prompt=SystemMessage(
            "Your goal is to manage a portfolio made of assets. An asset is either a token or a basket of tokens.  "
            "Users can buy, sell, or swap assets in their portfolio.  "
            "Before buying, selling or swapping assets, always show the user the intent investment plan you are creating by showing the list of assets to buy, sell or swap.  "
            "When you display a token, always display its display name, ticker and address by using this link 'https://bscscan.com/token/[token_address]'. Don't mention excluded assets.  "
            "After each answer, ask the user if he wants to add or remove any asset from the portfolio or if he wants to proceed.  "
            "If you don't know the answer, just say that you don't know and mention what you can do, don't try to make up an answer.  "
        ),
    )

    return agent_executor


class MessagesRequest(Model):
    agent_key: str


class MessagesResponse(Model):
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
@invest_agent.on_rest_post("/conversation/messages", MessagesRequest, MessagesResponse)
@authentication(configuration.agent_key)
async def get_conversation_messages(
    _ctx: Context,
    _req: MessagesRequest,
) -> MessagesResponse:
    """Retrieve the conversation messages."""
    async with aiosqlite.connect(langgraph_db_path) as conn:
        agent_executor = __create_agent_executor(conn)

        messages = await get_conversation_messages_use_case.execute(
            thread_id=configuration.langchain_thread_id, agent_executor=agent_executor
        )

        return MessagesResponse.from_domain(messages)


class AssetSwapPriceInfoRequest(Model):
    agent_key: str
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


class BalanceResponse(Model):
    amount: str
    asset: AssetResponse

    @staticmethod
    def from_domain(balance: Balance) -> "BalanceResponse":
        """Convert the domain Balance to a BalanceResponse."""
        return BalanceResponse(
            amount=str(balance.amount),
            asset=TokenResponse.from_domain(balance.asset)
            if isinstance(balance.asset, Token)
            else BasketResponse.from_domain(balance.asset),
        )


class ConvertedBalanceResponse(Model):
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
@invest_agent.on_rest_post(
    "/asset/swap/price",
    AssetSwapPriceInfoRequest,
    ConvertedBalanceResponse,
)
@authentication(configuration.agent_key)
async def get_asset_swap_price(_ctx: Context, req: AssetSwapPriceInfoRequest):
    """Test authentication to the Agent."""

    converted_balance = await get_asset_swap_price_use_case.execute(req.to_domain())

    return ConvertedBalanceResponse.from_domain(converted_balance)


class AuthRequest(Model):
    agent_key: str


class AuthResponse(Model):
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
@invest_agent.on_rest_post("/auth", AuthRequest, AuthResponse)
@authentication(configuration.agent_key)
async def auth_request(_ctx: Context, _req: AuthRequest) -> AuthResponse:
    return AuthResponse(status="OK")


class HealthResponse(Model):
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
@invest_agent.on_rest_get("/health", HealthResponse)
async def health_check(_ctx: Context) -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="OK")


class PortfolioRequest(Model):
    agent_key: str
    token: TokenRequest

    def to_domain(self):
        return Token(
            id=self.token.id,
            name=self.token.name,
            display_name=self.token.display_name,
            ticker=self.token.ticker,
            address=self.token.address,
        )


class BalanceAtomicResponse(Model):
    asset: AssetResponse
    amount: str
    amount_atomic: str
    decimals: int

    @staticmethod
    def from_domain(balance: BalanceAtomic) -> "BalanceAtomicResponse":
        """Convert the domain Balance to a BalanceResponse."""
        return BalanceAtomicResponse(
            amount=str(balance.amount),
            amount_atomic=str(balance.amount_atomic),
            asset=TokenResponse.from_domain(balance.asset)
            if isinstance(balance.asset, Token)
            else BasketResponse.from_domain(balance.asset),
            decimals=balance.decimals,
        )


class FeesResponse(Model):
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


class ChainTransactionResponse(Model):
    id: str
    try_id: str
    order_id: str
    type: ChainTransactionType
    data: str
    hash: str
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


class TryResponse(Model):
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


class OrderResponse(Model):
    id: str
    sell_balance: BalanceAtomicResponse
    buy_balance: BalanceAtomicResponse
    type: OrderType
    tries: list[TryResponse]
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
            tries=[TryResponse.from_domain(try_) for try_ in domain.tries],
            created_at=domain.created_at,
            status=domain.status,
            trigger=domain.trigger,
        )


class PortfolioBalanceResponse(Model):
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


class PortfolioResponse(Model):
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
@invest_agent.on_rest_post(
    "/portfolio",
    PortfolioRequest,
    PortfolioResponse,
)
@authentication(configuration.agent_key)
async def get_portfolio(_ctx: Context, req: PortfolioRequest):
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
@invest_agent.on_rest_get("/openapi", OpenApiResponse)
async def generate_openapi_documentation(_ctx: Context):
    return cast(OpenApiResponse, spec.to_dict())


def main():
    invest_agent.run()


if __name__ == "__main__":
    main()
