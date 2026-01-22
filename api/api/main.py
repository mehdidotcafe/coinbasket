from contextlib import asynccontextmanager
from contextvars import ContextVar
from decimal import Decimal
from typing import Any, Dict, Literal, Optional, cast

from api.asset.get_asset_by_id_use_case import GetAssetByIdUseCase
from api.asset.get_asset_swap_price_use_case import (
    AssetSwapPriceInfo,
    ConvertedBalance,
    GetAssetSwapPriceUseCase,
)
from api.authentication.generate_auth_nonce_use_case import GenerateAuthNonceUseCase
from api.authentication.verify_auth_use_case import VerifyAuthUseCase
from api.chain.chain import Gas
from api.conversation.conversation_use_case import ConversationUseCase
from api.conversation.get_conversation_messages_use_case import (
    GetConversationMessagesUseCase,
)
from api.investment.confirmed_order import ConfirmedOrder, ConfirmedOrderId
from api.investment.executed_order import ExecutedOrder
from api.investment.fees import Fees
from api.investment.intended_order import (
    IntendedOrder,
    IntendedOrderId,
)
from api.investment.plan_order_use_case import (
    PlanOrderUseCase,
)
from api.investment.build_signable_order_use_case import (
    BuildSignableOrderUseCase,
)
from api.address.address import Address

from api.investment.planned_order import PlannedOrder, PlannedOrderBalance
from api.investment.signable_order import SignableOrder
from api.portfolio.get_portfolio_asset_balance_use_case import (
    GetPortfolioAssetBalanceUseCase,
    PortfolioAssetBalance,
)
from api.portfolio.get_portfolio_use_case import (
    GetPortfolioUseCase,
    Portfolio,
    PortfolioBalance,
)
from api.protocol.asset import Asset
from api.protocol.asset_category import AssetCategory
from api.shared.app_exception import AppException
from api.similarity.basket.get_all_baskets_use_case import GetAllBasketsUseCase
from api.similarity.get_similar_assets_use_case import GetSimilarAssetsUseCase

from apispec import APISpec
from api.registry import (
    chain,
    configuration,
    conversation_repository,
    date_time,
    exchange,
    id_generator,
    asset_balance_converter,
    small_balance_policy,
    similarity_storage,
    siwe_manager,
    credential_generator,
    holding_repository,
    intended_order_repository,
    planned_order_repository,
    confirmed_order_repository,
    signable_order_repository,
    executed_order_repository,
)
from api.chain.balance import Balance, BalanceAtomic
from api.conversation.message import Message, QueryMessage
from api.documentation.response.invalid_authentication_credential import (
    invalid_authentication_credential,
)

from api.documentation.openapi import openapi
from api.protocol.token import Token
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, RootModel

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from api.protocol import (
    AssetResponse,
    BasketResponse,
    TokenResponse,
)
from api.protocol.fixture.token import usdt_token

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.types import interrupt

print(f"Agent Env: {configuration.app_env}")

# Context variable to store the authenticated user's address
request_address_context: ContextVar[str | None] = ContextVar(
    "request_address", default=None
)

get_portfolio_use_case = GetPortfolioUseCase(
    holding_repository=holding_repository,
    exchange=exchange,
    chain=chain,
    asset_balance_converter=asset_balance_converter,
    small_balance_policy=small_balance_policy,
)

get_portfolio_asset_balance_use_case = GetPortfolioAssetBalanceUseCase(
    chain=chain, holding_repository=holding_repository
)

conversation_use_case = ConversationUseCase(
    date_time=date_time,
    id_generator=id_generator,
)

get_conversation_messages_use_case = GetConversationMessagesUseCase(
    conversation_repository=conversation_repository
)


plan_order_use_case = PlanOrderUseCase(
    exchange=exchange,
    chain=chain,
    holding_repository=holding_repository,
    asset_balance_converter=asset_balance_converter,
)

build_signable_order_use_case = BuildSignableOrderUseCase(
    exchange=exchange, id_generator=id_generator
)

get_asset_swap_price_use_case = GetAssetSwapPriceUseCase(
    chain=chain,
    asset_balance_converter=asset_balance_converter,
)


get_similar_assets_use_case = GetSimilarAssetsUseCase(similarity_storage)

get_all_baskets_use_case = GetAllBasketsUseCase(similarity_storage)

