#!/usr/bin/env python
"""
Test the full API flow with different bullet styles
"""
import requests
import json
import os

# Configuration
BASE_URL = 'http://localhost:8000/api'
TOKEN = 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token {TOKEN}'
}

def test_generate_with_bullet_style(bullet_style):
    """Generate a presentation with a specific bullet style"""
    
    data = {
        'topic': f'Test {bullet_style}',
        'raw_content': 'This is test content. This presentation demonstrates different bullet styles. Each slide shows how the selected style appears. You can choose from numbered, elegant, modern, or professional bullet styles.',
        'target_audience': 'Test Audience',
        'tone': 'professional',
        'bullet_style': bullet_style,
        'template': 'warm_blue',
        'slide_ratio': '16:9'
    }
    
    print(f"\n{'='*60}")
    print(f"Testing bullet_style: '{bullet_style}'")
    print(f"{'='*60}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            f'{BASE_URL}/presentations/generate/',
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Success!")
            print(f"  Presentation ID: {result['id']}")
            print(f"  Title: {result['title']}")
            print(f"  Bullet Style Saved: {result.get('bullet_style', 'NOT FOUND')}")
            print(f"  Total Slides: {result['total_slides']}")
            return result['id']
        else:
            print(f"✗ Failed!")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None

def export_presentation_as_pptx(presentation_id, bullet_style):
    """Export presentation as PPTX"""
    
    print(f"\nExporting presentation {presentation_id} to PPTX...")
    
    try:
        response = requests.get(
            f'{BASE_URL}/presentations/{presentation_id}/export_pptx/',
            headers={'Authorization': f'Token {TOKEN}'},
            timeout=30
        )
        
        if response.status_code == 200:
            filename = f'test_api_{bullet_style}.pptx'
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✓ Exported: {filename} ({len(response.content)} bytes)")
        else:
            print(f"✗ Export failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("FULL API FLOW TEST - BULLET STYLES")
    print("="*60)
    
    bullet_styles = ['numbered', 'bullet_elegant', 'bullet_modern', 'bullet_professional']
    
    for style in bullet_styles:
        presentation_id = test_generate_with_bullet_style(style)
        if presentation_id:
            export_presentation_as_pptx(presentation_id, style)
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)
