#!/usr/bin/env python
"""Quick check to see what bullet_style is stored in the database"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from presentation_app.models import Presentation

# Get the last 5 presentations
presentations = Presentation.objects.all().order_by('-id')[:5]

print("\n" + "="*80)
print("LAST 5 PRESENTATIONS - BULLET STYLE CHECK")
print("="*80)

for p in presentations:
    print(f"\nID: {p.id}")
    print(f"  Title: {p.title}")
    print(f"  Template: {p.template}")
    print(f"  Slide Ratio: {p.slide_ratio}")
    print(f"  Bullet Style: '{p.bullet_style}' (type: {type(p.bullet_style).__name__})")
    print(f"  Created: {p.created_at}")

print("\n" + "="*80)
