from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from starlette.testclient import TestClient

from app.main import app
from app.models.models import User, Image
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


def test_create_user():
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    response = client.post("/users/", json=data)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == data["username"]
    assert user["email"] == data["email"]
    assert "hashed_password" not in user

    db: Session = next(override_get_db())
    db_user = db.query(User).filter(User.email == data["email"]).first()
    assert db_user is not None
    assert db_user.username == data["username"]
    assert db_user.email == data["email"]
    assert db_user.hashed_password is not None
    assert db_user.hashed_password != data["password"]
    assert db_user.verify_password(data["password"]) is True


def test_read_user():
    # создаем пользователя для теста
    db_user = User(username="testuse2r", email="testuser2@example.com", hashed_password="testhash2")
    db: Session = next(override_get_db())
    db.add(db_user)
    db.commit()

    # делаем запрос на чтение пользователя
    response = client.get(f"/users/{db_user.id}/")
    assert response.status_code == 200

    # проверяем, что полученные данные соответствуют ожидаемым
    user = response.json()
    assert user["username"] == db_user.username
    assert user["email"] == db_user.email
    assert user["id"] == db_user.id


def test_update_user():
    # создаем пользователя для теста
    db_user = User(username="testuser3", email="testuser3@example.com", hashed_password="testhash3")
    db: Session = next(override_get_db())
    db.add(db_user)
    db.commit()

    # делаем запрос на изменение пользователя
    data = {"email": "newemail@example.com"}
    response = client.put(f"/users/{db_user.id}/", json=data)
    assert response.status_code == 200

    # проверяем, что пользователь был изменен
    db.refresh(db_user)
    assert db_user.email == data["email"]


def test_delete_user():
    # создаем пользователя для теста
    db_user = User(username="testuser4", email="testuser4@example.com", hashed_password="testhash4")
    db: Session = next(override_get_db())
    db.add(db_user)
    db.commit()

    # делаем запрос на удаление пользователя
    response = client.delete(f"/users/{db_user.id}/")
    assert response.status_code == 200

    # проверяем, что пользователь был удален
    db_user = db.query(User).filter(User.id == db_user.id).first()
    assert db_user is None


# тесты для роута создания проекта для пользователя
def test_create_project():
    user_data = {
        "email": "testuser1231@example.com",
        "username": "Test User32",
        "password": "testpassword32"
    }
    print(jsonable_encoder(user_data))
    user_response = client.post("/users/", json=user_data)
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]
    project_data = {
        "title": "Test Project",
        "description": "Test Project123",
        "owner": user_id
    }

    project_response = client.post(f"/users/{user_id}/projects/",
                                   json=project_data)
    assert project_response.status_code == 200
    assert project_response.json()["title"] == project_data['title']
    assert project_response.json()["owner_id"] == user_id


def test_get_project():
    user_data = {
        "username": "testuser11",
        "email": "testuser11@example.com",
        "password": "testpassword"
    }
    # Создаем пользователя, чтобы иметь owner_id для проекта
    user_response = client.post("/users/", json=user_data)
    assert user_response.status_code == 200
    user = user_response.json()
    user_id = user["id"]

    # Данные проекта
    project_data = {
        "title": "Test Project",
        "description": "Test Project Description",
        "owner_id": user_id
    }

    # Отправляем запрос на создание проекта
    project_response = client.post(f"/users/{user_id}/projects/", json=project_data)
    assert project_response.status_code == 200
    project = project_response.json()

    # Отправляем запрос на получение проекта
    get_project_response = client.get(f"/projects/{project['id']}/")
    assert get_project_response.status_code == 200
    get_project_data = get_project_response.json()
    assert get_project_data == project


def test_update_project():
    user_data = {
        "username": "testuser10",
        "email": "testuser10@example.com",
        "password": "testpassword2"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == user_data["username"]
    assert user["email"] == user_data["email"]

    project_data = {
        "title": "Test Project",
        "description": "Test Project123",
        "owner_id": user["id"]
    }
    response = client.post(f"/users/{user['id']}/projects/", json=project_data)
    assert response.status_code == 200
    project = response.json()
    assert project["title"] == project_data["title"]
    assert project["description"] == project_data["description"]
    assert project["owner_id"] == project_data["owner_id"]

    update_data = {"title": "Updated Project", "description": "Updated Description"}
    response = client.put(f"/projects/{project['id']}/", json=update_data)
    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["title"] == update_data["title"]
    assert updated_project["description"] == update_data["description"]

    response = client.delete(f"/projects/{project['id']}/")
    assert response.status_code == 200


def test_delete_project():
    user_data = {
        "username": "testuser5",
        "email": "testuser5@example.com",
        "password": "testpassword5"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == user_data["username"]
    assert user["email"] == user_data["email"]

    project_data = {
        "title": "Test Project",
        "description": "Test Project123",
        "owner_id": user["id"]
    }
    response = client.post(f"/users/{user['id']}/projects/", json=project_data)
    assert response.status_code == 200
    project = response.json()
    assert project["title"] == project_data["title"]
    assert project["description"] == project_data["description"]
    assert project["owner_id"] == project_data["owner_id"]

    response = client.delete(f"/projects/{project['id']}/")
    assert response.status_code == 200

    response = client.get(f"/projects/{project['id']}/")
    assert response.status_code == 404


def test_get_project_count():
    user_response = client.post("/users/",
                                json={"username": "Test User234634",
                                      "email": "test34636@example.com",
                                      "password": "test132"})
    user_id = user_response.json()["id"]
    client.post(f"/users/{user_id}/projects/",
                json={"title": "Test Project2",
                      "description": "Test Project2"})
    response = client.get(f"/users/{user_id}/project_count")
    assert response.status_code == 200
    assert response.json() == 1


# тесты для роута добавления изображения в проект пользователя
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
