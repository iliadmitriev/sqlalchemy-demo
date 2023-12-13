import asyncio
from unittest import mock

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


@pytest.fixture(scope="session")
async def get_conn_url():
    return URL.create(
        drivername="postgresql+asyncpg",
        host="localhost",
        port=5433,
        username="item",
        password="secret",
        database="item",
    )


@pytest.fixture(scope="session")
async def get_engine(get_conn_url: URL):
    engine = create_async_engine(
        get_conn_url,
        connect_args={"server_settings": {"application_name": "alchemy-demo-test"}},
    )
    with mock.patch("sqlalchemy.ext.asyncio.create_async_engine") as patched_engine:
        patched_engine.return_value = engine
        from db import Base

        async with engine.begin() as session:
            await session.run_sync(Base.metadata.create_all)

        yield engine

        async with engine.begin() as session:
            await session.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def add_some_users(get_engine):
    from db import User

    test_users = [
        User(name="user1", login="user1"),
        User(name="user2", login="user2"),
        User(name="user3", login="user3"),
    ]
    async with AsyncSession(get_engine, expire_on_commit=False) as session:
        session.add_all(test_users)
        await session.flush()
        await session.commit()
        yield test_users


@pytest.fixture(scope="session")
async def get_app(get_engine):
    from main import app

    async with LifespanManager(app):
        yield app


@pytest.fixture(scope="session")
async def get_client(get_app, get_engine):
    async with AsyncClient(app=get_app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop()

    yield loop
    loop.close()
