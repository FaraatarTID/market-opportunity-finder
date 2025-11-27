import requests, json
url = 'http://127.0.0.1:8000/api/markets/analyze'
payload = {'country_name': 'Germany'}
headers = {'Content-Type': 'application/json'}
response = requests.post(url, json=payload, headers=headers)
print('Status code:', response.status_code)
print('Response:', response.text)
