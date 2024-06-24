from tests import client
import time


def test_create_node():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.get(
        "/verticals/all",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    # iterate through each obj in the response
    vertical_id = None
    for obj in response.json():
        if obj["res_short_name"] == "AE-LE":
            vertical_id = obj["id"]
            break

    response = client.post(
        "/nodes/create-node",
        json={
            "lbls": [],
            "sensor_type_id": 1,
            "latitude": 10,
            "longitude": 90,
            "area": "Kakinada",
            "name": "name1"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201  # 201 Created
