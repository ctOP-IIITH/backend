from tests import client
import time

def test_view_all_users():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.get(
        "/user/getusers",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    print(response.json())