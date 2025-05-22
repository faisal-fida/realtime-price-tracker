from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from src.app.core.config import settings

DATABASE_URL = str(settings.DATABASE_URL) # Ensure it's a string

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

async def get_db() -> AsyncSession: # type: ignore
    async with AsyncSessionLocal() as session:
        yield session
