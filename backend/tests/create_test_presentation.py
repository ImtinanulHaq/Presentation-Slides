#!/usr/bin/env python
import requests
import json

api_url = 'http://localhost:8000/api'
token = '57cade5694b471be8aa9b035d5ceb90d4d452e93'
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

print("=" * 60)
print("CREATING TEST PRESENTATION")
print("=" * 60)

# Create a presentation
presentation_data = {
    'title': 'Test Presentation',
    'description': 'This is a test presentation'
}

print("\n1. Creating presentation:")
response = requests.post(
    f'{api_url}/presentations/',
    headers=headers,
    json=presentation_data
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 201:
    presentation_id = response.json()['id']
    print(f"\n✓ Presentation created with ID: {presentation_id}")
    
    # List presentations
    print("\n2. Listing presentations:")
    response = requests.get(f'{api_url}/presentations/', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

print("\n" + "=" * 60)