get_asset_by_id_use_case = GetAssetByIdUseCase(
    asset_repository=similarity_storage, chain=chain
)

generate_auth_nonce_use_case = GenerateAuthNonceUseCase(
    siwe_manager=siwe_manager,
)

verify_auth_use_case = VerifyAuthUseCase(
    siwe_manager=siwe_manager,
    credential_generator=credential_generator,
    date_time=date_time,
)

spec = APISpec(
    title=configuration.app_name,
    version="0.0.1",
    openapi_version="3.0.2",
)


class ErrorResponse(BaseModel):
    message: str
    details: dict[str, Any] | None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Blocking call
    similarity_storage.start()

    await conversation_repository.start()

    print("API Ready.")

    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=configuration.frontend_url.split(","),
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def credential_authentication_middleware(request: Request, call_next):
    excluded_paths = [
        "/auth/nonce",
        "/auth/verify",
        "/health",
        "/docs",
        "/openapi",
        "/openapi.json",
    ]

    if not request.method == "OPTIONS" and not any(
        request.url.path.startswith(path) for path in excluded_paths
    ):
        credential = request.cookies.get("credential")

        if not credential:
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(
                    message="Credential cookie missing", details=None
                ).model_dump(),
            )

        claims = credential_generator.verify_credential(credential)

        if not claims:
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(
                    message="Invalid credential", details=None
                ).model_dump(),
            )

        # Store the address from claims in request state
        request.state.address = claims.get("address")

    return await call_next(request)


@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exception: AppException):
    return JSONResponse(
        status_code=exception.status_code,
        content={"message": exception.message, "details": exception.details},
    )


class AssetRequest(BaseModel):
    id: str

    @staticmethod
    def from_domain(asset: Asset) -> "AssetRequest":
        """Convert an Asset to an AssetRequest."""
        return AssetRequest(
            id=asset.id,
        )

    async def to_domain(self) -> Asset:
        """Convert the request to an Asset."""
        asset = await get_asset_by_id_use_case.execute(self.id)

        if not asset:
            raise ValueError(f"Asset id {self.id} not found")

        return asset


class ToolAssetRequest(BaseModel):
    asset_id: str


@tool(parse_docstring=True)
async def get_assets_from_filters(
    name_or_ticker: str | None,
    asset_type: Literal["TOKEN", "BASKET"] | None = None,
    categories: list[AssetCategory] | None = None,
) -> list[TokenResponse | BasketResponse]:
    """
    Retrieve a list of available assets from given filters.

    Args:
        name_or_ticker: The query to search for. It could be an asset name, ticker or part of it.
        categories: An optional list of categories to filter assets.
        asset_type: An optional asset type to filter assets (TOKEN or BASKET).


    Returns:
        A list of documents containing assets.
    """
    assets = await get_similar_assets_use_case.execute(
        name_or_ticker, asset_type, categories
    )

    return [
        (
            TokenResponse.from_domain(asset)
            if isinstance(asset, Token)
            else BasketResponse.from_domain(asset)
        )
        for asset in assets
    ]


class GetPortfolioSummaryRequest(BaseModel):
    conversion_token_id: str = usdt_token.id


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


@tool(
    parse_docstring=True,
)
async def get_portfolio_summary(
    request: GetPortfolioSummaryRequest = GetPortfolioSummaryRequest(),
):
    """EXPENSIVE/SLOW. Retrieve the portfolio. Only use this tool when the user asks for his portfolio.
    The portfolio contains the list of assets held by the agent (holdings) and their balances both in asset token and in converted token (defaults to USDT).
    It also contains the available cash balance in BNB and the list of pending (processing) orders.
    IMPORTANT: Do not call another tool if this returns results.

    Args:
        request: The request containing the token ID to convert the portfolio asset balances to (defaults to USDT).

    Returns:
        The portfolio of the agent.
    """
    # address = cast(Address, request_address_context.get())

    # conversion_asset = await get_asset_by_id_use_case.execute(
    #     request.conversion_token_id
    # )

    # if not conversion_asset:
    #     raise ValueError(f"Conversion token id {request.conversion_token_id} not found")
    # return PortfolioResponse.from_domain(
    #     await get_portfolio_use_case.execute(address, conversion_asset)
    # ).model_dump_json()
    return "The portfolio feature is not implemented yet and is coming soon."


