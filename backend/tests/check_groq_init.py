#!/usr/bin/env python
"""
Check Groq client initialization parameters
"""
from groq import Groq
import inspect
import os

print("=" * 60)
print("GROQ CLIENT INITIALIZATION DIAGNOSTICS")
print("=" * 60)

# Check parameters
sig = inspect.signature(Groq.__init__)
print("\nGroq.__init__ accepted parameters:")
for param_name, param in sig.parameters.items():
    if param_name != 'self':
        default = f" = {param.default}" if param.default != inspect.Parameter.empty else ""
        print(f"  - {param_name}{default}")

# Test initialization
print("\nTesting Groq initialization...")
api_key = os.environ.get('GROQ_API_KEY', 'gsk_test')

try:
    client = Groq(api_key=api_key)
    print("✓ SUCCESS: Groq client initialized with api_key only")
except TypeError as e:
    print(f"✗ FAILED: {e}")
except Exception as e:
    print(f"⚠ OTHER ERROR: {e}")

print("\n" + "=" * 60)
