"""
Test script generation for 30-minute presentation
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from presentation_app.script_generator import GroqScriptGenerator

# Sample presentation for testing
test_slides = [
    {
        "slide_number": 1,
        "title": "Future-Proofing Your Career",
        "subtitle": "Navigating the AI Era",
        "content": "Understanding how to adapt to AI-driven changes in the workplace",
        "bullets": [
            "AI is transforming industries rapidly",
            "New skills are in high demand",
            "Continuous learning is essential"
        ]
    },
    {
        "slide_number": 2,
        "title": "The Current Landscape",
        "subtitle": "",
        "content": "Overview of how AI is already impacting different sectors",
        "bullets": [
            "Tech sector leading adoption",
            "Manufacturing and logistics benefits",
            "Creative industries evolving"
        ]
    },
    {
        "slide_number": 3,
        "title": "Key Skills for the Future",
        "subtitle": "",
        "content": "Essential competencies to remain competitive",
        "bullets": [
            "Critical thinking and problem-solving",
            "Data literacy and interpretation",
            "Human-centered soft skills",
            "Adaptability and continuous learning"
        ]
    },
    {
        "slide_number": 4,
        "title": "Action Plan",
        "subtitle": "",
        "content": "Concrete steps you can take starting today",
        "bullets": [
            "Assess your current skill gaps",
            "Enroll in relevant courses",
            "Build your professional network",
            "Experiment with AI tools"
        ]
    },
    {
        "slide_number": 5,
        "title": "Conclusion",
        "subtitle": "",
        "content": "The future belongs to those who adapt",
        "bullets": [
            "Embrace change as opportunity",
            "Invest in yourself",
            "Stay curious and engaged"
        ]
    }
]

def test_script_generation():
    """Test script generation for 30-minute presentation"""
    print("Testing Script Generation for 30-Minute Presentation")
    print("=" * 60)
    
    try:
        generator = GroqScriptGenerator()
        
        print("\nGenerating scripts for 5 slides over 30 minutes...")
        print("Expected: 6 minutes per slide")
        print()
        
        result = generator.generate_script_for_slides(
            slides=test_slides,
            presentation_tone="professional",
            total_duration=30,
            presentation_title="Future-Proofing Your Career: Why Business Beats Jobs When AI Takes Over"
        )
        
        if result['success']:
            print("SUCCESS - Script generation completed!")
            print()
            print(f"Total scripts generated: {len(result['scripts'])}")
            print(f"Metadata: {result['metadata']}")
            print()
            
            # Show first script as sample
            if result['scripts']:
                first_script = result['scripts'][0]
                print(f"Sample (Slide {first_script['slide_number']}):")
                print(f"Title: {first_script.get('slide_title', 'N/A')}")
                print(f"Script length: {len(first_script.get('script', ''))} characters")
                print(f"Duration: {first_script.get('estimated_duration_seconds', 0)} seconds")
                print()
                print(f"First 500 chars of script:")
                print(first_script.get('script', '')[:500])
        else:
            print(f"FAILED - Error: {result.get('error')}")
            return False
        
        return True
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_script_generation()
    sys.exit(0 if success else 1)
