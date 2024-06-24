from tests import client
from app.utils.delete_with_payload import CustomTestClient

import pytest

import time


def test_create_ae():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]

    # checking if error comes if ae_short_name size is > 2
    response = client.post(
        "/verticals/create-ae",
        json={
            "ae_name": "test-vertical",
            "ae_description": "testing purpose",
            "ae_short_name": "tst",
            "labels": [],
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # checking if error comes if ae_short_name size is < 2
    response = client.post(
        "/verticals/create-ae",
        json={
            "ae_name": "test-vertical",
            "ae_description": "testing purpose",
            "ae_short_name": "t",
            "labels": [],
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # checking if error comes when json data is missing
    response = client.post(
        "/verticals/create-ae",
        json={},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # checking if error comes when json object value is not in the given format
    response = client.post(
        "/verticals/create-ae",
        json={
            "ae_name": "test-vertical",
            "ae_description": "testing purpose",
            "ae_short_name": "ts",
            "labels": 0,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # checking if vertical is created or not with a unique name
    response = client.post(
        "/verticals/create-ae",
        json={
            "ae_name": "test-vertical",
            "ae_description": "testing purpose",
            "ae_short_name": "ts",
            "labels": [],
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    assert response.json() == {"detail": "AE created"}

    # checking if error comes when vertical of existing name gets created.
    response = client.post(
        "/verticals/create-ae",
        json={
            "ae_name": "test-vertical",
            "ae_description": "testing purpose",
            "ae_short_name": "ts",
            "labels": [],
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "AE already exists"}


def test_get_all_ae():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]

    # Create one vertical and check if that information we got in the response of this getall_verticals api
    response = client.post(
        "/verticals/create-ae",
        json={
            "ae_name": "test_get_all_vertical",
            "ae_description": "testing get-all verticals",
            "ae_short_name": "tv",
            "labels": [],
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201

    response = client.get(
        "/verticals/all",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    found = False
    print(response.json())
    for obj in response.json():
        if (
            obj["res_name"] == "test_get_all_vertical"
            and obj["description"] == "testing get-all verticals"
            and obj["res_short_name"] == "AE-tv"
            and obj["labels"] == ["test_get_all_vertical"]
        ):
            found = True
            break

    assert found == True


def test_delete_ae():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]

    # test invalid vertical id format (string)
    response = client.delete_with_payload(
        "/verticals/delete-ae/test",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # test invalid vertical id format (list)
    response = client.delete_with_payload(
        "/verticals/delete-ae/[]",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # test invalid vertical id format (dictionary)
    response = client.delete_with_payload(
        "/verticals/delete-ae/{}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # test invalid vertical id format (float)
    response = client.delete_with_payload(
        "/verticals/delete-ae/1.5",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # test vertical id that dont exist even thogh it is a integer
    response = client.delete_with_payload(
        "/verticals/delete-ae/0",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "AE not found"}

    # checking if vertical id exists and if it has no nodes, it get's deleted
    response = client.get(
        "/verticals/all",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    id = 0
    for obj in response.json():
        if (
            obj["res_name"] == "test-vertical"
            and obj["description"] == "testing purpose"
            and obj["res_short_name"] == "AE-ts"
        ):
            id = obj["id"]
            break

    assert id != 0

    response = client.delete_with_payload(
        f"/verticals/delete-ae/{id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204

    # checking if vertical id exists and if it has nodes, it's not getting deleted
    ## 1. Create vertical
    response = client.post(
        "/verticals/create-ae",
        json={
            "ae_name": "test-vertical",
            "ae_description": "testing purpose",
            "ae_short_name": "ts",
            "labels": [],
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201

    ## 2. Get the vertical id
    response = client.get(
        "/verticals/all",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    id = 0
    for obj in response.json():
        if (
            obj["res_name"] == "test-vertical"
            and obj["description"] == "testing purpose"
            and obj["res_short_name"] == "AE-ts"
        ):
            id = obj["id"]
            break

    assert id != 0

    ## 3. Create sensor type
    response = client.post(
        "sensor-types/create",
        json={
            "res_name": "test-sensor",
            "parameters": ["string"],
            "data_types": ["string"],
            "labels": [],
            "vertical_id": id,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    ## 4. Get the sensor id
    response = client.get(
        f"/sensor-types/get/{id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    sensor_id = 0
    for obj in response.json():
        if obj["res_name"] == "test-sensor":
            sensor_id = obj["id"]
            break

    assert sensor_id != 0

    ## 5. Create node
    response = client.post(
        "nodes/create-node",
        json={
            "lbls": [],
            "sensor_type_id": sensor_id,
            "latitude": 0.22,
            "longitude": 0.3,
            "area": "string",
            "name":"Hello"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201

    ## 6. Now delete vertical should not work as it has nodes
    response = client.delete_with_payload(
        f"/verticals/delete-ae/{id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "AE has nodes. Delete nodes first"}
