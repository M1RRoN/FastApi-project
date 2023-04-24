from pydantic import BaseModel


class ImageBase(BaseModel):
    filename: str


class ImageCreate(ImageBase):
    pass


class Image(ImageBase):
    id: int
    project_id: int

    class Config:
        orm_mode = True
