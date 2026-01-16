#!/usr/bin/env python
"""
Test Groq initialization after fix
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from presentation_app.presentation_generator import GroqPresentationGenerator

print("=" * 70)
print("TESTING GROQ CLIENT INITIALIZATION")
print("=" * 70)

try:
    print("\nInitializing GroqPresentationGenerator...")
    
    generator = GroqPresentationGenerator(
        topic="Test Topic",
        raw_content="This is test content for the presentation. It contains sample information to demonstrate functionality.",
        target_audience="Test Audience",
        tone="professional",
        subject="general",
        num_slides=None,
        enable_chunking=False,
        enable_visuals=True
    )
    
    print("✓ SUCCESS: GroqPresentationGenerator initialized successfully")
    print(f"  - Client type: {type(generator.client).__name__}")
    print(f"  - Topic: {generator.topic}")
    print(f"  - Content length: {len(generator.raw_content)} characters")
    
except TypeError as te:
    print(f"✗ FAILED - TypeError: {te}")
except Exception as e:
    print(f"✗ FAILED - {type(e).__name__}: {e}")

print("\n" + "=" * 70)
