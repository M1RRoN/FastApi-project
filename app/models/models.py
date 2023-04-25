from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    projects = relationship("Project", back_populates="owner")

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    images = relationship("Image", back_populates="project")


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="images")
