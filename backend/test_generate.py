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
print("TESTING PRESENTATION GENERATION")
print("=" * 60)

# Test data matching what frontend sends
payload = {
    'topic': 'Test Topic',
    'raw_content': 'This is test content for the presentation. It should be long enough to process.',
    'target_audience': 'Students',
    'tone': 'professional',
    'subject': 'general',
    'slide_ratio': '16:9',
    'presentation_title': 'Test Presentation',
    'num_slides': None,
    'enable_visuals': True,
    'template': 'warm_blue'
}

print("\nPayload being sent:")
print(json.dumps(payload, indent=2))

print("\nSending POST request to /presentations/generate/:")
response = requests.post(
    f'{api_url}/presentations/generate/',
    headers=headers,
    json=payload
)

print(f"\nStatus Code: {response.status_code}")
print(f"Response:")
print(json.dumps(response.json(), indent=2))

print("\n" + "=" * 60)
