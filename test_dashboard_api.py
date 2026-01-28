
import requests

try:
    response = requests.get('http://localhost:3000/api/dashboard-stats')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
