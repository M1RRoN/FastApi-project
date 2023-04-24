import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.models import models
from app.schemas.images import Image
from database.database import get_db

logging.basicConfig(filename='app.log', level=logging.DEBUG)

router = APIRouter()


@router.post(
    "/projects/{project_id}/images/",
    response_model=Image,
    status_code=201
)
def create_image_for_project(
        project_id: int,
        image: UploadFile = File(...),
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
    contents = image.file.read()
    db_image = models.Image(filename=image.filename, project_id=project_id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    with open(f"app/images/{db_image.id}.png", "wb") as f:
        f.write(contents)
    logging.info(f"Image {db_image.id} created for project {project_id}")
    return db_image


@router.get("/images/", response_model=List[Image])
def read_images(
        db: Session = Depends(get_db)
):
    images = db.query(models.Image).all()
    logging.info(f"Retrieved all users. Count: {len(images)}")
    return images


@router.get("/images/{image_id}", response_model=Image)
def read_image(image_id: int, db: Session = Depends(get_db)):
    db_image = (
        db.query(models.Image)
        .filter(models.Image.id == image_id)
        .first()
    )
    if db_image is None:
        logging.error(f"Project with id {image_id} not found")
        raise HTTPException(status_code=404, detail="Image not found")
    logging.info(f"Retrieved image. Image id: {db_image.id}, Image filename: {db_image.filename}")
    return db_image


@router.delete("/images/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    db_image = (
        db.query(models.Image)
        .filter(models.Image.id == image_id)
        .first()
    )
    if db_image is None:
        logging.error(f"Project with id {image_id} not found")
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(db_image)
    db.commit()
    logging.info(f"Image {image_id} deleted")
    return {"detail": "Image deleted successfully"}
