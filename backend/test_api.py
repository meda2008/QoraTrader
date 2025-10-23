from src.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test a basic endpoint
response = client.get('/')
print(f'GET / status: {response.status_code}')
if response.status_code == 200:
    print(f'GET / response: {response.text[:100]}...')
else:
    print(f'GET / response: {response.text}')

# Test API root
response = client.get('/api/v1')
print(f'GET /api/v1 status: {response.status_code}')

# Test health endpoint if it exists
try:
    response = client.get('/api/v1/health')
    print(f'GET /api/v1/health status: {response.status_code}')
    print(f'GET /api/v1/health response: {response.text}')
except Exception as e:
    print(f"Error testing health endpoint: {e}")

# Test other endpoints
endpoints_to_test = [
    '/api/v1/strategies',
    '/api/v1/orders',
    '/api/v1/accounts',
    '/api/v1/positions'
]

for endpoint in endpoints_to_test:
    try:
        response = client.get(endpoint)
        print(f'GET {endpoint} status: {response.status_code}')
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")