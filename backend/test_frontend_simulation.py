#!/usr/bin/env python
"""Test frontend request simulation"""

import requests
import json

token = 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3'
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

# Test 1: What the frontend actually sends
print("=" * 70)
print("TEST 1: Frontend request simulation")
print("=" * 70)

frontend_payload = {
    'topic': 'Machine Learning Basics',
    'raw_content': 'Machine learning is a subset of AI that enables computers to learn from data.',
    'target_audience': 'Developers',
    'tone': 'professional',
    'presentation_title': 'ML Intro',
    'num_slides': None,
    'enable_chunking': False,
    'enable_visuals': True
}

print("\nPayload being sent:")
print(json.dumps(frontend_payload, indent=2))

response = requests.post(
    'http://localhost:8000/api/presentations/generate/',
    json=frontend_payload,
    headers=headers
)

print(f"\nStatus: {response.status_code}")
if response.status_code != 201:
    print(f"Error Response:\n{json.dumps(response.json(), indent=2)}")
else:
    print("✅ SUCCESS")
    data = response.json()
    print(f"   ID: {data.get('id')}")
    print(f"   Title: {data.get('title')}")
    print(f"   Slides: {data.get('total_slides')}")

# Test 2: Without optional fields
print("\n" + "=" * 70)
print("TEST 2: Minimal required fields only")
print("=" * 70)

minimal_payload = {
    'topic': 'Test',
    'raw_content': 'Test content',
    'target_audience': 'Users',
    'tone': 'professional'
}

print("\nPayload being sent:")
print(json.dumps(minimal_payload, indent=2))

response = requests.post(
    'http://localhost:8000/api/presentations/generate/',
    json=minimal_payload,
    headers=headers
)

print(f"\nStatus: {response.status_code}")
if response.status_code != 201:
    print(f"Error Response:\n{json.dumps(response.json(), indent=2)}")
else:
    print("✅ SUCCESS")

print("\n" + "=" * 70)