@tool(
    parse_docstring=True,
)
async def get_token_or_basket_or_asset_balance(request: ToolAssetRequest):
    """FAST. Retrieve ONLY the balance of a specific asset (token or basket).
    Use this tool when the user asks for his asset balance / holding or when you need the asset balance for planning and executing an order.

    Args:
        request: An object containing a field token to retrieve the available cash and balance for.

    Returns:
        The balance of the asset in the agent's wallet.
    """
    address = cast(Address, request_address_context.get())
    asset = await get_asset_by_id_use_case.execute(request.asset_id)

    if not asset:
        raise ValueError(f"Asset id {request.asset_id} not found")

    holding = await holding_repository.get_holding_balance(
        address,
        asset if not chain.is_native_token(asset) else chain.get_wrapped_base_token(),
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
    address = cast(Address, request_address_context.get())

    balance = await chain.get_native_token_balance(address)

    return BalanceAtomicResponse.from_domain(balance).model_dump_json()


class GetAssetPriceRequest(BaseModel):
    asset_id: str
    conversion_asset_id: str = usdt_token.id
    asset_amount: str = "1"

    async def to_domain(self) -> AssetSwapPriceInfo:
        """Convert the request to an AssetSwapPriceInfo."""
        asset = await get_asset_by_id_use_case.execute(self.asset_id)
        if not asset:
            raise ValueError(f"Asset id {self.asset_id} not found")

        conversion_asset = await get_asset_by_id_use_case.execute(
            self.conversion_asset_id
        )

        if not conversion_asset:
            raise ValueError(
                f"Conversion asset id {self.conversion_asset_id} not found"
            )

        return AssetSwapPriceInfo(
            sell_asset=asset,
            sell_asset_amount=Decimal(self.asset_amount),
            buy_asset=conversion_asset,
        )


class GetAssetPriceResponse(BaseModel):
    balance: BalanceResponse

    @staticmethod
    def from_domain(
        converted_balance: ConvertedBalance,
    ) -> "GetAssetPriceResponse":
        return GetAssetPriceResponse(
            balance=BalanceResponse.from_domain(converted_balance.buy_balance),
        )


@tool(
    parse_docstring=True,
)
async def get_asset_price(request: GetAssetPriceRequest):
    """FAST. Retrieve the price of a specific asset converted to a conversion token.
    Use this tool when the user asks for the price of an asset.

    Args:
        request: An object containing the asset_id to get the price for, an optional conversion_asset_id (defaults to USDT) and asset_amount (defaults to 1).

    Returns:
        The price of 1 unit of the asset in both native and converted form.
    """
    address = cast(Address, request_address_context.get())

    asset = await get_asset_by_id_use_case.execute(request.asset_id)
    if not asset:
        raise ValueError(f"Asset id {request.asset_id} not found")

    conversion_asset = await get_asset_by_id_use_case.execute(
        request.conversion_asset_id
    )
    if not conversion_asset:
        raise ValueError(f"Conversion asset id {request.conversion_asset_id} not found")

    balance = await get_asset_swap_price_use_case.execute(
        address=address,
        asset_swap_price_info=await request.to_domain(),
    )

    return GetAssetPriceResponse.from_domain(balance).model_dump_json()


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


class ExecutedOrderResponse(BaseModel):
    id: str
    transaction_hash: str
    buy_balance: BalanceAtomicResponse
    sell_balance: BalanceAtomicResponse

    @staticmethod
    def from_domain(domain: ExecutedOrder) -> "ExecutedOrderResponse":
        return ExecutedOrderResponse(
            id=domain.id,
            transaction_hash=domain.transaction_hash,
            buy_balance=BalanceAtomicResponse.from_domain(domain.buy_balance),
            sell_balance=BalanceAtomicResponse.from_domain(domain.sell_balance),
        )


class ExecutedOrdersResponse(BaseModel):
    orders: list[ExecutedOrderResponse]

    @classmethod
    def from_domain(cls, orders: list[ExecutedOrder]) -> "ExecutedOrdersResponse":
        return cls(
            orders=[ExecutedOrderResponse.from_domain(order) for order in orders]
        )


@tool(
    parse_docstring=True,
)
async def get_executed_orders(limit: int = 50, offset: int = 0):
    """SLOW / EXPENSIVE. Retrieve the executed orders from an eventual pagination

    Args:
        limit: The maximum number of orders to retrieve.
        offset: The offset for pagination.

    Returns:
        The list of orders matching the criteria.
    """
    orders = await executed_order_repository.get(limit, offset)

    return ExecutedOrdersResponse.from_domain(orders).model_dump_json()


@tool(
    parse_docstring=True,
)
async def get_executed_order(
    executed_order_id: str,
):
    """FAST. Retrieve an executed order from its id

    Args:
        executed_order_id: The id of the executed order to retrieve.

    Returns:
        The order matching the id or None if the order has not been found.
    """
    order = await executed_order_repository.get_one(executed_order_id)

    return ExecutedOrderResponse.from_domain(order).model_dump_json() if order else None


@tool(
    parse_docstring=True,
)
async def get_address():
    """FAST. Retrieve the address of the authenticated user.

    Args: None

    Returns:
        The address of the authenticated user.
    """
    address = cast(Address, request_address_context.get())
    return address


class BalanceRequest(BaseModel):
    asset: AssetRequest
    amount: str

    async def to_domain(self) -> Balance:
        """Convert the request to a Balance."""
        return Balance(
            asset=await self.asset.to_domain(),
            amount=Decimal(self.amount),
        )


class ConfirmedOrderRequest(BaseModel):
    planned_order_id: str
    buy_balance: BalanceRequest
    sell_balance: BalanceRequest

    async def to_domain(self, id: ConfirmedOrderId, address: Address) -> ConfirmedOrder:
        return ConfirmedOrder(
            id=id,
            planned_order_id=self.planned_order_id,
            address=address,
            buy_balance=await self.buy_balance.to_domain(),
            sell_balance=await self.sell_balance.to_domain(),
        )


class SignedOrderRequest(BaseModel):
    status: Literal["CONFIRM", "CANCEL"]
    signable_order_id: str | None = None
    transaction_hash: str | None = None


class IntentOrderRequest(BaseModel):
    sell_asset_id: str | None = None
    buy_asset_id: str | None = None
    sell_amount: str | None = None
    buy_amount: str | None = None

    async def to_domain(self, id: IntendedOrderId, address: Address):
        sell_asset = None

        if self.sell_asset_id:
            sell_asset = await get_asset_by_id_use_case.execute(self.sell_asset_id)

            if not sell_asset:
                raise ValueError(f"Asset id {self.sell_asset_id} not found")

        buy_asset = None

        if self.buy_asset_id:
            buy_asset = await get_asset_by_id_use_case.execute(self.buy_asset_id)

            if not buy_asset:
                raise ValueError(f"Asset id {self.buy_asset_id} not found")

        type = "SELL" if self.sell_amount else "BUY"
        amount = self.sell_amount or self.buy_amount

        return IntendedOrder(
            id=id,
            address=address,
            sell_asset=sell_asset,
            buy_asset=buy_asset,
            amount=Decimal(amount) if amount else None,
            type=type,
        )


class PlanAndExecuteOrderResponse(BaseModel):
    message: str
    executed_order: ExecutedOrderResponse | None = None

    @staticmethod
    def from_domain(
        message: str, executed_order: ExecutedOrder | None
    ) -> "PlanAndExecuteOrderResponse":
        return PlanAndExecuteOrderResponse(
            message=message,
            executed_order=ExecutedOrderResponse.from_domain(executed_order)
            if executed_order
            else None,
        )


class GasResponse(BaseModel):
    gas: str | None
    gas_price: str | None

    @staticmethod
    def from_domain(domain: Gas) -> "GasResponse":
        return GasResponse(
            gas=str(domain.gas) if domain.gas is not None else None,
            gas_price=str(domain.gas_price) if domain.gas_price is not None else None,
        )


class SignableTransactionResponse(BaseModel):
    type: Literal["SIGN", "SEND"]
    amount: str
    data: Any
    gas: GasResponse | None = None
    to_address: str | None = None


class ApprovalTransactionResponse(BaseModel):
    token_address: str
    spender_address: str
    data: str
    amount: str


class SignableOrderResponse(BaseModel):
    id: str
    buy_balance: BalanceAtomicResponse
    sell_balance: BalanceAtomicResponse
    transaction: SignableTransactionResponse
    signature_payload: Dict[str, Any] | None = None
    approval_transaction: ApprovalTransactionResponse | None = None

    @staticmethod
    def from_domain(
        domain: SignableOrder,
    ) -> "SignableOrderResponse":
        return SignableOrderResponse(
            id=domain.id,
            buy_balance=BalanceAtomicResponse.from_domain(domain.buy_balance),
            sell_balance=BalanceAtomicResponse.from_domain(domain.sell_balance),
            signature_payload=domain.signature_payload,
            approval_transaction=ApprovalTransactionResponse(
                token_address=domain.approval_transaction.token_address,
                spender_address=domain.approval_transaction.spender_address,
                data=domain.approval_transaction.data,
                amount=str(domain.approval_transaction.amount),
            )
            if domain.approval_transaction
            else None,
            transaction=SignableTransactionResponse(
                type=domain.transaction.type,
                amount=str(domain.transaction.amount),
                data=domain.transaction.data,
                gas=GasResponse.from_domain(domain.transaction.gas)
                if domain.transaction.gas
                else None,
                to_address=domain.transaction.to_address,
            ),
        )


class PlannedOrderAssetWithAmountResponse(BaseModel):
    asset: AssetResponse
    available_amount: str
    amount: str | None

    @staticmethod
    def from_domain(
        domain: PlannedOrderBalance,
    ) -> "PlannedOrderAssetWithAmountResponse":
        return PlannedOrderAssetWithAmountResponse(
            asset=TokenResponse.from_domain(domain.asset)
            if isinstance(domain.asset, Token)
            else BasketResponse.from_domain(domain.asset),
            amount=format(domain.amount, "f") if domain.amount is not None else None,
            available_amount=format(domain.available_amount, "f"),
        )


class FeesResponse(BaseModel):
    gas_fee: BalanceAtomicResponse | None
    provider_fee: BalanceAtomicResponse | None
    platform_fee: BalanceAtomicResponse | None

    @staticmethod
    def from_domain(fees: Fees) -> "FeesResponse":
        return FeesResponse(
            gas_fee=BalanceAtomicResponse.from_domain(fees.gas_fee)
            if fees.gas_fee
            else None,
            provider_fee=BalanceAtomicResponse.from_domain(fees.provider_fee)
            if fees.provider_fee
            else None,
            platform_fee=BalanceAtomicResponse.from_domain(fees.platform_fee)
            if fees.platform_fee
            else None,
        )


class PlannedOrderResponse(BaseModel):
    id: str
    address: str
    sell_asset_with_amount: PlannedOrderAssetWithAmountResponse
    buy_asset_with_amount: PlannedOrderAssetWithAmountResponse
    fees: FeesResponse

    @staticmethod
    def from_domain(domain: PlannedOrder) -> "PlannedOrderResponse":
        return PlannedOrderResponse(
            id=domain.id,
            address=domain.address,
            sell_asset_with_amount=PlannedOrderAssetWithAmountResponse.from_domain(
                domain.sell_asset_with_amount
            ),
            buy_asset_with_amount=PlannedOrderAssetWithAmountResponse.from_domain(
                domain.buy_asset_with_amount
            ),
            fees=FeesResponse.from_domain(domain.fees),
        )


@tool(parse_docstring=True)
async def plan_and_execute_swap_order(
    intended_order_request: IntentOrderRequest,
):
    """Executes the intent order.
    If no buy_asset_id, amount or sell_asset_id is provided set the field to None.
    Pass asset_id as they are don't change them.
    IMPORTANT: You can make a swap by providing both a buy_asset_id and a sell_asset_id.
    IMPORTANT: You don't need to know the amount to buy, sell, swap an asset in advance. You can leave the amount fields empty (set to None) and the agent will decide the amount to buy or sell based on the available cash and holdings.
    IMPORTANT: Only provide sell_amount or buy_amount. If user wants to buy or sell from a dollars or euro amount you first have to convert it to the related asset amount using the get_asset_price tool.
    IMPORTANT: Do not call another tool if this returns results.

    Args:
        intended_order_request (IntentOrderRequest): The intent order containing the assets to buy and/or sell eventually with their amounts for each step. A step can't have an amount defined if the related asset is not provided.

    Returns:
        PlanAndExecuteOrderResponse: The response containing the message and order hash.

    Example:
        IntentOrderRequest(
            buy_asset_id="2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
            sell_asset_id="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            buy_amount="5.33",
            sell_amount=None,
        )
        IntentOrderRequest(
            buy_asset_id="2bb6425b-a9ee-4292-89c8-c1f0c7a5cb70",
            sell_asset_id="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            sell_amount="9",
            buy_amount=None,
        )
    """
    address = cast(Address, request_address_context.get())

    intended_order = await intended_order_request.to_domain(
        id_generator.generate_random_id(), address
    )

    await intended_order_repository.save(intended_order)

    planned_order = await plan_order_use_case.execute(
        address=address,
        intended_order=intended_order,
    )

    if planned_order:
        await planned_order_repository.save(planned_order)

        signed_order_request = SignedOrderRequest.model_validate(
            interrupt(
                {
                    "ui": {
                        "id": "confirm_planned_order",
                        "args": {
                            "planned_order": PlannedOrderResponse.from_domain(
                                planned_order
                            ).model_dump(),
                        },
                    },
                    "content": None,
                }
            )
        )

        if signed_order_request.status == "CANCEL":
            return PlanAndExecuteOrderResponse.from_domain(
                "Order cancelled by user.",
                None,
            ).model_dump_json()

        order_receipt = await chain.parse_transaction_receipt(
            address=address,
            sell_asset=planned_order.sell_asset_with_amount.asset,
            buy_asset=planned_order.buy_asset_with_amount.asset,
            transaction_hash=cast(str, signed_order_request.transaction_hash),
        )

        executed_order = ExecutedOrder(
            id=id_generator.generate_random_id(),
            signable_order_id=cast(str, signed_order_request.signable_order_id),
            transaction_hash=cast(str, signed_order_request.transaction_hash),
            address=address,
            sell_balance=order_receipt.executed_sell_balance,
            buy_balance=order_receipt.executed_buy_balance,
            rate=order_receipt.rate,
        )

        await executed_order_repository.save(executed_order)

        return PlanAndExecuteOrderResponse.from_domain(
            "Order executed successfully.",
            executed_order,
        ).model_dump_json()


coinbasket_tools = [
    get_assets_from_filters,
    plan_and_execute_swap_order,
    get_available_cash,
    get_token_or_basket_or_asset_balance,
    get_asset_price,
    get_portfolio_summary,
    get_executed_orders,
    get_executed_order,
    get_address,
]


class QueryMessageRequest(BaseModel):
    id: str
    is_resuming: bool
    role: Literal["user"]
    content: str
    created_at: Optional[str]


class PromptRequest(BaseModel):
    message: QueryMessageRequest


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
                "401": invalid_authentication_credential,
            },
        }
    },
)
@app.post("/conversation")
async def conversation(request: Request, req: PromptRequest) -> MessageResponse:
    address = Address(getattr(request.state, "address"))
    request_address_context.set(address)

    async with AsyncPostgresSaver.from_conn_string(
        f"postgres://{configuration.database_user}:{configuration.database_password}@{configuration.database_host}:{configuration.database_port}/{configuration.database_name}"
    ) as checkpointer:
        agent_executor = await __create_agent_executor(checkpointer)

        message = await conversation_use_case.execute(
            thread_id=address,
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


async def __create_agent_executor(checkpointer: AsyncPostgresSaver):
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
        checkpointer=checkpointer,
        prompt=SystemMessage(
            "\n".join(
                [
                    "Your goal is to manage a portfolio made of assets on the BNB Chain. An asset is either a token or a basket.  ",
                    "Users can place orders to buy, sell, or swap assets for their portfolio.  ",
                    "When you display a token, ALWAYS display its display name, ticker and address by using this link 'https://bscscan.com/token/[token_address]'.  ",
                    "ALWAYS use a tool to fetch an asset address when you need it.  ",
                    "ALWAYS display amount with 4 decimals, don't use scientific notation.  ",
                    "The only way to place order is to use the plan_and_execute_swap_order tool.  ",
                    "You don't need to know the asset prices before calling the plan_and_execute_swap_order tool, the tool will handle it for you.  ",
                    "When asked for token, portfolio, order, asset or balance information, ALWAYS use a tool to fetch the data.  ",
                    "Formatting re-enabled — please use Markdown **bold**, links and header tags to **improve the readability** of your responses.",
                    "Consider all tool parameters optional unless explicitly stated otherwise.",
                    "If you don't know the answer, just say that you don't know and mention what you can do, don't try to make up an answer.  ",
                ]
            )
        ),
    )

    return agent_executor


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
    schemas=[],
    path="/conversation/messages",
    operations={
        "post": {
            "summary": "Get Agent messages history",
            "tags": ["Conversation"],
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
                "401": invalid_authentication_credential,
            },
        }
    },
)
@app.post("/conversation/messages")
async def get_conversation_messages(request: Request) -> MessagesResponse:
    address = Address(getattr(request.state, "address"))
    """Retrieve the conversation messages."""
    async with AsyncPostgresSaver.from_conn_string(
        f"postgres://{configuration.database_user}:{configuration.database_password}@{configuration.database_host}:{configuration.database_port}/{configuration.database_name}"
    ) as checkpointer:
        agent_executor = await __create_agent_executor(checkpointer)

        messages = await get_conversation_messages_use_case.execute(
            thread_id=address, agent_executor=agent_executor
        )

        return MessagesResponse.from_domain(messages)


