import requests

with open('../smartcontract/src/VulnerableToken.sol', 'rb') as f:
    files = {'file':('VulnerableToken.sol', f)}
    data = {'payment_id': '1'}
    try:
        r = requests.post("http://127.0.0.1:8000/api/simulate", files=files, data=data)
        print(r.status_code)
        print(r.json())
    except Exception as e:
        print("Error:", e)
