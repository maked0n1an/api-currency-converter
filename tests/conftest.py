from typing import Any, TypedDict

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from typing_extensions import NotRequired

from main import app
from src.api.dependencies.dependencies import get_session_maker
from src.core.config import db_settings
from src.db.database import Base
from src.db.models import User
from src.utils.password import PasswordHasher


@pytest.fixture(scope="session")
async def engine():
    async_engine = create_async_engine(
        db_settings.TEST_DATABASE_URL, echo=False, poolclass=NullPool
    )

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def test_session_maker(engine: AsyncEngine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture()
async def session(test_session_maker):
    async with test_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
async def clean_tables(engine: AsyncEngine):
    async with engine.connect() as connection:
        for table in Base.metadata.sorted_tables:
            await connection.execute(table.delete())
        await connection.commit()
    yield


@pytest.fixture()
async def client(test_session_maker):
    app.dependency_overrides[get_session_maker] = lambda: test_session_maker

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# Fixtures for testing
class TestUser(TypedDict):
    email: str
    username: str
    password: str

    cookies: NotRequired[dict[str, str]]
    headers: NotRequired[dict[str, str]]


@pytest.fixture(scope="session")
def test_user_data() -> TestUser:
    new_user = TestUser(
        email="user@example.com",
        username="testuser",
        password="_TestPassword87!",
        headers={"X-Device-ID": "test-device"},
    )
    return new_user


@pytest.fixture(scope="session")
def db_user() -> dict[str, str]:
    return {
        "email": "user@example.com",
        "username": "testuser",
        "hashed_password": PasswordHasher.hash("_TestPassword87!"),
    }


@pytest.fixture
async def create_user_in_db(session: AsyncSession):
    async def _create_user(**kwargs: Any) -> User:
        user = User(**kwargs)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    return _create_user


@pytest.fixture()
async def authed_user(
    client: AsyncClient,
    create_user_in_db,
    db_user: dict[str, str],
    test_user_data: TestUser,
) -> TestUser:
    await create_user_in_db(**db_user)

    response = await client.post(
        url="/api/auth/login",
        json={"username": "testuser", "password": "_TestPassword87!"},
        headers={"X-Device-ID": "test-device"},
    )
    tokens = response.json()

    return TestUser(
        email=test_user_data["email"],
        username=test_user_data["username"],
        password=test_user_data["password"],
        headers={
            "X-Device-ID": test_user_data["headers"]["X-Device-ID"],
            "Authorization": f"Bearer {tokens['access_token']}",
            "X-CSRF-Token": response.cookies.get("csrf_token"),
        },
        cookies={
            "csrf_token": response.cookies.get("csrf_token"),
            "refresh_token": response.cookies.get("refresh_token"),
        },
    )
