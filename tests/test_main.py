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
