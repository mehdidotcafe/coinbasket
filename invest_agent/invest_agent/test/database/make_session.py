from typing import cast
from environs import env
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

agent_env = env.str("AGENT_ENV")
agent_name = env.str("AGENT_NAME")


db_path = f"./database/{agent_env}/{agent_name}.db"

engine = create_async_engine(
    f"sqlite+aiosqlite:///{db_path}",
    connect_args={"check_same_thread": False, "timeout": 60},
    poolclass=StaticPool,
)
AsyncSessionLocal = cast(
    type[AsyncSession], sessionmaker(expire_on_commit=False, class_=AsyncSession)
)


def make_session() -> AsyncSession:
    return AsyncSessionLocal(bind=engine)
