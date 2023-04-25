from sqlalchemy.orm import Session

from app.models.models import Image
from tests.test_main import client, override_get_db


def test_create_image_for_project():
    user_response = client.post("/users/",
                                json={"username": "Test User6",
                                      "email": "test16@example.com",
                                      "password": "123"})
    user_id = user_response.json()["id"]

    project_response = client.post(f"/users/{user_id}/projects/",
                                   json={"title": "Test Project2",
                                         "description": "Test Project2"})
    project_id = project_response.json()["id"]

    image = ("test_image.png", open("tests/test_image.png", "rb"))

    response = client.post(f"/projects/{project_id}/images/", files={"image": image})
    assert response.status_code == 201
    assert response.json()["filename"] == "test_image.png"
    assert response.json()["project_id"] == project_id


def test_read_images():
    db: Session = next(override_get_db())
    test_image = Image(filename='test_image5.png', project_id=1)
    db.add(test_image)
    db.commit()

    response = client.get("/images/")
    assert response.status_code == 200
    images = response.json()
    assert len(images) == 2
    assert images[1]['id'] == test_image.id


def test_read_image():
    db: Session = next(override_get_db())
    test_image = Image(filename='test_image2.png', project_id=2)
    db.add(test_image)
    db.commit()

    response = client.get(f"/images/{test_image.id}")
    assert response.status_code == 200
    image = response.json()
    assert image['id'] == test_image.id


def test_delete_image():
    db: Session = next(override_get_db())
    test_image = Image(filename='test_image3.png', project_id=2)
    db.add(test_image)
    db.commit()

    response = client.delete(f"/images/{test_image.id}")
    assert response.status_code == 200

    db_image = db.query(Image).filter(Image.id == test_image.id).first()
    assert db_image is None


def test_get_image_count():
    response = client.get("/images/")
    print(response)
    assert response.status_code == 200
    assert len(response.json()) == 3
