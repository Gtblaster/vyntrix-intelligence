import requests
print("Testing CORS headers on 415 error...")
try:
    res = requests.post(
        "http://127.0.0.1:8000/scan-image/", 
        files={"file": ("bad.txt", b"hello", "text/plain")},
        headers={
            "Origin": "http://localhost:3000"
        }
    )
    print("STATUS:", res.status_code)
    print("HEADERS:", res.headers)
    print("BODY:", res.text)
except Exception as e:
    print("FAILED:", e)
