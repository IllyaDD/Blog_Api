from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    first_name: str
    second_name: str


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    second_name: str


class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str] = None
    second_name: Optional[str] = None