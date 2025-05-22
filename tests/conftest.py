import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.app.main import app
from src.app.core.db import get_db, Base # Base is needed for metadata
from src.app.core.config import settings

# --- Test Database Setup ---
TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"

test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

async def override_get_db() -> AsyncSession: # type: ignore
    async with TestingSessionLocal() as session:
        yield session

# --- Fixtures ---
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Set up the test database: drop all tables, create all tables.
    This runs once per session.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown: drop tables after all tests in the session are done
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(setup_test_db): # setup_test_db ensures DB is ready
    """
    Provides an AsyncClient for making HTTP requests to the FastAPI app.
    Overrides the 'get_db' dependency for the duration of the test.
    """
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear() # Clean up overrides
    
# Note: The original db_url in settings is not modified here, as test_engine uses TEST_DATABASE_URL.
# The main application's engine (if used directly by some non-overridden part) would still point to the original DB.
# However, all API endpoints should use the overridden get_db.
