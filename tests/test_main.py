import factory
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.testing import db
from starlette.testclient import TestClient

from app.main import app
from app.models.models import User, Project
from database.database import Base, get_db

SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    name = factory.Faker('name')
    email = factory.Faker('email')


class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Project

    title = factory.Faker('sentence')
    description = factory.Faker('text')
    owner = factory.SubFactory(UserFactory)


def test_create_user():
    user_data = UserFactory.build()
    response = client.post("/users/", json=jsonable_encoder(user_data))
    assert response.status_code == 200
    assert response.json()["name"] == user_data.name
    assert response.json()["email"] == user_data.email


# тесты для роута создания проекта для пользователя
def test_create_project():
    user_data = UserFactory.build()
    project_data = {"title": "Test Project", "description": "Test Project123", "owner": jsonable_encoder(user_data)}
    user_response = client.post("/users/", json=jsonable_encoder(user_data))
    user_id = user_response.json()["id"]

    project_response = client.post(f"/users/{user_id}/projects/",
                                   json=project_data)
    assert project_response.status_code == 200
    assert project_response.json()["title"] == project_data['title']
    assert project_response.json()["owner_id"] == user_id


# тесты для роута добавления изображения в проект пользователя
def test_create_image_for_project():
    user_response = client.post("/users/", json={"name": "Test User", "email": "test1@example.com"})
    user_id = user_response.json()["id"]

    project_response = client.post(f"/users/{user_id}/projects/", json={"title": "Test Project2", "description": "Test Project2"})
    project_id = project_response.json()["id"]

    image = ("test_image.png", open("tests/test_image.png", "rb"))

    response = client.post(f"/projects/{project_id}/images/", files={"image": image})
    assert response.status_code == 201
    assert response.json()["filename"] == "test_image.png"
    assert response.json()["project_id"] == project_id


def test_get_project_count():
    user_response = client.post("/users/", json={"name": "Test User234634", "email": "test34636@example.com"})
    user_id = user_response.json()["id"]
    client.post(f"/users/{user_id}/projects/", json={"title": "Test Project2", "description": "Test Project2"})
    response = client.get(f"/users/{user_id}/project_count")
    assert response.status_code == 200
    assert response.json() == 1


def test_get_image_count():
    response = client.get("/images/")
    assert response.status_code == 200
    assert len(response.json()) == 1
