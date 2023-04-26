from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str = Field(alias="password")


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


class UserWithToken(User):
    token: str


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: str
