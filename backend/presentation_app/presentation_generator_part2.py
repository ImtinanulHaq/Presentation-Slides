"""
Groq-Based Presentation Generator - PART 2
Continuation of presentation_generator.py with remaining methods
"""

# This file should be appended to presentation_generator.py after line 539
# Contains the _build_prompt method

def _build_prompt(self, content: str = None) -> str:
    """Build comprehensive prompt for slide generation
    
    Calculates optimal slide count based on professional word-to-slide ratios.
    Ensures 4-8 bullet points per slide with detailed content preservation.
    """
    
    if content is None:
        content = self.raw_content
    
    # Calculate optimal slide count
    word_count = len(content.split())
    slide_calc = self._calculate_optimal_slides(word_count)
    
    num_slides = slide_calc['recommended']
    
    return f"""You are an expert professional presentation designer.
Create a comprehensive presentation with detailed, high-quality slides.

================================================================================
PRESENTATION GUIDELINES
================================================================================
Topic: {self.topic}
Target Audience: {self.target_audience}
Tone: {self.tone}
Total Word Count: {word_count} words
Recommended Slides: {num_slides} slides

Professional Word-to-Slide Ratio:
• 1000+ words: 3 slides per 100 words (detailed content)
• 500-999 words: 4-5 slides per 100 words (balanced detail)
• 300-499 words: 4-5 slides per 100 words (detailed breakdown)
• 100-299 words: 5-8 slides per 100 words (comprehensive coverage)
• <100 words: 3-8 slides minimum

CONTENT TO CONVERT INTO SLIDES
================================================================================
{content}

================================================================================
CRITICAL REQUIREMENTS - BULLET POINTS (PROFESSIONAL STANDARD)
================================================================================
⚠️ MANDATORY BULLET POINT RULES:
✓ EVERY slide MUST have 4-8 bullet points (no exceptions)
✓ Minimum: 4 points per slide (ensures detailed content)
✓ Maximum: 8 points per slide (maintains readability)
✓ NO slides with 1, 2, or 3 points (unprofessional)
✓ NO slides with more than 8 points (unreadable)

📝 BULLET POINT CONTENT:
1. Each point: 8-15 words maximum (concise but detailed)
2. Start with strong action verbs or key terms
3. Include specific numbers, metrics, dates, evidence from content
4. Each point must be distinct and non-repetitive
5. Never use generic placeholder text
6. Reference actual information from the provided content
7. All points must support the slide title

💼 CONTENT COVERAGE REQUIREMENTS:
• Include ALL significant information from the provided content
• No important details should be skipped
• If content has statistics, metrics, or numbers - include them
• If content has multiple concepts - represent each one
• Preserve all critical data points and context
• Balance detail across all slides proportionally

================================================================================
PROFESSIONAL FORMATTING & SYMBOLS
================================================================================
Use ONLY professional symbols for bullets (NO basic bullet points):

For 4-point slides: ▪ ▸ ◆ ■
For 5-point slides: ▪ ▸ ◆ ■ ★
For 6-point slides: ▪ ▸ ◆ ■ ★ ●
For 7-point slides: ▪ ▸ ◆ ■ ★ ● ✓
For 8-point slides: ▪ ▸ ◆ ■ ★ ● ✓ →

================================================================================
EMOJI USAGE RULES (SELECTIVE & PROFESSIONAL ONLY)
================================================================================
Use emojis SPARINGLY - only when contextually appropriate:

✅ APPROPRIATE EMOJI CONTEXTS:
📊 📈 💹 - Financial metrics, growth data, statistics (numbers only)
🔧 💻 🔐 - Technical concepts, IT, security (tech topics only)
✅ - Achievements, successes, milestones (only when celebrating)
🎯 - Strategic goals, objectives, targets (only for goals)
⚠️ - Critical warnings, risks, important cautions (only warnings)
📅 ⏱️ - Timeline, scheduling, time-based content (only dates/time)

❌ NEVER USE:
😊 😄 👍 - Casual/cute emojis (unprofessional)
🌟 ⭐ 💫 - Generic decorative emojis
Multiple emojis per slide (maximum 1-2 per slide)
Emojis in formal/academic presentations
Emojis for regular descriptive text

Default to professional symbols instead of emojis when possible.

================================================================================
SLIDE STRUCTURE & ORGANIZATION
================================================================================
✓ Create {num_slides} high-quality slides total
✓ Each slide has ONE main topic/concept/theme
✓ Organize content logically with clear progression
✓ Each slide builds on previous knowledge
✓ Group related information together
✓ Use consistent formatting throughout
✓ Professional hierarchy and visual flow

================================================================================
OUTPUT REQUIREMENTS
================================================================================
1. Output ONLY valid JSON array - NO explanations, markdown, or code
2. Each slide MUST have exactly 4-8 bullet points
3. All content must come from the provided input (no external info)
4. Maintain {self.tone} tone throughout
5. Professional, corporate-quality presentation
6. No typos, grammatical errors, or formatting issues

================================================================================
REQUIRED JSON FORMAT (VALID JSON ONLY)
================================================================================
[
  {{
    "title": "Clear, Descriptive Slide Title",
    "type": "standard",
    "bullets": [
      "Point 1: Detailed content with specific information",
      "Point 2: Include numbers, data, or evidence from content",
      "Point 3: Expand key concepts from the source",
      "Point 4: Additional supporting details"
    ]
  }},
  {{
    "title": "Next Slide Title",
    "type": "standard",
    "bullets": [
      "Point 1: Information from content",
      "Point 2: More detailed points",
      "Point 3: Supporting evidence",
      "Point 4: Context or examples",
      "Point 5: [optional: 5-8 points allowed]"
    ]
  }}
]

================================================================================
VALIDATION CHECKLIST BEFORE OUTPUT
================================================================================
□ Total slides = {num_slides}
□ EVERY slide has 4-8 bullets (count them!)
□ NO slide has fewer than 4 or more than 8 points
□ All content from provided text (no external info)
□ Professional symbols used (▪ ▸ ◆ ■ ★ ● ✓ →)
□ Emojis used ONLY when contextually appropriate (max 1-2)
□ All points are 8-15 words
□ No typos or grammatical errors
□ {self.tone} tone maintained
□ Valid JSON format (no syntax errors)

CRITICAL: Count bullets in each slide. No exceptions - 4-8 points mandatory.
"""
