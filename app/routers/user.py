import logging
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, create_jwt_token
from app.models import models
from app.schemas.projects import Project
from app.schemas.users import UserCreate, User, UserUpdate, UserWithToken, Token
from database.database import get_db
import jwt


logging.basicConfig(filename='app.log', level=logging.DEBUG)

router = APIRouter()


@router.get("/users/", response_model=List[User])
def read_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    logging.info(f"Retrieved all users. Count: {len(users)}")
    return users


@router.post("/users/", response_model=UserWithToken)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(email=user.email, username=user.username)
    db_user.hashed_password = db_user.get_password_hash(password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logging.info(f"Created user. User id: {db_user.id}, "
                 f"User name: {db_user.username}, "
                 f"User email: {db_user.email}",)
    token = create_jwt_token(db_user.username)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email, "token": token}


@router.post("/login/", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_claims = {"sub": user.username}
    access_token = create_access_token(access_token_claims, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# @router.delete("/logout/")
# async def logout(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
#     db.query(models.Token).filter(models.Token.user_id == current_user.id).delete()
#     db.commit()
#     return {"detail": "Successfully logged out."}
#
#
# @router.get("/users/me")
# def read_users_me(current_user: models.User = Depends(get_current_active_user)):
#     return current_user


@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        logging.warning(f"User with id {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logging.info(f"Retrieved user. User id: {db_user.id}, "
                 f"User name: {db_user.username}, "
                 f"User email: {db_user.email}")
    return db_user


@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.username
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    logging.info(f"Updated user. User id: {db_user.id}, "
                 f"User name: {db_user.username}, "
                 f"User email: {db_user.email}")
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
    project_count = (db.query(models.Project)
                     .filter(models.Project.owner_id == user_id).count()
                     )
    logging.info(f"User {db_user.username} has {project_count} projects")
    return project_count
