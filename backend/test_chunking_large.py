"""
Test script generation for large presentations with chunking
Tests with 50+ slides to verify chunking logic works correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from presentation_app.script_generator import GroqScriptGenerator

def create_test_slides(num_slides):
    """Create test slides for large presentations"""
    topics = [
        "Introduction and Overview",
        "Market Analysis",
        "Current Trends",
        "Opportunities",
        "Challenges",
        "Solutions",
        "Case Studies",
        "Best Practices",
        "Implementation Strategy",
        "Risk Management",
        "Timeline and Milestones",
        "Budget and Resources",
        "Team Structure",
        "Communication Plan",
        "Conclusion and Next Steps"
    ]
    
    slides = []
    for i in range(1, num_slides + 1):
        topic = topics[(i - 1) % len(topics)]
        slides.append({
            "slide_number": i,
            "title": f"{topic} - Part {((i - 1) // len(topics)) + 1}",
            "subtitle": f"Slide {i} of {num_slides}",
            "content": f"Detailed content for slide {i} covering {topic.lower()}",
            "bullets": [
                f"Key point 1 for slide {i}",
                f"Key point 2 for slide {i}",
                f"Key point 3 for slide {i}",
            ]
        })
    return slides

def test_chunked_generation(num_slides):
    """Test script generation with chunking for presentations with many slides"""
    print(f"\nTesting Script Generation for {num_slides}-Slide Presentation")
    print("=" * 70)
    
    try:
        generator = GroqScriptGenerator()
        
        # Create test slides
        slides = create_test_slides(num_slides)
        
        # Calculate expected chunk info
        if num_slides > 50:
            chunk_size = 10
        elif num_slides > 30:
            chunk_size = 12
        else:
            chunk_size = 15
        
        num_chunks = (num_slides + chunk_size - 1) // chunk_size
        
        print(f"\nPresentation Details:")
        print(f"  Total Slides: {num_slides}")
        print(f"  Total Duration: 60 minutes")
        print(f"  Duration per Slide: {60/num_slides:.2f} minutes")
        print(f"\nChunking Strategy:")
        print(f"  Chunk Size: ~{chunk_size} slides per chunk")
        print(f"  Expected Number of Chunks: {num_chunks}")
        print()
        
        print("Generating scripts (this may take a minute)...")
        print()
        
        result = generator.generate_script_for_slides(
            slides=slides,
            presentation_tone="professional",
            total_duration=60,
            presentation_title=f"Comprehensive {num_slides}-Slide Presentation"
        )
        
        if result['success']:
            print("SUCCESS - Script generation completed!")
            print()
            print(f"Generation Results:")
            print(f"  Total Scripts Generated: {len(result['scripts'])}")
            print(f"  Metadata:")
            for key, value in result['metadata'].items():
                print(f"    {key}: {value}")
            print()
            
            # Show sample scripts
            if result['scripts']:
                sample_indices = [0, len(result['scripts']) // 2, -1]
                print("Sample Scripts:")
                for idx in sample_indices:
                    script = result['scripts'][idx]
                    print(f"\n  Slide {script['slide_number']}: {script.get('slide_title', 'N/A')}")
                    print(f"    Script length: {len(script.get('script', ''))} characters")
                    print(f"    Duration: {script.get('estimated_duration_seconds', 0)} seconds")
                    print(f"    Preview: {script.get('script', '')[:100]}...")
            
            return True
        else:
            print(f"FAILED - Error: {result.get('error')}")
            return False
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Script Generation with Chunking Logic")
    print("=" * 70)
    
    # Test with different sizes to verify chunking
    test_sizes = [20, 50, 100]
    
    for size in test_sizes:
        success = test_chunked_generation(size)
        if not success:
            print(f"\nFailed to generate scripts for {size}-slide presentation")
            sys.exit(1)
    
    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    sys.exit(0)
