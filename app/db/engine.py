from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator
from app.config import Settings

settings = Settings()
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG, #i do know what this is : Prints SQL queries on console
    pool_size=5, #Idk what this is
    max_overflow=10 #idk what this is either :)
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise