"""Главный модуль."""
from datetime import datetime, timezone
import sqlalchemy

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db import Item, User, get_auth, get_session
from schemas import ItemDB, ItemPatch, ItemPost, UserDB, UserPost

app = FastAPI()

auth_scheme = HTTPBearer()


@app.post('/user', response_model=UserDB)
async def post_user(
    user_post: UserPost,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_auth),
) -> User:
    """Создание пользователя."""
    try:
        user = User(**user_post.model_dump(exclude_unset=True))
        session.add(user)
        await session.flush()  # validate at db level
    except IntegrityError as ex:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Data [{user}] can't be added") from ex

    await session.commit()
    await session.refresh(user)
    return user


@app.get('/user/{user_id}', response_model=UserDB)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_auth),
) -> User:
    """Получение пользователя."""
    user_db = await session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail=f'User {user_id} does not exist')
    return user_db


@app.post('/item', response_model=ItemDB)
async def post_item(
    item_post: ItemPost,
    session: AsyncSession = Depends(get_session),
    auth: User = Depends(get_auth),
) -> Item:
    """Добавление элемента."""
    item = Item(**item_post.model_dump(exclude_unset=True))
    item.user_id = auth.id
    item.created = datetime.now(timezone.utc)
    item.updated = sqlalchemy.func.now()
    session.add(item)
    await session.flush()
    await session.commit()
    await session.refresh(item)
    return item


@app.patch('/item/{item_id}', response_model=ItemDB)
async def patch_item(
    item_id: int,
    item_patch: ItemPatch,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_auth),
) -> Item:
    """Обновление элемента."""
    item = await session.get_one(Item, item_id)
    for key, value in item_patch.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    item.updated = sqlalchemy.func.now()
    session.add(item)
    await session.flush()
    await session.commit()
    await session.refresh(item)
    return item


if __name__ == '__main__':
    uvicorn.run(app)
