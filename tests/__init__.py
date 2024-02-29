from fastapi.testclient import TestClient
from app.database import init_db

# Initialize the database with the SQLite URL for testing
database_url = "sqlite:///./test.db"
init_db(database_url)

# Import main after initializing the test database to ensure it uses the correct settings
from main import app, initialize

# Initialize the app
initialize(database_url)

print("Testing main.py")

client = TestClient(app)
