#!/usr/bin/env python
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create or get user
user, user_created = User.objects.get_or_create(
    username='presentation_api',
    defaults={'email': 'api@presentation.local'}
)

if user_created:
    user.set_password('presentation_secure_2026')
    user.save()
    print("✓ User created: presentation_api")
else:
    print("✓ User exists: presentation_api")

# Create or get token
token, token_created = Token.objects.get_or_create(user=user)

print(f"\n{'='*60}")
print(f"API TOKEN: {token.key}")
print(f"{'='*60}\n")

# Save to file for reference
with open('TOKEN.txt', 'w') as f:
    f.write(token.key)

print("✓ Token saved to TOKEN.txt")
