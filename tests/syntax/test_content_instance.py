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
        json={"name": "test_vertical"},
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
        "/sensor-types/create-sensor-type",
        json={"name": "test_sensor_type", "unit": "test_unit"},
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
        "/nodes/create-node",


    