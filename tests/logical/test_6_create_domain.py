from tests import client
import time

def test_create_domain():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.post(
        "/verticals/create-ae",
        json={"ae_name": "logical_test_ae",
               "ae_description": "test_description",
               "ae_short_name": "LE",
               "labels": []
        },
        headers={"Authorization": f"Bearer {access_token}"}, 
    )

    assert response.status_code == 201

