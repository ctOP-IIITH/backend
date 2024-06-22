from tests import client
from app.models.user_types import UserType
import time

def test_create_vendor():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.post(
        "/user/create-user",
        json={
            "email": "vendor1@localhost",
            "password": "vendor",
            "username": "vendor",
            "user_type": UserType.VENDOR.value,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "user created successfully"}

    response = client.post(
        "/user/login", json={"email": "vendor1@localhost", "password": "vendor"}
    )
    assert response.status_code == 200
    response = client.get(
        "/user/profile",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "email": "vendor1@localhost",
        "username": "vendor",
        "user_type": UserType.VENDOR.value,
    }