#!/usr/bin/env python
import os
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

print("=" * 60)
print("TESTING AUTHENTICATION")
print("=" * 60)

# Check tokens in database
print("\n1. Checking tokens in database:")
all_tokens = Token.objects.all()
print(f"Total tokens: {all_tokens.count()}")
for token in all_tokens:
    print(f"   - Token: {token.key}")
    print(f"     User: {token.user.username} (ID: {token.user.id})")

# Check the specific token
token_key = '57cade5694b471be8aa9b035d5ceb90d4d452e93'
print(f"\n2. Looking for token: {token_key}")
try:
    token = Token.objects.get(key=token_key)
    print(f"✓ Token found!")
    print(f"   User: {token.user.username}")
    print(f"   User ID: {token.user.id}")
except Token.DoesNotExist:
    print(f"✗ Token NOT found in database!")

# Test API call
print(f"\n3. Testing API call with token:")
api_url = 'http://localhost:8000/api/presentations/'
headers = {
    'Authorization': f'Token {token_key}'
}
try:
    response = requests.get(api_url, headers=headers, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
