from fastapi.testclient import TestClient
from app.utils.delete_with_payload import CustomTestClient
from main import app, initialize

# Initialize the app
initialize()

print("Testing main.py")

client = CustomTestClient(app)
