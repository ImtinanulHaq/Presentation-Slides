#!/usr/bin/env python
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Create or get production user
user, user_created = User.objects.get_or_create(username='presentation_api')
if user_created:
    user.set_password('production_secure_password_change_this')
    user.save()
    print("✓ Created new user: presentation_api")
else:
    print("✓ User already exists: presentation_api")

# Create or get token
token, token_created = Token.objects.get_or_create(user=user)

print("\n" + "="*60)
print("PRODUCTION API TOKEN")
print("="*60)
print(f"\nToken: {token.key}")
print(f"Username: {user.username}")
print(f"User ID: {user.id}")
print("\n✓ Use this token in REACT_APP_API_TOKEN environment variable")
print("="*60 + "\n")