class AssetSwapPriceInfoRequest(BaseModel):
    sell_asset: AssetRequest
    sell_asset_amount: str
    buy_asset: AssetRequest

    async def to_domain(self) -> AssetSwapPriceInfo:
        """Convert the request to an AssetSwapPriceInfo."""
        return AssetSwapPriceInfo(
            sell_asset=await self.sell_asset.to_domain(),
            sell_asset_amount=Decimal(self.sell_asset_amount),
            buy_asset=await self.buy_asset.to_domain(),
        )


class ConvertedBalanceResponse(BaseModel):
    sell_balance: BalanceResponse
    buy_balance: BalanceResponse
    fees: FeesResponse

    @staticmethod
    def from_domain(
        converted_balance: ConvertedBalance,
    ) -> "ConvertedBalanceResponse":
        return ConvertedBalanceResponse(
            sell_balance=BalanceResponse.from_domain(converted_balance.sell_balance),
            buy_balance=BalanceResponse.from_domain(converted_balance.buy_balance),
            fees=FeesResponse.from_domain(converted_balance.fees),
        )


@openapi(
    spec=spec,
    schemas=[
        AssetSwapPriceInfoRequest,
        TokenResponse,
        BasketResponse,
        BalanceResponse,
        ConvertedBalanceResponse,
        FeesResponse,
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
                "401": invalid_authentication_credential,
            },
        }
    },
)
@app.post(
    "/asset/swap/price",
)
async def get_asset_swap_price(request: Request, req: AssetSwapPriceInfoRequest):
    """Test authentication to the Agent."""
    address = cast(Address, request.state.address)

    converted_balance = await get_asset_swap_price_use_case.execute(
        address, await req.to_domain()
    )
    return ConvertedBalanceResponse.from_domain(converted_balance)


