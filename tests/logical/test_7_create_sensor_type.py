from tests import client
import time


def test_create_sensor_type():
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
        "/sensor-types/create",
        json={
            "res_name": "logical_sensor_type",
            "parameters": ["test_parameter"],
            "data_types": ["str"],
            "labels": ["logic_label"],
            "vertical_id": vertical_id,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    response = client.get(
        "/sensor-types/get/{vertical_id}".format(vertical_id=vertical_id),
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "res_name": "logical_sensor_type",
            "parameters": ["test_parameter"],
            "data_types": ["str"],
            "labels": ["logic_label"],
            "vertical_id": vertical_id,
        }
    ]
