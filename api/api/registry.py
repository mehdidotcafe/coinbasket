from typing import cast
from api.authentication.credential.infrastructure.py_jwt_credential_generator import (
    PyJwtCredentialGenerator,
)
from api.authentication.siwe.infrastructure.siwe_py_siwe_manager import (
    SiwePySiweManager,
)
from api.chain.infrastructure.test_transaction_receipt_parser import (
    TestTransactionReceiptParser,
)
from api.conversation.repository.infrastructure.langchain_postgresql_conversation_repository import (
    LangchainPostgresqlConversationRepository,
)
from api.investment.infrastructure.test_exchange import TestExchange
from api.investment.order.infrastructure.sql_alchemy_confirmed_order_repository import (
    SqlAlchemyConfirmedOrderRepository,
)
from api.investment.order.infrastructure.sql_alchemy_intended_order_repository import (
    SqlAlchemyIntendedOrderRepository,
)
from api.investment.order.infrastructure.sql_alchemy_planned_order_repository import (
    SqlAlchemyPlannedOrderRepository,
)
from api.investment.order.infrastructure.sql_alchemy_signable_order_repository import (
    SqlAlchemySignableOrderRepository,
)
from api.investment.order.infrastructure.sql_alchemy_executed_order_repository import (
    SqlAlchemyExecutedOrderRepository,
)
from api.portfolio.holding.infrastructure.bsc_chain_holding_repository import (
    BscChainHoldingRepository,
)
from pydantic import SecretStr
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, AsyncQdrantClient

from langchain_openai import OpenAIEmbeddings

from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
)
from api.portfolio.small_balance.absolute_small_balance_policy import (
    AbsoluteSmallBalancePolicy,
)

from api.chain.infrastructure.bsc.bsc_transaction_receipt_parser import (
    BscTransactionReceiptParser,
)

from api.database.infrastructure.sql_alchemy_session_manager import (
    SqlAlchemySessionManager,
)

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from api.datetime.infrastructure.python_date_time import PythonDateTime

from api.shared.http_request.infrastructure.aiohttp_http_request import (
    AiohttpHttpRequest,
)
from api.shared.id_generator.id_generator import IdGenerator
from api.shared.random_generator.random_generator import RandomGenerator
from api.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from api.investment.infrastructure.zero_x.zero_x_swapper import ZeroXSwapper

from web3 import AsyncWeb3, AsyncHTTPProvider

from api.chain.infrastructure.bsc.bsc_chain import BscChain
from api.chain.infrastructure.bsc.bsc_contract import BscContract
from api.configuration import Configuration

from api.similarity.infrastructure.qdrant_langchain.qdrant_langchain_asset_similarity_repository import (
    QdrantLangChainAssetSimilarityRepository,
)
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
)

date_time = PythonDateTime()


configuration = Configuration()

w3 = AsyncWeb3(
    AsyncHTTPProvider(
        endpoint_uri=configuration.bsc_rpc_url,
        request_kwargs={"headers": {"Origin": configuration.app_domain}}
        if configuration.app_env == "production"
        else None,
    )
)

transaction_receipt_parser = (
    BscTransactionReceiptParser(w3=w3)
    if configuration.app_env != "test"
    else TestTransactionReceiptParser()
)

chain = BscChain(
    w3=w3,
    transaction_receipt_parser=transaction_receipt_parser,
)

contract = BscContract(w3=w3)

aiohttp_http_request = AiohttpHttpRequest(
    configuration={"app_domain": configuration.app_domain}
)

id_generator = IdGenerator()

random_generator = RandomGenerator()

api_client = ZeroXApiClient(
    configuration={
        "zero_x_api_url": configuration.zero_x_api_url,
        "zero_x_api_key": configuration.zero_x_api_key,
    },
    http_request=aiohttp_http_request,
)

exchange = (
    ZeroXSwapper(
        api_client=api_client,
        chain=chain,
        contract=contract,
        w3=w3,
        configuration={
            "bsc_rpc_url": configuration.bsc_rpc_url,
            "fee_integrator_address": configuration.fee_integrator_address,
            "fee_value_in_percentage": configuration.fee_value_in_percentage,
        },
    )
    if configuration.app_env != "test"
    else TestExchange()
)

engine = create_async_engine(
    f"postgresql+asyncpg://{configuration.database_user}:{configuration.database_password}@{configuration.database_host}:{configuration.database_port}/{configuration.database_name}",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
AsyncSessionLocal = cast(
    type[AsyncSession], sessionmaker(expire_on_commit=False, class_=AsyncSession)
)

holding_repository = BscChainHoldingRepository(
    chain=chain,
)

intended_order_repository = SqlAlchemyIntendedOrderRepository(
    AsyncSessionLocal=AsyncSessionLocal, engine=engine
)
planned_order_repository = SqlAlchemyPlannedOrderRepository(
    AsyncSessionLocal=AsyncSessionLocal, engine=engine
)
confirmed_order_repository = SqlAlchemyConfirmedOrderRepository(
    AsyncSessionLocal=AsyncSessionLocal, engine=engine
)
signable_order_repository = SqlAlchemySignableOrderRepository(
    AsyncSessionLocal=AsyncSessionLocal, engine=engine
)
executed_order_repository = SqlAlchemyExecutedOrderRepository(
    AsyncSessionLocal=AsyncSessionLocal, engine=engine
)

conversation_repository = LangchainPostgresqlConversationRepository(
    date_time=date_time,
    id_generator=id_generator,
    configuration={
        "database_user": configuration.database_user,
        "database_password": configuration.database_password,
        "database_host": configuration.database_host,
        "database_port": configuration.database_port,
        "database_name": configuration.database_name,
    },
)

session_manager = SqlAlchemySessionManager(
    engine=engine, AsyncSessionLocal=AsyncSessionLocal
)

asset_balance_converter = AssetBalanceConverter(exchange=exchange, chain=chain)

small_balance_policy = AbsoluteSmallBalancePolicy(
    {"threshold": configuration.small_balance_threshold}
)

similarity_storage = QdrantLangChainAssetSimilarityRepository(
    {
        "qdrant_url": configuration.qdrant_url,
        "qdrant_port": configuration.qdrant_port,
        "qdrant_grpc_port": configuration.qdrant_grpc_port,
        "qdrant_collection": configuration.qdrant_collection,
        "qdrant_api_key": configuration.qdrant_api_key,
    },
    QdrantClient,
    AsyncQdrantClient,
    QdrantVectorStore,
    OpenAIEmbeddings(
        model=configuration.embedding_provider_model,
        api_key=SecretStr(configuration.embedding_provider_api_key),
    ),
)

token_repository = CoingeckoTokenRepository(
    aiohttp_http_request,
    {
        "coingecko_base_url": configuration.coingecko_base_url,
        "coingecko_api_key": configuration.coingecko_api_key,
    },
)

siwe_manager = SiwePySiweManager()

credential_generator = PyJwtCredentialGenerator(secret_key=configuration.app_secret_key)
