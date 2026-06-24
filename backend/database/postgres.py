from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine


class BasePostgresConnection:
    def __init__(self, user: str, password: str, database: str, host: str):
        self.user = user
        self.password = password
        self.database = database
        self.host = host

    def _create_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:5432/{self.database}"

    def _create_pg_engine(self):
        return create_async_engine(self._create_url())

    @property
    def engine(self):
        if not hasattr(self, "_engine"):
            self._engine = self._create_pg_engine()
        return self._engine

    async def pg_execution(self):
        async with AsyncSession(self.engine) as session:
            yield session