@openapi(
    spec=spec,
    schemas=[
        BalanceRequest,
        ConfirmedOrderRequest,
        SignableTransactionResponse,
        SignableOrderResponse,
    ],
    path="/order/signable",
    operations={
        "post": {
            "summary": "Build a signable order from a confirmed order",
            "tags": ["Order"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ConfirmedOrderRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Signable order ready for signing",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SignableOrderResponse"
                            }
                        }
                    },
                },
                "401": invalid_authentication_credential,
            },
        }
    },
)
@app.post("/order/signable")
async def build_signable_order(request: Request, req: ConfirmedOrderRequest):
    """Build a signable order from a confirmed order."""
    address = cast(Address, request.state.address)
    confirmed_order = await req.to_domain(id_generator.generate_random_id(), address)

    await confirmed_order_repository.save(confirmed_order)

    signable_order = await build_signable_order_use_case.execute(confirmed_order)

    await signable_order_repository.save(signable_order)

    return SignableOrderResponse.from_domain(signable_order)


class AuthResponse(BaseModel):
    status: str


@openapi(
    spec=spec,
    schemas=[AuthResponse],
    path="/auth",
    operations={
        "post": {
            "summary": "Test authentication to the Agent",
            "tags": ["Authentication"],
            "responses": {
                "200": {
                    "description": "Authentication status",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AuthResponse"}
                        }
                    },
                },
                "401": invalid_authentication_credential,
            },
        }
    },
)
@app.post("/auth")
async def auth_request() -> AuthResponse:
    return AuthResponse(status="OK")


