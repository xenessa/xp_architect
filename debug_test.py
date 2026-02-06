import requests

BASE_URL = "https://xparchitect-production.up.railway.app"

resp = requests.post(f"{BASE_URL}/api/auth/register", json={
    "email": "debug_test2@example.com",
    "password": "test123",
    "name": "Debug User",
    "role": "SA"
})

print("Status:", resp.status_code)
print(resp.json())