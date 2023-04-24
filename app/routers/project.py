import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import models
from app.schemas.projects import Project, ProjectCreate, ProjectUpdate
from database.database import get_db

logging.basicConfig(filename='app.log', level=logging.DEBUG)

router = APIRouter()


@router.post("/users/{user_id}/projects/", response_model=Project)
def create_project_for_user(
        user_id: int, project: ProjectCreate, db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        logging.error(f"User with id {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    db_project = models.Project(title=project.title, description=project.description, owner_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    logging.info(f"Project with id {db_project.id} created by user {user_id}")
    return db_project


@router.get("/projects/{project_id}", response_model=Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id)
        .first()
    )
    if db_project is None:
        logging.error(f"Project with id {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    logging.info(f"Project with id {project_id} read")
    return db_project


@router.put("/projects/{project_id}", response_model=Project)
def update_project(project_id: int,
                   project: ProjectUpdate,
                   db: Session = Depends(get_db)
                   ):
    db_project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id)
        .first()
    )
    if db_project is None:
        logging.error(f"Project with id {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    update_data = project.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    logging.info(f"Project with id {project_id} updated")
    return db_project


@router.delete("/projects/{project_id}", response_model=Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id)
        .first()
    )
    if db_project is None:
        logging.error(f"Project with id {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    logging.info(f"Project with id {project_id} deleted.")
    return db_project


@router.get("/users/{user_id}/project_count")
def get_user_project_count(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        logging.error(f"Project with id {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logging.info(f"Project with id {user_id} deleted.")
    return {"project_count": len(user.projects)}
