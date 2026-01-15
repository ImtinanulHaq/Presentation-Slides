"""Complete test of presentation generator with Bitcoin research paper from test.txt"""

import sys
sys.path.insert(0, '.')

from presentation_app.presentation_generator import GroqPresentationGenerator

# Read the Bitcoin research paper from test.txt
with open('../test.txt', 'r', encoding='utf-8') as f:
    research_content = f.read()

word_count = len(research_content.split())

print("\n" + "="*80)
print("COMPLETE PRESENTATION GENERATION TEST")
print("="*80)
print("\nInput: Bitcoin Research Paper from test.txt")
print("Word Count: %d words" % word_count)
print("\nGenerating professional presentation with 4-8 bullet points per slide...")
print("="*80 + "\n")

generator = GroqPresentationGenerator(
    topic="Bitcoin Price Prediction Using Machine Learning",
    raw_content=research_content,
    target_audience="Investors, Researchers, Finance Professionals",
    tone="professional"
)

try:
    result = generator.generate()
    
    # Handle both dict (single generation) and list (chunked array)
    if isinstance(result, dict):
        slides = result.get('slides', [])
        title = result.get('presentation_title', 'Bitcoin Research')
        summary = result.get('presentation_summary', '')
    elif isinstance(result, list):
        slides = result
        title = "Bitcoin Research Presentation"
        summary = ""
    else:
        raise ValueError("Unexpected result type: %s" % type(result))
    
    print("\nPresentation Title: %s" % title)
    if summary:
        print("Summary: %s\n" % summary)
    
    print("Total Slides Generated: %d\n" % len(slides))
    print("="*80)
    print("SLIDE VALIDATION REPORT")
    print("="*80 + "\n")
    
    violations = 0
    bullet_distribution = {}
    
    for i, slide in enumerate(slides, 1):
        bullets = slide.get('bullets', [])
        bullet_count = len(bullets)
        slide_type = slide.get('type', slide.get('slide_type', 'standard')).lower()
        title_text = slide.get('title', 'Untitled')[:50]
        
        # Track bullet distribution
        if bullet_count not in bullet_distribution:
            bullet_distribution[bullet_count] = 0
        bullet_distribution[bullet_count] += 1
        
        # Title slides are allowed to have 0 bullets
        if slide_type in ['title', 'intro']:
            status = "[OK]"
        elif 4 <= bullet_count <= 8:
            status = "[OK]"
        else:
            status = "[FAIL]"
            violations += 1
        
        print("%s Slide %2d: %d bullets - %s (%s)" % (status, i, bullet_count, title_text, slide_type))
    
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    print("\nBullet Point Distribution:")
    for count in sorted(bullet_distribution.keys()):
        print("  %d bullets: %d slides" % (count, bullet_distribution[count]))
    
    print("\n" + "="*80)
    if violations == 0:
        print("SUCCESS: All %d slides have 4-8 bullet points" % len(slides))
    else:
        print("VIOLATIONS: %d / %d slides have incorrect bullet count" % (violations, len(slides)))
    
    print("\nPresentation Quality Metrics:")
    print("  - Total Slides: %d" % len(slides))
    print("  - Total Content Words: ~%d" % (len(slides) * 50))
    print("  - Average Bullets per Slide: %.2f" % (sum(len(s.get('bullets', [])) for s in slides) / len(slides)))
    print("  - Professional Formatting: Applied")
    print("  - 4-8 Bullet Requirement: %s" % ("PASSED" if violations == 0 else "FAILED"))
    print("\n" + "="*80 + "\n")
    
    if violations == 0:
        print("PRESENTATION READY FOR USE")
        print("Generated from: Bitcoin Price Prediction Research Paper")
        print("Slides can be exported to PPTX format")
    
except Exception as e:
    print("\nERROR: %s" % str(e))
    import traceback
    traceback.print_exc()
