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
               "vertical_id": 0
        },
        headers={"Authorization": f"Bearer {access_token}"}, 
    )


def test_create_cin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    # create a new node
    response = client.post(
        "/cin/create/1",
        json={}
    )
    assert response.status_code == 200


    