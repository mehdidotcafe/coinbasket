from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

NullableSession = AsyncSession | None

class SqlAlchemyBaseRepository:
    engine: AsyncEngine
    AsyncSessionLocal: type[AsyncSession]

    @asynccontextmanager
    async def get_session(self, session: NullableSession):
        if session is not None:
            yield session
        else:
            async with self.AsyncSessionLocal(bind=self.engine) as session:
                async with session.begin():
                    try:
                        yield session
                    except Exception:
                        # Session will automatically rollback on exception
                        raise
