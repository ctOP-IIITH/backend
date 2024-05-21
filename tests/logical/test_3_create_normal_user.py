from tests import client
from app.models.user_types import UserType
import time

def test_create_normal_user():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/create-user",
        json={
            "email": "normal@localhost",
            "password": "normal",
            "username": "normal",
            "user_type": UserType.CUSTOMER.value,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "user created successfully"}
    response = client.post(
        "/user/login", json={"email": "normal@localhost", "password": "normal"}
    )
    assert response.status_code == 200
    response = client.get(
        "/user/profile",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "email": "normal@localhost",
        "username": "normal",
        "user_type": UserType.CUSTOMER.value,
    }