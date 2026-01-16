#!/usr/bin/env python
"""
Deep diagnostic of Groq initialization issue
"""
import os
import traceback

print("=" * 70)
print("GROQ INITIALIZATION - DEEP DIAGNOSTIC")
print("=" * 70)

# Test 1: Direct import and initialization
print("\n[TEST 1] Direct Groq initialization outside Django")
print("-" * 70)

try:
    from groq import Groq
    api_key = 'gsk_test_key'
    
    print(f"Attempting: Groq(api_key='{api_key[:10]}...')")
    client = Groq(api_key=api_key)
    print("✓ SUCCESS")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

# Test 2: Check if httpx is interfering
print("\n\n[TEST 2] Check httpx configuration")
print("-" * 70)

try:
    import httpx
    print(f"httpx version: {httpx.__version__}")
    
    # Check if there are any environment variables affecting httpx
    env_vars = [k for k in os.environ.keys() if 'PROXY' in k.upper() or 'HTTP' in k.upper()]
    if env_vars:
        print(f"Relevant environment variables: {env_vars}")
        for var in env_vars:
            print(f"  {var}: {os.environ[var]}")
    else:
        print("No proxy-related environment variables found")
        
except Exception as e:
    print(f"Error checking httpx: {e}")

# Test 3: Check if there's a monkeypatch or middleware
print("\n\n[TEST 3] Check for Groq class modification")
print("-" * 70)

try:
    from groq import Groq
    import inspect
    
    # Get the source file
    source_file = inspect.getfile(Groq)
    print(f"Groq source: {source_file}")
    
    # Get init signature
    sig = inspect.signature(Groq.__init__)
    print(f"Groq.__init__ signature: {sig}")
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)
