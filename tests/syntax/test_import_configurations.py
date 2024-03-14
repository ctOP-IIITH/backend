from tests import client

import time

def test_get_import_configurations():
    # login as admin and get access token
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.get("/import/import", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

def test_invalid_type_of_request_import_configurations():
    # login as admin and get access token
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post("/import/import", json={"name": "test"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405

    response = client.put("/import/import", json={"name": "test"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405

    response = client.delete("/import/import",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
