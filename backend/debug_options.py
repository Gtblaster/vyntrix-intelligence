import requests

print("Testing OPTIONS request...")
try:
    res = requests.options(
        "http://127.0.0.1:8000/scan-image/", 
        headers={
            "Origin": "http://localhost:3000", 
            "Access-Control-Request-Method": "POST"
        }
    )
    print("STATUS:", res.status_code)
    print("HEADERS:", res.headers)
    print("BODY:", res.text)
except Exception as e:
    print("FAILED:", e)
