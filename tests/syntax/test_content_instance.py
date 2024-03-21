from tests import client
import time

# create new vertical
def create_vertical():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/verticals/create-ae",
        json={"ae_name": "test_ae",
               "ae_description": "test_description",
               "ae_short_name": "TE",
               "labels": []
        },
        headers={"Authorization": f"Bearer {access_token}"}, 
    )
    

# create new sensor type
def create_sensor_type():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/sensor-types/create",
        json={"res_name": "test_sensor_type",
               "parameters": ["test_parameter"],
               "data_types": ["test_data_type"],
               "labels": ["test_label"],
               "vertical_id": 1
        },
        headers={"Authorization": f"Bearer {access_token}"}, 
    )

def create_node():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/nodes/create-node",
        json = {
                "lbls": [],
                "sensor_type_id": 1,
                "latitude": 10,
                "longitude": 90,
                "area": "Kakinada"
            },
    )


# test create content instance
def test_create_cin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    create_vertical()
    create_sensor_type()
    create_node()
    response = client.post(
        "/cin/create/1",
        json={},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

def test_create_cin_invalid_node_id():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/cin/create/100",
        json={},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404

def test_create_cin_no_node_id():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/cin/create/",
        json={},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404

def test_invalid_type_of_req_create_cin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    create_vertical()
    create_sensor_type()
    create_node()

    response = client.get(
        "/cin/create/1",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405

    response = client.put(
        "/cin/create/1",
        json={},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405

    response = client.delete(
        "/cin/create/1",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
    

# test delete cin
def test_delete_cin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    create_vertical()
    create_sensor_type()
    create_node()

    response = client.delete(
        "/cin/delete",
        json={
            "cin_id": "TE01-0000-0001",
            "node_id": 1,
            "path": "AE-TE"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

def test_delete_cin_invalid_cin_id():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    create_vertical()
    create_sensor_type()
    create_node()

    response = client.delete(
        "/cin/delete",
        json={
            "cin_id": "TEfd01-0000-0002",
            "node_id": 1,
            "path": "AE-TE"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404

def test_delete_cin_invalid_node_id():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    create_vertical()
    create_sensor_type()
    create_node()

    response = client.delete(
        "/cin/delete",
        json={
            "cin_id": "TE01-0000-0001",
            "node_id": 100,
            "path": "AE-TE"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404

def test_missing_details_delete_cin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    create_vertical()
    create_sensor_type()
    create_node()

    response = client.delete(
        "/cin/delete",
        json={
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

def test_invalid_type_of_req_delete_cin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.get(
        "/cin/delete",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 405

    response = client.put(
        "/cin/delete",
        json={},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 405

    response = client.post(
        "/cin/delete",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 405

    