from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


class BasePostgresConnection:
    def __init__(self, user: str, password: str, database: str, host: str):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.engine: AsyncEngine = create_async_engine(self._create_url())

    def _create_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:5432/{self.database}"

    async def get_session(self):
        async with AsyncSession(self.engine) as session:
            yield session
