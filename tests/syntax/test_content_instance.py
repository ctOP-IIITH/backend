from tests import client
import time

def test_create_cin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post("/cin/create/1",
        headers={"Authorization": f"Bearer {access_token}"},
        json = {}
    )

    