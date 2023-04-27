import asyncio
from datetime import datetime
from typing import Optional

import sqlalchemy.exc
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import String, ForeignKey, URL, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from starlette.requests import Request


class Base(DeclarativeBase):

    @classmethod
    def from_pd(cls, source: BaseModel, **kwargs):
        target = cls()
        return cls.__update(target, source, **kwargs)

    def __update(self, source: BaseModel, **kwargs):
        source_dict = source.dict(**kwargs)
        for field, value in source_dict.items():
            if hasattr(self, field):
                setattr(self, field, value)
        return self

    def update_fields(self, source: BaseModel, **kwargs):
        return self.__update(source, **kwargs)


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    login: Mapped[str] = mapped_column(String(20), unique=True)


class Item(Base):
    __tablename__ = "item"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    weight: Mapped[float] = mapped_column(default=0.0)
    created: Mapped[Optional[datetime]] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))


# conn_string = "postgresql+psycopg2://login:pass@host:port/dbname?encoding=UTF-8"
conn_string = URL.create(
    drivername="postgresql+asyncpg",
    host="localhost",
    port=5432,
    username="item",
    password="secret",
    database="item"
)

engine = create_async_engine(
    conn_string,
    echo=True,
    connect_args={
        "server_settings": {
            # https://magicstack.github.io/asyncpg/current/api/index.html
            "application_name": "alchemy-demo"
        }
    }
)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


async def get_auth(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Authorization: login
    """
    try:
        login = str(request.headers["Authorization"])
        user_res = await session.execute(select(User).where(User.login == login))
        user_db = user_res.scalar_one()
    except (KeyError, ValueError, sqlalchemy.exc.NoResultFound):
        raise HTTPException(status_code=401, detail="Unauthorized user")
    yield user_db

"""
# https://hub.docker.com/_/postgres#Environment%20Variables
# https://hub.docker.com/_/postgres/tags?page=1&name=alpine
docker run -d -e POSTGRES_PASSWORD=secret -e POSTGRES_USER=item -e POSTGRES_DB=item -p 5432:5432 postgres:alpine
"""


async def create_all_models():
    async with engine.begin() as session:
        await session.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(create_all_models())
