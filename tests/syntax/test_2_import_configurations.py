from tests import client
from app.utils.delete_with_payload import CustomTestClient
import json
import time
import pytest

with open('../import-template.json', 'r') as f:
    template_body = json.load(f)


def test_valid_bulk_import():
    # login as admin and get access token
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post("/import/import", json =template_body, headers={"Authorization": f"Bearer {access_token}"})
    print(response)
    # assert 1 == 2 # for confirmation
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
    nodes = {
    "nodes": [
        {
            "latitude": 17.446919,
            "area": "Gachibowli",
            "name": "Name_1"
        },
        {
            "latitude": 52.446919,
            "longitude": 12.612,
            "name": "Name_2"

        }
    ]
    }
    with pytest.raises(KeyError, match='sensor_type'):
        response = client.post("/import/import", json=nodes, headers={"Authorization": f"Bearer {access_token}"})
        print(response)
    
def test_five_thousand_nodes():
    # login as admin and get access token
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    nodes = {
    "nodes": [0] * 5001
    }
    response = client.post("/import/import", json=nodes, headers={"Authorization": f"Bearer {access_token}"})
    recvd_error = response.json()['error']
    expected_error =  'Import less than 5000 nodes at one time!'
    assert recvd_error == expected_error
        
def test_invalid_payload():
    # login as admin and get access token
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    nodes = {
    "NOT_OK": [0] * 5001
    }
    response = client.post("/import/import", json=nodes,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    recvd_error = response.json()['error']
    expected_error =  "Missing 'nodes' key in the JSON payload"
    assert recvd_error == expected_error
        
    
def test_repeated_name():
    # login as admin and get access token
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    nodes = {
    "nodes": [
        {
            "latitude": 12.3,
            "longitude": 12.3,
            "area": "Mehdipatnam2",
            "sensor_type":"test_sensor_type",
            "domain": "Water Quality",
            "name": "Name 2"                         # already created above
        }
    ]
    }
    response = client.post("/import/import", json=nodes,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(response.json())
    recvd_error = response.json()['failed_nodes'][0]['error']
    expected_error = 'Node: Name 2 already exists'
    assert recvd_error == expected_error
    
    # no other behaviour
    assert len(response.json()['invalid_sensor_nodes']) == 0
    assert len(response.json()['created_nodes']) == 0
    
def test_invalid_sensor_type():
    # login as admin and get access token
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    nodes = {
    "nodes": [
        {
            "latitude": 12.3,
            "longitude": 12.3,
            "area": "Mehdipatnam2",
            "sensor_type":"test_sensor_type_xyz", # does not exist in db
            "domain": "Water Quality",
            "name": "Name 2"
        }
    ]
    }
    response = client.post("/import/import", json=nodes,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(response.json())
    recvd_error = response.json()['invalid_sensor_nodes'][0]['error']
    expected_error = "Sensor type 'test_sensor_type_xyz' not found"
    assert recvd_error == expected_error
    
    # no other behaviour
    assert len(response.json()['failed_nodes']) == 0
    assert len(response.json()['created_nodes']) == 0