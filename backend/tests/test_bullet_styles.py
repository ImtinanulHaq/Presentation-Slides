#!/usr/bin/env python
"""
Test bullet style functionality in PPTX generation
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from presentation_app.models import Presentation, Slide
from presentation_app.pptx_generator import generate_pptx

def test_bullet_styles():
    """Test different bullet styles in PPTX generation"""
    
    # Get a test presentation
    presentation = Presentation.objects.get(id=113)
    
    print("=" * 60)
    print("TESTING BULLET STYLES IN PPTX GENERATION")
    print("=" * 60)
    
    bullet_styles = ['numbered', 'bullet_elegant', 'bullet_modern', 'bullet_professional']
    
    for style in bullet_styles:
        try:
            print(f"\nGenerating PPTX with bullet_style='{style}'...")
            pptx_file = generate_pptx(
                presentation, 
                template_name='rose_elegance',
                slide_ratio='16:9',
                bullet_style=style
            )
            
            # Save to file for verification
            filename = f"test_presentation_{style}.pptx"
            with open(filename, 'wb') as f:
                f.write(pptx_file.getvalue())
            
            file_size = os.path.getsize(filename)
            print(f"✓ Successfully generated: {filename} ({file_size} bytes)")
            
        except Exception as e:
            print(f"✗ Error generating with style '{style}': {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
    print("\nGenerated files can be found in the current directory.")
    print("You can now verify that each file has the correct bullet style applied.")

if __name__ == '__main__':
    test_bullet_styles()
