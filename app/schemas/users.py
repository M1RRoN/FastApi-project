from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserSummary(BaseModel):
    user_id: int
    project_count: int
    image_count: int
