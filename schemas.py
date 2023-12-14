"""Модуль схем."""
from datetime import datetime, timezone
import logging
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

logger = logging.getLogger(__name__)


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
    """Элемент переданный в PATCH-запросе."""

    title: Optional[str] = None
    weight: Optional[float]
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    user_id: Optional[int] = None


class ItemDB(ItemPost):
    """Элемент из БД."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created: datetime
    updated: datetime
    user_id: int
