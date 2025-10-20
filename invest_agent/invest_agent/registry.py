from typing import Any, cast
from temporalio.client import Client as TemporalClient

from invest_agent.chain.infrastructure.bsc.transaction_receipt_parser import (
    BscTransactionReceiptParser,
)

from invest_agent.database.infrastructure.sql_alchemy_session_manager import (
    SqlAlchemySessionManager,
)
from invest_agent.investment.order.infrastructure.sql_alchemy_order_repository import (
    SqlAlchemyOrderRepository,
)
from invest_agent.investment.transaction.infrastructure.sql_alchemy_transaction_repository import (
    SqlAlchemyTransactionRepository,
)

from invest_agent.portfolio.posting.infrastructure.sql_alchemy_posting_repository import (
    SqlAlchemyPostingRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from invest_agent.conversation.repository.infrastructure.langchain_sqlite_conversation_repository import (
    LangchainSqliteConversationRepository,
)
from invest_agent.datetime.infrastructure.python_date_time import PythonDateTime
from invest_agent.http.agent_to_agent.infrastructure.aiohttp_agent_to_agent_client import (
    AiohttpAgentToAgentClient,
)
from invest_agent.chain.infrastructure.bsc.nonce_manager import NonceManager
from invest_agent.investment.order.infrastructure.temporal_order_submitter import (
    TemporalOrderSubmitter,
)
from shared.http_request.infrastructure.aiohttp_http_request import AiohttpHttpRequest
from shared.http_request.infrastructure.requests_http_request import RequestsHttpRequest
from shared.id_generator.id_generator import IdGenerator
from shared.random_generator.random_generator import RandomGenerator
from invest_agent.investment.infrastructure.zero_x.zero_x_api_client import (
    ZeroXApiClient,
)
from invest_agent.investment.infrastructure.zero_x.zero_x_swapper import ZeroXSwapper

from uagents.storage import KeyValueStore

from web3 import AsyncWeb3, AsyncHTTPProvider

from invest_agent.chain.infrastructure.bsc.bsc_chain import BscChain
from invest_agent.chain.infrastructure.bsc.bsc_contract import BscContract
from invest_agent.configuration import Configuration
from invest_agent.infrastructure.fetch_ai.storage.fetch_ai_storage import (
    FetchAiStorage,
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

conversation_repository = LangchainSqliteConversationRepository(
    db_path=langgraph_db_path, date_time=date_time, id_generator=id_generator
)

order_submitter = TemporalOrderSubmitter(
    order_repository=order_repository,
    id_generator=id_generator,
    configuration={
        "temporal_host": configuration.temporal_host,
        "temporal_port": configuration.temporal_port,
        "agent_name": configuration.agent_name,
    },
    TemporalClient=TemporalClient,
)

session_manager = SqlAlchemySessionManager(
    engine=engine, AsyncSessionLocal=AsyncSessionLocal
)
