from tests import client
from app.models.user_types import UserType


def test_create_admin():

    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/create-user",
        json={
            "email": "admin2@localhost",
            "password": "admin2",
            "username": "admin2",
            "user_type": UserType.ADMIN.value,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "user created successfully"}
    response = client.post(
        "/user/login", json={"email": "admin2@localhost", "password": "admin2"}
    )
    assert response.status_code == 200
    response = client.get(
        "/user/profile",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "email": "admin2@localhost",
        "username": "admin2",
        "user_type": UserType.ADMIN.value,
    }
