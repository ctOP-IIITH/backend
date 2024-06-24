from tests import client


def test_correct_login():
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "admin"}
    )
    assert response.status_code == 200
    # check if response.json() has access_token and refresh_token
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    # store the access_token for future use
    access_token = response.json()["access_token"]
    # do user/am-i-admin to check if the user is admin
    response = client.get(
        "/user/am-i-admin", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {"admin": True, "username": "admin"}


def test_a_incorrect_password_login():
    response = client.post(
        "/user/login", json={"email": "admin@localhost", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect password"}


def test_b_incorrect_email_login():
    response = client.post(
        "/user/login", json={"email": "admin1@localhost", "password": "admin"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect email"}
