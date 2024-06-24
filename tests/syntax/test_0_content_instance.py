from tests import client
import time
from app.utils.delete_with_payload import CustomTestClient


# create new sensor type
def create_sensor_type(access_token):
    response = client.post(
        "/sensor-types/create",
        json={
            "res_name": "test_sensor_type",
            "parameters": ["test_parameter"],
            "data_types": ["str"],
            "labels": ["test_label"],
            "vertical_id": 1,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print("HIHIHIHIHIHIHI from create sensor type")
    print(response.json())


def create_node(access_token, name):
    response = client.post(
        "/nodes/create-node",
        json={
            "lbls": [],
            "sensor_type_id": 1,
            "latitude": 10,
            "longitude": 90,
            "area": "Kakinada",
            "name": name
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print(response.json())
    return response.json()


def create_vendor(access_token):
    response = client.post(
        "/user/create-user",
        json={
            "username": "testvendor",
            "email": "vendor@localhost",
            "password": "vendor",
            "user_type": 2,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print("HIHIHIHIHIHIHI from create vendor")
    print(response.json())


def assign_vendor_to_node(node_name, access_token):
    response = client.post(
        "/nodes/assign-vendor",
        json={"node_id": node_name, "vendor_email": "vendor@localhost"},
        headers={"Authorization": f"Bearer {access_token}"},
    )


def get_vendor(node_name, access_token):
    response = client.get(
        "/nodes/get-vendor/" + node_name,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response.json()


# test create content instance
def test_create_cin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    # create_vertical()
    create_sensor_type(access_token)
    node = create_node(access_token, "test_create_cin")
    print("node", node)
    create_vendor(access_token)
    assign_vendor_to_node(node["node_name"], access_token)
    vendor = get_vendor(node["node_name"], access_token)
    print("vendor", vendor)
    response = client.post(
        "/cin/create/" + str(node["token_num"]),
        json={"test_parameter": "test_value"},
        headers={"Authorization": f"Bearer {vendor['api_token']}"},
    )
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
        "/cin/create/100", json={}, headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404


def test_create_cin_no_node_id():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/cin/create/", json={}, headers={"Authorization": f"Bearer {access_token}"}
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
    node = create_node(access_token, "test_invalid_type_of_req_create_cin")
    create_vendor(access_token)
    assign_vendor_to_node(node["node_name"], access_token)
    vendor = get_vendor(node["node_name"], access_token)
    response = client.get(
        "/cin/create/" + str(node["token_num"]),
        headers={"Authorization": f"Bearer {vendor['api_token']}"},
    )
    assert response.status_code == 405

    response = client.put(
        "/cin/create/1", json={}, headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405

    response = client.delete_with_payload(
        "/cin/create/1", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
