import pytest
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.database import engine as database, get_session, Base, init_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Initialize the database with the SQLite URL for testing
database_url = "sqlite:///./test.db"
init_db(database_url)

# Import main after initializing the test database to ensure it uses the correct settings
from main import app, initialize

# Initialize the app
initialize(database_url)

print("Testing main.py")

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_login():
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
