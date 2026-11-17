import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from api.main import app
import getpass

username = input("Username: ")
password = getpass.getpass("Password: ")

client = TestClient(app)

response = client.post(
    "/auth/login",
    data={
        "username": username,
        "password": password
    }
)

print("HTTP status:", response.status_code)

if response.status_code == 200:
    print("Login endpoint: SUCCESS")
    print("Token received:", bool(response.json().get("access_token")))
else:
    print("Login endpoint response:", response.json())