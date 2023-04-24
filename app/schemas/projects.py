from typing import Optional

from pydantic import BaseModel


class ProjectBase(BaseModel):
    title: str
    description: str


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]


class Project(ProjectBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
