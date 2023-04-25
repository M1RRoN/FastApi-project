from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[str]


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserSummary(BaseModel):
    user_id: int
    project_count: int
    image_count: int
