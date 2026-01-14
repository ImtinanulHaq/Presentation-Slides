#!/usr/bin/env python
"""Stress test edge cases and error scenarios"""

import requests
import json

token = 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3'
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}

edge_cases = [
    {
        'name': 'Edge Case 1: Minimal valid request',
        'data': {
            'topic': 'Test',
            'target_audience': 'Users',
            'tone': 'professional',
            'raw_content': 'Content'
        },
        'expect': 201
    },
    {
        'name': 'Edge Case 2: num_slides as string (legacy)',
        'data': {
            'topic': 'Test',
            'target_audience': 'Users',
            'tone': 'professional',
            'raw_content': 'Content here',
            'num_slides': '7'  # String instead of int
        },
        'expect': 201
    },
    {
        'name': 'Edge Case 3: Very long content',
        'data': {
            'topic': 'Comprehensive Analysis',
            'target_audience': 'Business Executives',
            'tone': 'professional',
            'raw_content': 'Lorem ipsum dolor sit amet. ' * 100,  # ~3000 chars
            'enable_visuals': True
        },
        'expect': 201
    },
    {
        'name': 'Edge Case 4: Exact minimum (3 slides)',
        'data': {
            'topic': 'Minimal',
            'target_audience': 'Users',
            'tone': 'casual',
            'raw_content': 'Content',
            'num_slides': 3
        },
        'expect': 201
    },
    {
        'name': 'Edge Case 5: Medium slides (10)',
        'data': {
            'topic': 'Medium',
            'target_audience': 'Users',
            'tone': 'professional',
            'raw_content': 'This is comprehensive content for medium-sized presentations. ' * 20,
            'num_slides': 10
        },
        'expect': 201
    },
    {
        'name': 'Edge Case 6: All tones tested',
        'data': [
            {
                'topic': 'Professional',
                'target_audience': 'Users',
                'tone': 'professional',
                'raw_content': 'Professional content'
            },
            {
                'topic': 'Casual',
                'target_audience': 'Users',
                'tone': 'casual',
                'raw_content': 'Casual content'
            },
            {
                'topic': 'Academic',
                'target_audience': 'Users',
                'tone': 'academic',
                'raw_content': 'Academic content'
            },
            {
                'topic': 'Persuasive',
                'target_audience': 'Users',
                'tone': 'persuasive',
                'raw_content': 'Persuasive content'
            }
        ],
        'expect': 201,
        'is_list': True
    }
]

print("=" * 80)
print("EDGE CASE & STRESS TEST")
print("=" * 80)

passed = 0
failed = 0

for test in edge_cases:
    if test.get('is_list'):
        # Test multiple data items
        for data in test['data']:
            response = requests.post('http://localhost:8000/api/presentations/generate/', 
                                    json=data, headers=headers)
            if response.status_code == test['expect']:
                passed += 1
                print(f"\n✓ {test['name']} [{data['tone']}]: PASS")
            else:
                failed += 1
                print(f"\n✗ {test['name']} [{data['tone']}]: FAIL (Status {response.status_code})")
                print(f"  Error: {response.text[:200]}")
    else:
        # Single data item
        response = requests.post('http://localhost:8000/api/presentations/generate/', 
                                json=test['data'], headers=headers)
        if response.status_code == test['expect']:
            passed += 1
            data_resp = response.json()
            print(f"\n✓ {test['name']}: PASS (ID: {data_resp.get('id')}, Slides: {data_resp.get('total_slides')})")
        else:
            failed += 1
            print(f"\n✗ {test['name']}: FAIL (Status {response.status_code})")
            print(f"  Error: {response.text[:300]}")

print("\n" + "=" * 80)
print(f"STRESS TEST RESULTS: {passed} passed, {failed} failed")
if failed == 0:
    print("✅ ALL EDGE CASES HANDLED CORRECTLY")
else:
    print(f"⚠️  {failed} edge case(s) failed")
print("=" * 80)
