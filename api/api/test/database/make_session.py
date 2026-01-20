from typing import cast
from environs import env
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

database_user = env.str("DATABASE_USER")
database_password = env.str("DATABASE_PASSWORD")
database_host = env.str("DATABASE_HOST")
database_port = env.int("DATABASE_PORT")
app_name = env.str("APP_NAME")
app_env = env.str("APP_ENV")

engine = create_async_engine(
    f"postgresql+asyncpg://{database_user}:{database_password}@{database_host}:{database_port}/{app_name}_{app_env}",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
AsyncSessionLocal = cast(
    type[AsyncSession], sessionmaker(expire_on_commit=False, class_=AsyncSession)
)


def make_session() -> AsyncSession:
    return AsyncSessionLocal(bind=engine)
