from tests.test_main import client


def test_create_project():
    user_data = {
        "email": "testuser1231@example.com",
        "username": "Test User32",
        "password": "testpassword32"
    }
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
    user_response = client.post("/users/", json=user_data)
    assert user_response.status_code == 200
    user = user_response.json()
    user_id = user["id"]

    project_data = {
        "title": "Test Project",
        "description": "Test Project Description",
        "owner_id": user_id
    }

    project_response = client.post(f"/users/{user_id}/projects/", json=project_data)
    assert project_response.status_code == 200
    project = project_response.json()

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
