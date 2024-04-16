from tests import client
import time
from app.utils.delete_with_payload import CustomTestClient
    

# create new sensor type
def create_sensor_type(access_token):
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
    print("HIHIHIHIHIHIHI from create sensor type")
    print(response.json())

def create_node(access_token):
    response = client.post(
        "/nodes/create-node",
        json = {
                "lbls": [],
                "sensor_type_id": 1 ,
                "latitude": 10,
                "longitude": 90,
                "area": "Kakinada"
            },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print("HIHIHIHIHIHIHI from create node")
    print(response.json())

def create_vendor(access_token):
    response = client.post(
        "/user/create-user",
        json = {
                "username": "testvendor",
                "email": "vendor@localhost",
                "password": "vendor",
                "user_type": 2
            },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print("HIHIHIHIHIHIHI from create vendor")
    print(response.json())

def assign_vendor_to_node(access_token):
    response = client.post(
        "/nodes/assign-vendor", json={"node_id": "WQ01-0000-0001",
                                        "vendor_email": "vendor@localhost"},    
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print("HIHIHIHIHIHIHI from assign vendor to node")
    print(response.json())


# test create content instance
def test_create_cin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    # create_vertical()
    create_sensor_type(access_token)
    create_node(access_token)
    create_vendor(access_token)
    assign_vendor_to_node(access_token)
    response = client.post(
        "/cin/create/1",
        json={},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print("HIHIHIHIHIHIHI")
    print(response.json())
    print(response.status_code)
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
    # create_vertical()
    create_sensor_type(access_token)
    create_node(access_token)
    create_vendor(access_token)
    assign_vendor_to_node(access_token)
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

    response = client.delete_with_payload(
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
    # create_vertical()
    create_sensor_type(access_token)
    create_node(access_token)
    create_vendor(access_token)
    assign_vendor_to_node(access_token)

    response = client.delete_with_payload(
        "/cin/delete",
        json={
            "cin_id": "WQ01-0000-0001",
            "node_id": "1",
            "path": "AE-WQ"
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
    # create_vertical()
    create_sensor_type(access_token)
    create_node(access_token)
    create_vendor(access_token)
    assign_vendor_to_node(access_token)

    response = client.delete_with_payload(
        "/cin/delete",
        json={
            "cin_id": "TEfd01-0000-0002",
            "node_id": "1",
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
    # create_vertical()
    create_sensor_type(access_token)
    create_node(access_token)
    create_vendor(access_token)
    assign_vendor_to_node(access_token)

    response = client.delete_with_payload(
        "/cin/delete",
        json={
            "cin_id": "TE01-0000-0001",
            "node_id": "100",
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
    # create_vertical()
    create_sensor_type(access_token)
    create_node(access_token)
    create_vendor(access_token)
    assign_vendor_to_node(access_token)

    response = client.delete_with_payload(
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

    