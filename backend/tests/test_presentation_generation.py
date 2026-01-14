"""
Test Script for Presentation Generation System
Tests the complete flow: API authentication, presentation generation, and database storage
"""

import os
import sys
import django
import json
import requests
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from presentation_app.models import Presentation, Slide
from presentation_app.presentation_generator import GroqPresentationGenerator


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_groq_connection():
    """Test Groq API connection"""
    print_header("TEST 1: Groq API Connection")
    
    try:
        from groq import Groq
        api_key = os.environ.get('GROQ_API_KEY', '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')
        
        client = Groq(api_key=api_key)
        print("✓ Groq client initialized successfully")
        print(f"✓ API Key available: {api_key[:20]}...")
        
        # Test simple completion
        message = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say 'API connection successful' in 5 words"}],
            temperature=0.7,
            max_tokens=100,
        )
        response = message.choices[0].message.content
        print(f"✓ API Response: {response}")
        return True
        
    except Exception as e:
        print(f"✗ Groq API Error: {str(e)}")
        return False


def test_user_and_token():
    """Test user creation and token generation"""
    print_header("TEST 2: User and Token Setup")
    
    try:
        # Get or create user
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )
        print(f"✓ User 'test_user' {'created' if created else 'retrieved'}")
        
        # Get or create token
        token, token_created = Token.objects.get_or_create(user=user)
        print(f"✓ Token {'created' if token_created else 'retrieved'}: {token.key}")
        
        return True, token.key
        
    except Exception as e:
        print(f"✗ User/Token Error: {str(e)}")
        return False, None


def test_presentation_generator():
    """Test LLM presentation generation"""
    print_header("TEST 3: Presentation Generation (Groq LLM)")
    
    try:
        # Test data
        topic = "Climate Change Solutions"
        raw_content = """
        Climate change is a major global challenge. We need renewable energy sources like solar and wind power.
        Electric vehicles are becoming more popular. Trees and forests help absorb carbon dioxide.
        Governments are setting new climate targets. Companies are investing in green technology.
        Individual actions matter - recycling, reducing waste, and using public transport.
        """
        target_audience = "general"
        tone = "professional"
        
        print(f"Topic: {topic}")
        print(f"Content length: {len(raw_content)} characters")
        print(f"Audience: {target_audience}")
        print(f"Tone: {tone}")
        print("\n🔄 Generating presentation (this may take 5-10 seconds)...\n")
        
        # Generate
        generator = GroqPresentationGenerator(
            topic=topic,
            raw_content=raw_content,
            target_audience=target_audience,
            tone=tone,
        )
        
        presentation_json = generator.generate()
        
        if presentation_json:
            print("✓ Presentation generated successfully!")
            print(f"✓ Title: {presentation_json.get('presentation_title', 'N/A')}")
            print(f"✓ Slides count: {len(presentation_json.get('slides', []))}")
            
            # Show first slide
            if presentation_json.get('slides'):
                first_slide = presentation_json['slides'][0]
                print(f"\n📄 First Slide Preview:")
                print(f"  - Type: {first_slide.get('slide_type', 'N/A')}")
                print(f"  - Title: {first_slide.get('title', 'N/A')}")
                print(f"  - Bullets: {len(first_slide.get('bullets', []))} bullet points")
            
            return True, presentation_json
        else:
            print("✗ No presentation generated")
            return False, None
            
    except Exception as e:
        print(f"✗ Generation Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_database_storage(presentation_json):
    """Test saving presentation to database"""
    print_header("TEST 4: Database Storage")
    
    try:
        user = User.objects.get(username='test_user')
        
        # Create presentation
        presentation = Presentation.objects.create(
            title=presentation_json.get('presentation_title', 'Test Presentation'),
            topic='Climate Change Solutions',
            raw_content='Test content',
            target_audience='general',
            tone='professional',
            json_structure=presentation_json,
            created_by=user,
        )
        print(f"✓ Presentation saved to database (ID: {presentation.id})")
        
        # Create slides
        slide_count = 0
        for slide_data in presentation_json.get('slides', []):
            Slide.objects.create(
                presentation=presentation,
                slide_number=slide_data.get('slide_number', 0),
                slide_type=slide_data.get('slide_type', 'content'),
                title=slide_data.get('title', ''),
                subtitle=slide_data.get('subtitle', ''),
                bullets=slide_data.get('bullets', []),
                visuals=slide_data.get('visuals', {}),
                speaker_notes=slide_data.get('speaker_notes', ''),
                order=slide_data.get('slide_number', 0),
            )
            slide_count += 1
        
        print(f"✓ {slide_count} slides created in database")
        
        # Verify retrieval
        retrieved = Presentation.objects.get(id=presentation.id)
        print(f"✓ Presentation retrieved from database")
        print(f"  - Title: {retrieved.title}")
        print(f"  - Slides in DB: {retrieved.slides.count()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Database Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint(token):
    """Test API endpoint"""
    print_header("TEST 5: REST API Endpoint")
    
    try:
        api_url = "http://localhost:8000/api/presentations/generate/"
        
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
        }
        
        data = {
            "topic": "Python Programming",
            "raw_content": "Python is a versatile programming language used in web development, data science, and automation. It has simple syntax and powerful libraries like Django, NumPy, and Pandas.",
            "target_audience": "developers",
            "tone": "technical",
            "presentation_title": "Python Programming Essentials"
        }
        
        print(f"API URL: {api_url}")
        print("Making POST request with test data...")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✓ Presentation created successfully via API!")
            result = response.json()
            print(f"✓ Response ID: {result.get('id')}")
            print(f"✓ Title: {result.get('title')}")
            print(f"✓ Slides count: {len(result.get('slides', []))}")
            return True
        else:
            print(f"✗ API Error: {response.status_code}")
            print(f"✗ Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend server")
        print("  Make sure Django is running: python manage.py runserver 0.0.0.0:8000")
        return False
    except Exception as e:
        print(f"✗ API Test Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "PRESENTATION GENERATION TEST SUITE" + " "*19 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {}
    
    # Test 1: Groq connection
    results['groq'] = test_groq_connection()
    
    # Test 2: User and token
    user_ok, token = test_user_and_token()
    results['user_token'] = user_ok
    
    # Test 3: Presentation generation
    gen_ok, presentation_json = test_presentation_generator()
    results['generation'] = gen_ok
    
    # Test 4: Database storage
    if gen_ok and presentation_json:
        results['database'] = test_database_storage(presentation_json)
    else:
        results['database'] = False
        print_header("TEST 4: Database Storage (SKIPPED - No presentation JSON)")
    
    # Test 5: API endpoint
    if token:
        results['api'] = test_api_endpoint(token)
    else:
        results['api'] = False
        print_header("TEST 5: REST API Endpoint (SKIPPED - No token)")
    
    # Summary
    print_header("TEST SUMMARY")
    
    test_names = [
        ('Groq API Connection', 'groq'),
        ('User & Token Setup', 'user_token'),
        ('Presentation Generation', 'generation'),
        ('Database Storage', 'database'),
        ('REST API Endpoint', 'api'),
    ]
    
    passed = sum(1 for _, key in test_names if results.get(key))
    total = len(test_names)
    
    for name, key in test_names:
        status_icon = "✓" if results.get(key) else "✗"
        status_text = "PASSED" if results.get(key) else "FAILED"
        print(f"{status_icon} {name}: {status_text}")
    
    print(f"\n{'='*70}")
    print(f"Overall: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Check errors above for details.")


if __name__ == '__main__':
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n✗ Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
