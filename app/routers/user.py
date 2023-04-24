import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import models
from app.schemas.projects import Project
from app.schemas.users import UserCreate, User, UserUpdate
from database.database import get_db

logging.basicConfig(filename='app.log', level=logging.DEBUG)

router = APIRouter()


@router.get("/users/", response_model=List[User])
def read_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    logging.info(f"Retrieved all users. Count: {len(users)}")
    return users


@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logging.info(f"Created user. User id: {db_user.id}, User name: {db_user.name}, User email: {db_user.email}")
    return db_user


@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        logging.warning(f"User with id {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logging.info(f"Retrieved user. User id: {db_user.id}, User name: {db_user.name}, User email: {db_user.email}")
    return db_user


@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    logging.info(f"Updated user. User id: {db_user.id}, User name: {db_user.name}, User email: {db_user.email}")
    return db_user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    logging.info(f"Deleted user. User id: {user_id}")
    return {"message": "User deleted successfully"}


@router.get("/users/{user_id}/projects", response_model=List[Project])
def read_user_projects(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    logging.info(f"Retrieved projects of user. User id: {db_user.id}")
    return db_user.projects


@router.get("/users/{user_id}/project_count", response_model=int)
def read_user_project_count(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    project_count = db.query(models.Project).filter(models.Project.owner_id == user_id).count()
    logging.info(f"User {db_user.name} has {project_count} projects")
    return project_count
