#!/usr/bin/env python
"""Test missing required fields"""
import requests
import json

token = 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3'
headers = {'Authorization': f'Token {token}'}

test_cases = [
    {
        'name': 'Missing target_audience',
        'data': {
            'topic': 'Hacker',
            'raw_content': 'Test content',
            'tone': 'professional',
        }
    },
    {
        'name': 'Missing tone',
        'data': {
            'topic': 'Hacker',
            'raw_content': 'Test content',
            'target_audience': 'General',
        }
    },
    {
        'name': 'Missing both',
        'data': {
            'topic': 'Hacker',
            'raw_content': 'Test content',
        }
    }
]

for test in test_cases:
    r = requests.post('http://localhost:8000/api/presentations/generate/', json=test['data'], headers=headers)
    print('Test:', test['name'])
    print('Status:', r.status_code)
    if r.status_code != 201:
        error_data = r.json()
        print('Error:', json.dumps(error_data, indent=2))
    print()
