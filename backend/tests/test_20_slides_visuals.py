#!/usr/bin/env python
"""
Test script to generate 20 slides with visuals enabled.
Tests both exact slide count enforcement and visual feature.
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from presentation_app.models import Presentation

# API endpoint
API_URL = "http://localhost:8000/api/presentations/generate/"

# Test token from .env
TOKEN = "b1bf242b1c8a2b638e79f0b282599ffafea3faf3"

def test_20_slides_with_visuals():
    """Test generating 20 slides with visuals enabled."""
    
    print("\n" + "="*70)
    print("TEST: 20 SLIDES WITH VISUALS ENABLED")
    print("="*70)
    
    test_data = {
        "presentation_title": "Comprehensive Business Strategy 2026",
        "topic": "Strategic Business Planning and Digital Transformation",
        "target_audience": "Business Executives",
        "tone": "professional",
        "raw_content": """
        Strategic business planning is essential for organizations in today's competitive digital landscape.
        
        STRATEGIC VISION:
        Organizations must develop clear strategic visions that align with market opportunities and organizational capabilities. 
        This involves comprehensive market analysis, competitive positioning, and long-term goal setting.
        
        DIGITAL TRANSFORMATION:
        Digital transformation encompasses organizational restructuring, technology adoption, and process innovation.
        Companies are leveraging AI, cloud computing, and big data analytics to enhance operational efficiency.
        Digital platforms enable real-time collaboration, data-driven decision making, and enhanced customer experiences.
        
        FINANCIAL MANAGEMENT:
        Sound financial management includes budget planning, cash flow optimization, and risk management.
        Organizations must balance short-term profitability with long-term sustainable growth.
        Investment in R&D and employee development creates competitive advantages.
        
        LEADERSHIP AND CULTURE:
        Effective leadership drives organizational change and builds strong company culture.
        Leaders must foster innovation, encourage cross-functional collaboration, and develop talent.
        Organizational culture impacts employee engagement, retention, and productivity.
        
        MARKET POSITIONING:
        Companies must continuously monitor market trends and customer needs.
        Competitive differentiation comes through unique value propositions and superior customer service.
        Brand development and customer loyalty programs are critical for market leadership.
        
        INNOVATION STRATEGY:
        Innovation drives competitive advantage and long-term success.
        Organizations must encourage experimentation, embrace calculated risks, and learn from failures.
        Product innovation, service innovation, and business model innovation are all important.
        
        OPERATIONAL EXCELLENCE:
        Efficient operations reduce costs and improve quality.
        Lean methodologies, process automation, and continuous improvement are essential.
        Supply chain optimization and quality management create operational excellence.
        
        STAKEHOLDER ENGAGEMENT:
        Managing relationships with customers, employees, investors, and partners is crucial.
        Transparent communication builds trust and strengthens relationships.
        Corporate social responsibility addresses stakeholder concerns about sustainability and ethics.
        
        PERFORMANCE METRICS:
        Organizations must establish clear KPIs and monitor performance regularly.
        Data analytics provides insights for performance improvement and strategic decisions.
        Balanced scorecards align business activities with strategic objectives.
        
        RISK MANAGEMENT:
        Identifying and mitigating risks protects organizational assets and ensures continuity.
        Risk assessment frameworks help organizations prepare for various scenarios.
        Crisis management and business continuity planning ensure organizational resilience.
        
        This comprehensive content should generate approximately 20 detailed slides covering all aspects of business strategy.
        """,
        "num_slides": 20,
        "enable_visuals": True
    }
    
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"\nSending request to: {API_URL}")
    print(f"Slides requested: 20")
    print(f"Visuals enabled: True")
    print(f"Content length: {len(test_data['raw_content'])} characters")
    print("\nRequest payload:")
    print(json.dumps({k: v for k, v in test_data.items() if k != 'raw_content'}, indent=2))
    
    try:
        response = requests.post(API_URL, json=test_data, headers=headers)
        
        print(f"\n{'='*70}")
        print(f"Response Status: {response.status_code}")
        print(f"{'='*70}")
        
        if response.status_code == 201:
            response_data = response.json()
            
            print(f"\n[SUCCESS] Presentation generated!")
            print(f"\nPresentation ID: {response_data.get('id')}")
            print(f"Title: {response_data.get('title')}")
            print(f"Status: {response_data.get('status')}")
            
            # Check slides
            slides = response_data.get('slides', [])
            print(f"\nTotal slides generated: {len(slides)}")
            
            if len(slides) == 20:
                print("[PASS] Exact slide count verified (20/20)")
            else:
                print(f"[WARN] Slide count mismatch: Expected 20, got {len(slides)}")
            
            # Check for visuals in slides
            slides_with_visuals = 0
            slides_without_visuals = 0
            
            print("\n" + "-"*70)
            print("VISUAL CONTENT ANALYSIS")
            print("-"*70)
            
            for i, slide in enumerate(slides, 1):
                has_visual = False
                
                # Check for visual data
                visuals_data = slide.get('visuals') or slide.get('slide_visuals')
                bullet_visuals_count = 0
                
                if visuals_data:
                    has_visual = True
                    slides_with_visuals += 1
                    print(f"\nSlide {i}: {slide.get('title', 'No title')}")
                    print(f"  [YES] Has slide-level visuals:")
                    if isinstance(visuals_data, dict):
                        print(f"     - Icons: {visuals_data.get('slide_icons', [])}")
                        print(f"     - Symbols: {visuals_data.get('slide_symbols', [])}")
                        print(f"     - Image ideas: {visuals_data.get('slide_image_ideas', [])}")
                else:
                    slides_without_visuals += 1
                    print(f"\nSlide {i}: {slide.get('title', 'No title')}")
                    print(f"  [NO] No slide-level visuals data")
                
                # Check bullets for per-bullet visuals
                if slide.get('bullets'):
                    bullets = slide.get('bullets', [])
                    print(f"  Bullets: {len(bullets)}")
                    for j, bullet in enumerate(bullets[:2], 1):  # Show first 2 bullets
                        if isinstance(bullet, dict):
                            text = bullet.get('text', bullet)
                            icon = bullet.get('icon', 'N/A')
                            emoji = bullet.get('emoji', 'N/A')
                            color = bullet.get('color', 'N/A')
                            if icon != 'N/A' or emoji != 'N/A' or color != 'N/A':
                                bullet_visuals_count += 1
                                print(f"    • {text[:50]}...")
                                print(f"      Icon: {icon}, Emoji: {emoji}, Color: {color}")
                            else:
                                print(f"    • {text[:50]}...")
                        else:
                            print(f"    • {str(bullet)[:60]}...")
                    
                    if bullet_visuals_count > 0:
                        has_visual = True
                        if i not in [idx+1 for idx, s in enumerate(slides) if s.get('visuals') or s.get('slide_visuals')]:
                            slides_with_visuals += 1
            
            print(f"\n{'='*70}")
            print("VISUAL FEATURE VERIFICATION")
            print(f"{'='*70}")
            print(f"Slides with visual elements: {slides_with_visuals}/{len(slides)}")
            print(f"Slides without visual elements: {slides_without_visuals}/{len(slides)}")
            
            # Count total per-bullet visuals
            total_bullet_visuals = 0
            for slide in slides:
                if slide.get('bullets'):
                    for bullet in slide.get('bullets', []):
                        if isinstance(bullet, dict) and (bullet.get('icon') or bullet.get('emoji') or bullet.get('color')):
                            total_bullet_visuals += 1
            
            print(f"\nPer-bullet visuals found: {total_bullet_visuals}")
            
            if slides_with_visuals > 0 or total_bullet_visuals > 0:
                print("[PASS] VISUAL FEATURE IS WORKING!")
                print(f"   - Slide-level visuals: {slides_with_visuals} slides")
                print(f"   - Per-bullet visuals: {total_bullet_visuals} bullets")
            else:
                print("[FAIL] No visual elements found in any slides")
            
            return True
        
        elif response.status_code == 400:
            print("\n[FAIL] BAD REQUEST (400)")
            print("\nError response:")
            print(json.dumps(response.json(), indent=2))
            return False
        
        elif response.status_code == 401:
            print("\n[FAIL] UNAUTHORIZED (401)")
            print("Token issue or authentication failed")
            print(f"Response: {response.text}")
            return False
        
        else:
            print(f"\n[FAIL] ERROR ({response.status_code})")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"\n[ERROR] EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_20_slides_with_visuals()
    sys.exit(0 if success else 1)
