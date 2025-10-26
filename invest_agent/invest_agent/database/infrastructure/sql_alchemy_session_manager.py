from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

class SqlAlchemySessionManager:
    """
    Manages database sessions and transaction boundaries.
    Use this to control when transactions start and commit.
    """
    
    def __init__(self, engine: AsyncEngine, AsyncSessionLocal: type[AsyncSession]):
        self.engine = engine
        self.AsyncSessionLocal = AsyncSessionLocal
    
    @asynccontextmanager
    async def session(self):
        """
        Create a new session with transaction management.
        
        Usage:
            async with session_manager.session() as session:
                await repo.create_order(session, order)
                await repo.add_order_try(session, order_id, try_)
                # Commits on successful exit, rolls back on exception
        """
        async with self.AsyncSessionLocal(bind=self.engine) as session:
            async with session.begin():
                try:
                    yield session
                except Exception:
                    # Session will automatically rollback on exception
                    raise