class AuthVerifyRequest(BaseModel):
    message: str
    signature: str


class AuthVerifyResponse(BaseModel):
    credential: str


@openapi(
    spec=spec,
    schemas=[AuthVerifyRequest, AuthVerifyResponse, ErrorResponse],
    path="/auth/verify",
    operations={
        "get": {
            "summary": "Verify a signature of the nonce for authentication. Return a JWT token if successful.",
            "tags": ["Authentication"],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/AuthVerifyRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Address Credential",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/AuthVerifyResponse"
                            }
                        }
                    },
                    "headers": {
                        "Set-Cookie": {
                            "description": "Cookie of the address Credential",
                            "schema": {"type": "string"},
                            "example": "token=eyJhbGciOiJIUzI1NiJ9.eyJhZGRyZXNzIjoiMHhmYWtlYWRkcmVzcyIsImV4cCI6IjE3MDAwMDAwMDAwIn0.d3XdcV86FrpkeHCI6yoFNg6LdRrsIIrUZqn48WHfEFw; Path=/; HttpOnly",
                        }
                    },
                },
                "401": {
                    "description": "Invalid signature or message",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    },
                },
            },
        }
    },
)
@app.post("/auth/verify")
async def auth_verify(request: Request, req: AuthVerifyRequest) -> JSONResponse:
    nonce = request.cookies.get("nonce")

    if not nonce:
        raise HTTPException(
            status_code=400,
            detail="Nonce cookie is missing. Please obtain a nonce first.",
        )

    credential, claims = await verify_auth_use_case.execute(
        nonce=nonce,
        signature=req.signature,
        message=req.message,
        domain=configuration.frontend_url.split(",")[0]
        .replace("https://", "")
        .replace("http://", ""),
    )

    response = JSONResponse(
        content=AuthVerifyResponse(credential=credential).model_dump()
    )

    response.delete_cookie(key="nonce")
    response.set_cookie(
        key="credential",
        value=credential,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=int(claims["exp"]) - date_time.now(),
    )

    return response


