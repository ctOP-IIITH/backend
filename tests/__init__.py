from fastapi.testclient import TestClient
from main import app, initialize

# Initialize the app
initialize()

print("Testing main.py")

client = TestClient(app)
