from typing import cast
from api.authentication.credential.infrastructure.py_jwt_credential_generator import (
    PyJwtCredentialGenerator,
)
from api.authentication.siwe.infrastructure.siwe_py_siwe_manager import (
    SiwePySiweManager,
)
from api.investment.infrastructure.test_exchange import TestExchange
from api.portfolio.holding.infrastructure.bsc_chain_holding_repository import (
    BscChainHoldingRepository,
)
from pydantic import SecretStr
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from langchain_openai import OpenAIEmbeddings

from api.investment.calculator.asset_balance_converter import (
    AssetBalanceConverter,
)
from api.portfolio.small_balance.absolute_small_balance_policy import (
    AbsoluteSmallBalancePolicy,
)
from temporalio.client import Client as TemporalClient

from api.chain.infrastructure.bsc.transaction_receipt_parser import (
    BscTransactionReceiptParser,
)

from api.database.infrastructure.sql_alchemy_session_manager import (
    SqlAlchemySessionManager,
)
from api.investment.order.infrastructure.sql_alchemy_order_repository import (
    SqlAlchemyOrderRepository,
)
from api.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    SqlAlchemyTransactionRepository,
)

from api.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    SqlAlchemyPostingRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.conversation.repository.infrastructure.langchain_sqlite_conversation_repository import (
    LangchainSqliteConversationRepository,
)
from api.datetime.infrastructure.python_date_time import PythonDateTime
from api.chain.infrastructure.bsc.nonce_manager import NonceManager
from api.investment.order.infrastructure.temporal_order_submitter import (
    TemporalOrderSubmitter,
)
from api.shared.http_request.infrastructure.aiohttp_http_request import (
    AiohttpHttpRequest,
)
from api.shared.http_request.infrastructure.requests_http_request import (
    RequestsHttpRequest,
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

from api.similarity.infrastructure.qdrant_langchain.similarity_storage.qdrant_langchain_similarity_storage import (
    QdrantLangChainSimilarityStorage,
)
from api.token.infrastructure.coingecko.coingecko_token_repository import (
    CoingeckoTokenRepository,
)

date_time = PythonDateTime()

date_time = PythonDateTime()


configuration = Configuration()

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

random_generator = RandomGenerator()

api_client = ZeroXApiClient(
    configuration={
        "zero_x_api_url": configuration.zero_x_api_url,
        "zero_x_api_key": configuration.zero_x_api_key,
    },
    http_request=requests_http_request,
)

exchange = (
    ZeroXSwapper(
        api_client=api_client,
        chain=chain,
        contract=contract,
        w3=w3,
        configuration={
            "bsc_rpc_url": configuration.bsc_rpc_url,
            "private_key": configuration.bsc_private_key,
        },
    )
    if configuration.app_env != "test"
    else TestExchange()
)

langgraph_db_path = (
    f"./database/{configuration.app_env}/{configuration.app_name}.langgraph.db"
)

engine = create_async_engine(
    f"postgresql+asyncpg://{configuration.database_user}:{configuration.database_password}@{configuration.database_host}:{configuration.database_port}/{configuration.app_name}",
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
holding_repository = BscChainHoldingRepository(
    chain=chain,
)

conversation_repository = LangchainSqliteConversationRepository(
    db_path=langgraph_db_path, date_time=date_time, id_generator=id_generator
)

order_submitter = TemporalOrderSubmitter(
    order_repository=order_repository,
    id_generator=id_generator,
    configuration={
        "temporal_host": configuration.temporal_host,
        "temporal_port": configuration.temporal_port,
        "app_name": configuration.app_name,
    },
    TemporalClient=TemporalClient,
)

session_manager = SqlAlchemySessionManager(
    engine=engine, AsyncSessionLocal=AsyncSessionLocal
)

asset_balance_converter = AssetBalanceConverter(exchange=exchange, chain=chain)

small_balance_policy = AbsoluteSmallBalancePolicy(
    {"threshold": configuration.small_balance_threshold}
)

similarity_storage = QdrantLangChainSimilarityStorage(
    {
        "qdrant_url": configuration.qdrant_url,
        "qdrant_port": configuration.qdrant_port,
        "qdrant_grpc_port": configuration.qdrant_grpc_port,
        "qdrant_collection": configuration.qdrant_collection,
        "qdrant_api_key": configuration.qdrant_api_key,
    },
    QdrantClient,
    QdrantVectorStore,
    OpenAIEmbeddings(
        model=configuration.embedding_provider_model,
        api_key=SecretStr(configuration.embedding_provider_api_key),
    ),
)

token_repository = CoingeckoTokenRepository(
    requests_http_request,
    {
        "coingecko_base_url": configuration.coingecko_base_url,
        "coingecko_api_key": configuration.coingecko_api_key,
    },
)

siwe_manager = SiwePySiweManager()

credential_generator = PyJwtCredentialGenerator(secret_key=configuration.app_secret_key)
