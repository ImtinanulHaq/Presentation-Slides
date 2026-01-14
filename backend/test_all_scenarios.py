#!/usr/bin/env python
"""Comprehensive test of all API scenarios"""

import requests
import json

token = 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3'
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}

test_cases = [
    {
        'name': 'Test 1: Without num_slides (auto)',
        'data': {
            'presentation_title': 'Auto Slides',
            'topic': 'Testing',
            'target_audience': 'Users',
            'tone': 'professional',
            'raw_content': 'This is test content',
            'enable_visuals': True
        }
    },
    {
        'name': 'Test 2: With num_slides=5',
        'data': {
            'presentation_title': 'Test 5',
            'topic': 'Python',
            'target_audience': 'Developers',
            'tone': 'casual',
            'raw_content': 'Python is great. It has many libraries.',
            'num_slides': 5,
            'enable_visuals': True
        }
    },
    {
        'name': 'Test 3: Without visuals',
        'data': {
            'presentation_title': 'No Visuals',
            'topic': 'Topic',
            'target_audience': 'Audience',
            'tone': 'professional',
            'raw_content': 'Content here',
            'num_slides': 3,
            'enable_visuals': False
        }
    },
    {
        'name': 'Test 4: Large content auto-determine',
        'data': {
            'presentation_title': 'Large Content',
            'topic': 'Business',
            'target_audience': 'Executives',
            'tone': 'professional',
            'raw_content': 'Business strategy involves planning, execution, and monitoring. Planning includes market analysis, competitive positioning, and goal setting. Execution requires resource allocation, team coordination, and timeline management. Monitoring involves KPI tracking, progress measurement, and adjustment processes.',
            'enable_visuals': True
        }
    },
    {
        'name': 'Test 5: Minimum slides (3)',
        'data': {
            'presentation_title': 'Min Slides',
            'topic': 'Minimal',
            'target_audience': 'Users',
            'tone': 'academic',
            'raw_content': 'Short content',
            'num_slides': 3,
            'enable_visuals': True
        }
    },
    {
        'name': 'Test 6: Maximum slides (20)',
        'data': {
            'presentation_title': 'Max Slides',
            'topic': 'Comprehensive',
            'target_audience': 'Executives',
            'tone': 'professional',
            'raw_content': 'This is comprehensive content about many topics including strategy, execution, monitoring, analysis, planning, implementation, and results evaluation across multiple dimensions.',
            'num_slides': 20,
            'enable_visuals': True
        }
    }
]

print("=" * 70)
print("COMPREHENSIVE API TEST - ALL SCENARIOS")
print("=" * 70)

passed = 0
failed = 0

for test in test_cases:
    response = requests.post('http://localhost:8000/api/presentations/generate/', json=test['data'], headers=headers)
    status = 'PASS' if response.status_code == 201 else 'FAIL'
    
    if response.status_code == 201:
        passed += 1
        data = response.json()
        print(f"\n{test['name']}: {status}")
        print(f"  ID: {data.get('id')}, Slides: {data.get('total_slides')}")
    else:
        failed += 1
        print(f"\n{test['name']}: {status} (Status {response.status_code})")
        print(f"  Error: {response.text[:300]}")

print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 70)
