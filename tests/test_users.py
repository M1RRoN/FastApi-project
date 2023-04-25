from sqlalchemy.orm import Session

from app.models.models import User
from tests.test_main import client, override_get_db


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
    db_user = User(
        username="testuse2r",
        email="testuser2@example.com",
        hashed_password="testhash2"
    )
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
    db_user = User(
        username="testuser3",
        email="testuser3@example.com",
        hashed_password="testhash3"
    )
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
    db_user = User(
        username="testuser4",
        email="testuser4@example.com",
        hashed_password="testhash4"
    )
    db: Session = next(override_get_db())
    db.add(db_user)
    db.commit()

    # делаем запрос на удаление пользователя
    response = client.delete(f"/users/{db_user.id}/")
    assert response.status_code == 200

    # проверяем, что пользователь был удален
    db_user = db.query(User).filter(User.id == db_user.id).first()
    assert db_user is None
