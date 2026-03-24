from datetime import datetime

import pytest
from app.core.dependencies import get_current_user
from app.models import Users
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import json

from app.main import app
from app.db.connection import get_db

DATABASE_URL = "postgresql+asyncpg://test:test@postgres_test:5432/db_test"

@pytest.fixture
async def engine():
    engine = create_async_engine(DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def run_migrations():
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        DATABASE_URL
    )
    command.upgrade(alembic_cfg, "head")


@pytest.fixture
async def db_session(engine, run_migrations):
    async with engine.connect() as conn:
        transaction = await conn.begin()

        session = AsyncSession(bind=conn)
        await session.begin_nested()
        yield session

        await session.close()
        await transaction.rollback()


@pytest.fixture
def fake_redis():
    class FakeRedis:
        async def get(self, key):
            return json.dumps({
                "access_token": "fake",
                "refresh_token": "fake",
                "id_token": "fake"
            })

    return FakeRedis()

@pytest.fixture(autouse=True)
def force_public_auth():
    for route in app.routes:
        if hasattr(route, "endpoint"):
            setattr(route.endpoint, "auth_mode", "public")


@pytest.fixture
def override_user(db_session):
    async def user():
        return await db_session.get(Users,1)

    return user

@pytest.fixture
async def client(db_session, fake_redis, override_user):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_user


    app.state.redis = fake_redis

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        cookies={"session_id": "test"}
    ) as c:
        yield c

    app.dependency_overrides.clear()