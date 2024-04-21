from tests import client
from app.utils.delete_with_payload import CustomTestClient

import time
 
# create user
def test_create_user():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    # print(access_token)
    response = client.post(
        "/user/create-user",
        json={
            "username": "testuser",
            "email": "test@localhost",
            "password": "testpassword", 
            "user_type": 0
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print(response.json())
    assert response.status_code == 200

def test_create_user_with_alreadyregistered_email():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/create-user",
        json={
            "username": "admin",
            "email": "admin@localhost",
            "password": "testpassword",
            "user_type": 0
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

def test_missing_details_create_user():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/create-user",
        json={},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

def test_empty_details_create_user():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/create-user",
        json={
              "username": "admin",
              "email": "admin@localhost",
              "password": "",
              "user_type": 0
            },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

    response = client.post(
        "/user/create-user",
        json={
              "username": "admin",
              "email": "",
              "password": "admin",
              "user_type": 0
            },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

    response = client.post(
        "/user/create-user",
        json={
              "username": "",
              "email": "admin@localhost",
              "password": "admin",
              "user_type": 0
            },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

def test_invalid_type_of_request_create_user():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.get(
        "/user/create-user",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.put(
        "/user/create-user",
        json={
              "username": "admin",
              "email": "admin@localhost",
              "password": "admin",
              "user_type": 0
            },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete_with_payload(
        "/user/create-user",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}
    
# login
def test_correct_login():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    assert response.status_code == 200
    # check if response.json() has access_token and refresh_token
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    # store the access_token for future use
    access_token = response.json()["access_token"]
    response = client.get(
        "/user/am-i-admin", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {"admin": True, "username": "admin"}


def test_incorrect_login():
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect password"}


def test_incorrect_email_login():
    response = client.post(
        "/user/login", json={"email": "wrongemail@localhost", "password": "admin"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect email"}

def test_missing_details():
    response = client.post(
        "/user/login", json={}
    )
    assert response.status_code == 422


def test_empty_details():
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": ""}
    )

    assert response.status_code == 400

    response = client.post(
        "/user/login", json={"email": "", "password": "admin"}
    )

    assert response.status_code == 400

def test_invalid_type_of_request_login():
    response = client.get(
        "/user/login"
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.put(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete_with_payload(
        "/user/login"
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}
 

# profile
    
def test_get_profile():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.get(
        "/user/profile", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"email": "admin@localhost", "username": "admin", "user_type": 1}


def test_invalid_type_of_request_profile():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    access_token = response.json()["access_token"]

    response = client.post(
        "/user/profile",
        json={"email": "admin@localhost", "username": "admin", "user_type": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.put(
        "/user/profile",
        json={"email": "admin@localhost", "username": "admin", "user_type": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405  
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete_with_payload(
        "/user/profile", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

# refresh token
def test_refresh_token():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    refresh_token = response.json()["refresh_token"]
    response = client.post(
        "/user/token/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

# def test_invalid_refresh_token():
#     time.sleep(1)
#     response = client.post(
#         "/user/token/refresh", json={"refresh_token": "invalidtoken"}
#     )
#     assert response.status_code == 400

def test_missing_details_refresh_token():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    refresh_token = response.json()["refresh_token"]
    response = client.post(
        "/user/token/refresh", json={}
    )
    assert response.status_code == 422

def test_invalid_type_of_request_refresh_token():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    refresh_token = response.json()["refresh_token"]
    response = client.get(
        "/user/token/refresh"
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.put(
        "/user/token/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete_with_payload(
        "/user/token/refresh"
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


# get users
def test_get_users():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.get(
        "/user/getusers", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

def test_invalid_type_of_request_get_users():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/getusers",
        json={"email": "admin@localhost", "username": "admin", "user_type": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.put(
        "/user/getusers",
        json={"email": "admin@localhost", "username": "admin", "user_type": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete_with_payload(
        "/user/getusers", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


# am i admin
def test_am_i_admin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.get(
        "/user/am-i-admin", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"admin": True, "username": "admin"}

def test_invalid_type_of_request_am_i_admin():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/am-i-admin",
        json={"email": "admin@localhost", "username": "admin", "user_type": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.put(
        "/user/am-i-admin",
        json={"email": "admin@localhost", "username": "admin", "user_type": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete_with_payload(
        "/user/am-i-admin", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}


# change password
    
def create_user(email, password, username, user_type):
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/create-user",
        json={
            "username": username,
            "email": email,
            "password": password,
            "user_type": user_type
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

def test_change_password():
    create_user("test@localhost", "testpassword", "testuser", 0)
    response = client.post(
        "/user/login", json={"email": "test@localhost",
        "password": "testpassword"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/change-password",
        json={
            "email": "test@localhost",
            "old_password": "testpassword",
            "new_password": "testpassword1"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


def test_missing_details_change_password():
    create_user("test1@localhost", "test1password", "test1user", 0)   
    response = client.post(
        "/user/login", json={"email": "test1@localhost",
        "password": "test1password"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/change-password",
        json={},
        headers={"Authorization": f"Bearer {access_token}"},
    ) 

    assert response.status_code == 422
           

def test_empty_details_change_password():
    create_user("test2@localhost", "test2password", "test2user", 0)
    response = client.post(
        "/user/login", json={"email": "test2@localhost",
        "password": "test2password"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/change-password",
        json={
            "email": "test2@localhost",
            "old_password": "",
            "new_password": "testpassword1"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

    create_user("test3@localhost", "test3password", "test3user", 0) 
    response = client.post(
        "/user/login", json={"email": "test3@localhost",
        "password": "test3password"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/change-password",
        json={
            "email": "test3@localhost",
            "old_password": "test3password",
            "new_password": ""
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

    create_user("test4@localhost", "test4password", "test4user", 0)
    response = client.post(
        "/user/login", json={"email": "test4@localhost",
        "password": "test4password"}
    )

    access_token = response.json()["access_token"]
    response = client.post(
        "/user/change-password",
        json={
            "email": "",
            "old_password": "test4password",
            "new_password": "testpassword4"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

    
def test_wrong_old_password_change_password():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/change-password",
        json={
            "email": "admin@localhost",
            "old_password": "wrongpassword",
            "new_password": "testpassword1"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

def test_invalid_email_change_password():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "admin@localhost",
        "password": "admin"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/change-password",
        json={
            "email": "wrongemail@localhost",
            "old_password": "admin",
            "new_password": "testpassword1"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

def test_same_old_and_new_password_change_password():
    create_user("test5@localhost", "test5password", "test5user", 0)
    response = client.post(
        "/user/login", json={"email": "test5@localhost",
        "password": "test5password"}
    )
    access_token = response.json()["access_token"]
    response = client.post(
        "/user/change-password",
        json={
            "email": "test5@localhost",
            "old_password": "test5password",
            "new_password": "test5password"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400

def test_invalid_type_of_request_change_password():
    time.sleep(1)
    response = client.post(
        "/user/login", json={"email": "test@localhost",
        "password": "testpassword1"}
    )
    access_token = response.json()["access_token"]

    response = client.get(
        "/user/change-password",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.put(
        "/user/change-password",
        json={
            "email": "test@localhost",
            "old_password": "testpassword1",
            "new_password": "testpassword1"
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}

    response = client.delete_with_payload(
        "/user/change-password",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}
    