"""Модуль схем."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserPost(BaseModel):
    """Пользователь."""

    login: str
    name: str


class UserDB(UserPost):
    """Пользователь из БД."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class ItemPost(BaseModel):
    """Элемент переданный в POST-запросе."""

    title: str
    weight: float


class ItemPatch(BaseModel):
    """Элемент переданный в PATHCH-запросе."""

    title: Optional[str]
    weight: Optional[float]
    created: Optional[datetime]
    user_id: Optional[int]


class ItemDB(ItemPost):
    """Элемент из БД."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created: datetime
    user_id: int
