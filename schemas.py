from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserPost(BaseModel):
    login: str
    name: str


class UserDB(UserPost):
    id: int

    class Config:
        orm_mode = True


class ItemPost(BaseModel):
    title: str
    weight: float


class ItemPatch(BaseModel):
    title: Optional[str]
    weight: Optional[float]
    created: Optional[datetime]
    user_id: Optional[int]


class ItemDB(ItemPost):
    id: int
    created: datetime
    user_id: int

    class Config:
        orm_mode = True
