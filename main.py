from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db import User, get_session, get_auth, Item
from schemas import UserPost, UserDB, ItemDB, ItemPost, ItemPatch

app = FastAPI()


@app.post("/user", response_model=UserDB)
async def post_user(user: UserPost, session: AsyncSession = Depends(get_session), auth: User = Depends(get_auth)):
    try:
        new_user = User.from_pd(user)
        session.add(new_user)
        await session.flush()  # validate at db level
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Data [{user}] can't be added")

    await session.commit()
    await session.refresh(new_user)
    return new_user


@app.get("/user/{user_id}", response_model=UserDB)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session), auth: User = Depends(get_auth)):
    user_db = await session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail=f"User {user_id} does not exist")
    return user_db


@app.post("/item", response_model=ItemDB)
async def post_item(item: ItemPost, session: AsyncSession = Depends(get_session), auth: User = Depends(get_auth)):
    new_item = Item.from_pd(item)
    new_item.user_id = auth.id
    new_item.created = datetime.now()
    session.add(new_item)
    await session.flush()
    await session.commit()
    await session.refresh(new_item)
    return new_item


@app.patch("/item/{item_id}", response_model=ItemDB)
async def patch_item(item_id: int, item: ItemPatch, session: AsyncSession = Depends(get_session), auth: User = Depends(get_auth)):
    patched_item = await session.get(Item, item_id)
    patched_item.update_fields(item, exclude_unset=True)
    session.add(patched_item)
    await session.flush()
    await session.commit()
    await session.refresh(patched_item)
    return patched_item


if __name__ == '__main__':
    uvicorn.run(app)
