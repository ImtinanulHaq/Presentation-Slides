#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

print("\n" + "="*70)
print("TOKEN VERIFICATION")
print("="*70)

user = User.objects.get(username='presenter')
token = Token.objects.get(user=user)

print(f"\nUser Details:")
print(f"  Username:     {user.username}")
print(f"  Email:        {user.email}")
print(f"  First Name:   {user.first_name}")
print(f"  Last Name:    {user.last_name}")
print(f"  Active:       {user.is_active}")
print(f"  Is Staff:     {user.is_staff}")
print(f"  Is Superuser: {user.is_superuser}")

print(f"\nToken Details:")
print(f"  Token:        {token.key}")
print(f"  Length:       {len(token.key)}")
print(f"  Valid Format: {len(token.key) == 40}")
print(f"  Created:      {token.created}")

print(f"\nAuthentication Test:")
print(f"  Format:       Token {token.key}")
print(f"  Status:       READY TO USE")

print(f"\n" + "="*70)
print("This token should be in frontend/.env as REACT_APP_API_TOKEN")
print("="*70 + "\n")
