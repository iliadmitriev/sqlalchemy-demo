import asyncio
from datetime import datetime
from typing import AsyncGenerator, Optional

import sqlalchemy.exc
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import URL, DateTime, ForeignKey, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from starlette.requests import Request


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    login: Mapped[str] = mapped_column(String(20), unique=True)


class Item(Base):
    __tablename__ = 'item'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    weight: Mapped[float] = mapped_column(default=0.0)
    created: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))


# conn_string = 'postgresql+psycopg2://login:pass@host:port/dbname?encoding=UTF-8'
conn_string = URL.create(
    drivername='postgresql+asyncpg',
    host='localhost',
    port=5432,
    username='item',
    password='secret',
    database='item',
)

engine = create_async_engine(
    conn_string,
    echo=True,
    connect_args={
        'server_settings': {
            # https://magicstack.github.io/asyncpg/current/api/index.html
            'application_name': 'alchemy-demo'
        }
    },
)

auth_scheme = HTTPBearer()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Создание сессии."""
    async with AsyncSession(engine) as session:
        yield session


async def get_auth(
    _: Request,
    session: AsyncSession = Depends(get_session),
    login: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> AsyncGenerator[User, None]:
    """Authorization: login."""
    try:
        user_res = await session.execute(select(User).where(User.login == login.credentials))
        user_db = user_res.scalar_one()
        yield user_db
    except (KeyError, ValueError, sqlalchemy.exc.NoResultFound) as ex:
        raise HTTPException(status_code=401, detail="Unauthorized user") from ex


_ = """
https://hub.docker.com/_/postgres#Environment%20Variables
https://hub.docker.com/_/postgres/tags?page=1&name=alpine
docker run -d -e POSTGRES_PASSWORD=secret -e POSTGRES_USER=item -e POSTGRES_DB=item -p 5432:5432 postgres:alpine
"""


async def create_all_models() -> None:
    """Создать таблицы и юзера."""
    async with engine.begin() as session:
        await session.run_sync(Base.metadata.drop_all)

    async with engine.begin() as session:
        await session.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        session.add(User(login='user', name='username'))
        await session.commit()


if __name__ == '__main__':
    asyncio.run(create_all_models())