class AuthNonceResponse(BaseModel):
    nonce: str


@openapi(
    spec=spec,
    schemas=[AuthNonceResponse],
    path="/auth/nonce",
    operations={
        "get": {
            "summary": "Return a nonce for authentication",
            "tags": ["Authentication"],
            "responses": {
                "200": {
                    "description": "Nonce for authentication",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AuthNonceResponse"}
                        }
                    },
                    "headers": {
                        "Set-Cookie": {
                            "description": "Nonce cookie for authentication",
                            "schema": {"type": "string"},
                            "example": "nonce=abc123; Path=/; HttpOnly",
                        }
                    },
                }
            },
        }
    },
)
@app.get("/auth/nonce")
async def generate_auth_nonce() -> JSONResponse:
    nonce = generate_auth_nonce_use_case.execute()

    response = JSONResponse(content=AuthNonceResponse(nonce=nonce).model_dump())
    response.set_cookie(
        key="nonce",
        value=nonce,
        httponly=True,
        secure=configuration.app_env != "development",
        samesite="strict",
        # 5 minutes validity
        max_age=60 * 5,
    )

    return response


@openapi(
    spec=spec,
    schemas=[],
    path="/auth/signout",
    operations={
        "post": {
            "summary": "Sign out the user by clearing authentication cookies",
            "tags": ["Authentication"],
            "responses": {
                "204": {
                    "description": "Successfully signed out, cookies cleared",
                    "content": {},
                    "headers": {
                        "Set-Cookie": {
                            "description": "Delete nonce cookie and credential cookies for authentication",
                            "schema": {"type": "string"},
                            "example": 'nonce=""; credential=""; Path=/; HttpOnly',
                        }
                    },
                }
            },
        }
    },
)
@app.post("/auth/signout")
async def signout() -> Response:
    response = Response(status_code=204)
    response.delete_cookie(key="nonce")
    response.delete_cookie(key="credential")

    return response


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
    token: AssetRequest

    async def to_domain(self):
        return await AssetRequest.to_domain(self.token)


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
        AssetRequest,
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
                "401": invalid_authentication_credential,
            },
        }
    },
)
@app.post("/portfolio")
async def get_converted_portfolio(request: Request, req: PortfolioRequest):
    address = Address(getattr(request.state, "address"))
    converted_token_balances = await get_portfolio_use_case.execute(
        address, await req.to_domain()
    )

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
