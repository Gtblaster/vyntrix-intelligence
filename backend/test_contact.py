import requests

response = requests.post(
    "http://127.0.0.1:8000/contact/",
    json={"name": "Alice", "email": "alice@nexus.com", "message": "Test transmission."}
)
print("Status Code:", response.status_code)
print("Response:", response.json())
