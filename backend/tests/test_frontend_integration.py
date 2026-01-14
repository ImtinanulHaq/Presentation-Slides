#!/usr/bin/env python
"""
End-to-End Frontend Integration Test
Tests the exact flow that the frontend performs
"""

import requests
import json
import time

token = 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3'
headers = {
    'Authorization': f'Token {token}',
    'Content-Type': 'application/json'
}

API_BASE = 'http://localhost:8000/api'

print("=" * 80)
print("END-TO-END FRONTEND INTEGRATION TEST")
print("=" * 80)

# Simulate exactly what the frontend sends
test_scenarios = [
    {
        'name': 'Scenario 1: Basic generation (auto slides)',
        'data': {
            'topic': 'Web Development',
            'raw_content': 'HTML, CSS, and JavaScript are the core technologies of web development.',
            'target_audience': 'Beginners',
            'tone': 'professional',
            'presentation_title': 'Web Dev Basics',
            'num_slides': None,  # Frontend sends null for auto
            'enable_chunking': False,
            'enable_visuals': True
        }
    },
    {
        'name': 'Scenario 2: With specific slide count',
        'data': {
            'topic': 'Machine Learning',
            'raw_content': 'Machine learning algorithms learn patterns from data to make predictions.',
            'target_audience': 'Students',
            'tone': 'academic',
            'presentation_title': 'ML Introduction',
            'num_slides': 5,
            'enable_chunking': False,
            'enable_visuals': True
        }
    },
    {
        'name': 'Scenario 3: Minimal form submission',
        'data': {
            'topic': 'Python Programming',
            'raw_content': 'Python is easy to learn and powerful.',
            'target_audience': 'Developers',
            'tone': 'casual',
            'presentation_title': '',  # Empty string like frontend
            'num_slides': None,
            'enable_chunking': False,
            'enable_visuals': True
        }
    },
    {
        'name': 'Scenario 4: With chunking enabled',
        'data': {
            'topic': 'Data Science',
            'raw_content': 'Data science combines statistics, programming, and domain knowledge. ' * 20,
            'target_audience': 'Professionals',
            'tone': 'professional',
            'presentation_title': 'Data Science Overview',
            'num_slides': None,
            'enable_chunking': True,
            'enable_visuals': True
        }
    },
    {
        'name': 'Scenario 5: Without visuals',
        'data': {
            'topic': 'Project Management',
            'raw_content': 'Managing projects requires planning, execution, and monitoring.',
            'target_audience': 'Managers',
            'tone': 'professional',
            'presentation_title': 'PM Basics',
            'num_slides': 4,
            'enable_chunking': False,
            'enable_visuals': False
        }
    }
]

passed = 0
failed = 0

for scenario in test_scenarios:
    print(f"\n{scenario['name']}")
    print("-" * 80)
    
    try:
        print(f"Sending request to: {API_BASE}/presentations/generate/")
        print(f"Payload (condensed): topic={scenario['data']['topic']}, slides={scenario['data']['num_slides']}")
        
        response = requests.post(
            f"{API_BASE}/presentations/generate/",
            json=scenario['data'],
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ SUCCESS - Status: {response.status_code}")
            print(f"   • Presentation ID: {data.get('id')}")
            print(f"   • Title: {data.get('title')}")
            print(f"   • Slides Generated: {data.get('total_slides')}")
            print(f"   • Created: {data.get('created_at')}")
            passed += 1
        else:
            failed += 1
            print(f"❌ FAILED - Status: {response.status_code}")
            error_data = response.json() if response.text else {}
            print(f"   Error Response: {json.dumps(error_data, indent=6)[:500]}")
            
    except requests.exceptions.ConnectionError as e:
        failed += 1
        print(f"❌ CONNECTION ERROR: Cannot reach backend at {API_BASE}")
        print(f"   Make sure Django is running: python manage.py runserver")
    except requests.exceptions.Timeout as e:
        failed += 1
        print(f"❌ TIMEOUT: Request took too long")
    except Exception as e:
        failed += 1
        print(f"❌ ERROR: {str(e)}")

print("\n" + "=" * 80)
print(f"INTEGRATION TEST RESULTS: {passed} passed, {failed} failed out of {len(test_scenarios)} scenarios")
if failed == 0:
    print("✅ ALL SCENARIOS PASSED - FRONTEND INTEGRATION READY")
else:
    print(f"⚠️  {failed} scenario(s) failed - check backend logs")
print("=" * 80)
