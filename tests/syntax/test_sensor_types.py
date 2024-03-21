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

# test create new sensor type
def test_create_sensor_type():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    create_vertical()
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

    assert response.status_code == 200

def test_invalid_vertical_id_create_sensor_type():
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
               "vertical_id": 1000
        },
        headers={"Authorization": f"Bearer {access_token}"}, 
    )

    assert response.status_code == 500

def test_already_existing_sensor_type_create_sensor_type():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    create_vertical()
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

    assert response.status_code == 500

def test_invalid_type_of_request_create_sensor_type():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.get(
        "/sensor-types/create",
        headers={"Authorization": f"Bearer {access_token}"}, 
    )

    assert response.status_code == 405

    response = client.put(
        "/sensor-types/create",
        headers={"Authorization": f"Bearer {access_token}"}, 
    )

    assert response.status_code == 405

    response = client.delete(
        "/sensor-types/create",
        headers={"Authorization": f"Bearer {access_token}"}, 
    )

    assert response.status_code == 405

# test get all sensor types
def test_get_all_sensor_types():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]

    create_vertical()
    response = client.get(
        "/sensor-types/get-all",
        json={"vertical_id": 1},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

def test_invalid_vertical_id_get_all_sensor_types():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.get(
        "/sensor-types/get-all",
        json={"vertical_id": 1000},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 500

def test_invalid_type_of_request_get_all_sensor_types():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.post(
        "/sensor-types/get-all",
        json={"vertical_id": 1},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 405

    response = client.put(
        "/sensor-types/get-all",
        json={"vertical_id": 1},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 405

    response = client.delete(
        "/sensor-types/get-all",
        json={"vertical_id": 1},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 405

# test delete sensor type
def test_delete_sensor_type():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]

    create_vertical()

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

    response = client.delete(
        "/sensor-types/delete",
        json={"id": 1,
               "vertical_id": 1
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

def test_invalid_details_delete_sensor_type():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]

    create_vertical()

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

    response = client.delete(
        "/sensor-types/delete",
        json={"id": 1000,
               "vertical_id": 1
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 500

    response = client.delete(
        "/sensor-types/delete",
        json={"id": 1,
               "vertical_id": 1000
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 500

def test_missing_details_delete_sensor_type():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.delete(
        "/sensor-types/delete",
        json = {}
    )

    assert response.status_code == 422


def test_invalid_type_of_request_delete_sensor_type():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
                                "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.get(
        "/sensor-types/delete",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 405

    response = client.put(
        "/sensor-types/delete",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 405

    response = client.post(
        "/sensor-types/delete",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 405
