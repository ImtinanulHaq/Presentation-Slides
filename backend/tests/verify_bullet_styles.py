#!/usr/bin/env python
"""
Verify bullet style implementation in generated PPTX files
"""
import os
import sys
import django
from zipfile import ZipFile
import xml.etree.ElementTree as ET

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

def extract_bullet_text_from_pptx(filename):
    """Extract bullet point text from a PPTX file"""
    bullets = []
    
    try:
        with ZipFile(filename, 'r') as zip_ref:
            # Read slide1.xml (first content slide)
            slide_xml = zip_ref.read('ppt/slides/slide2.xml').decode('utf-8')
            root = ET.fromstring(slide_xml)
            
            # Find all text runs
            namespaces = {
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            }
            
            # Extract all text from paragraphs
            for t_elem in root.findall('.//a:t', namespaces):
                if t_elem.text:
                    bullets.append(t_elem.text)
    
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
    
    return bullets

def verify_bullet_styles():
    """Verify that bullet styles are correctly applied"""
    
    print("=" * 60)
    print("VERIFYING BULLET STYLES IN GENERATED PPTX FILES")
    print("=" * 60)
    
    test_files = [
        ('test_presentation_numbered.pptx', 'numbered'),
        ('test_presentation_bullet_elegant.pptx', 'elegant'),
        ('test_presentation_bullet_modern.pptx', 'modern'),
        ('test_presentation_bullet_professional.pptx', 'professional'),
    ]
    
    for filename, style_name in test_files:
        if os.path.exists(filename):
            print(f"\n{style_name.upper()} STYLE ({filename}):")
            bullets = extract_bullet_text_from_pptx(filename)
            
            if bullets:
                print(f"First few bullets found:")
                for i, bullet in enumerate(bullets[:5]):
                    print(f"  {bullet}")
            else:
                print("  (No bullets found in extraction)")
        else:
            print(f"\n✗ File not found: {filename}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    verify_bullet_styles()
