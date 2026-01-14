"""
Groq-Based Presentation Generator
Converts raw content to structured JSON using Groq LLM API
"""

import json
from groq import Groq
import os
import re
from .content_chunker import ContentChunker, create_chunked_prompt


def repair_json_string(json_str: str) -> str:
    """
    Attempt to repair common JSON formatting issues
    Handles incomplete structures, missing commas, trailing commas, etc.
    """
    # Remove any leading/trailing whitespace
    json_str = json_str.strip()
    
    # Fix trailing commas before closing brackets/braces
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Try to complete incomplete JSON structures
    # Count opening and closing braces
    open_braces = json_str.count('{')
    close_braces = json_str.count('}')
    
    if open_braces > close_braces:
        json_str += '}' * (open_braces - close_braces)
    
    # Count opening and closing brackets
    open_brackets = json_str.count('[')
    close_brackets = json_str.count(']')
    
    if open_brackets > close_brackets:
        json_str += ']' * (open_brackets - close_brackets)
    
    return json_str


class GroqPresentationGenerator:
    """Generate presentation structure using Groq API"""
    
    def __init__(self, topic: str, raw_content: str, target_audience: str, tone: str, num_slides: int = None, enable_chunking: bool = False, enable_visuals: bool = True):
        self.topic = topic
        self.raw_content = raw_content
        self.target_audience = target_audience
        self.tone = tone
        self.num_slides = num_slides  # User-specified slide count (optional)
        
        # AUTO-ENABLE CHUNKING if content is very large
        # Groq TPM limit: 6000 tokens, so keep single request under ~4500 tokens to be safe
        # 1 word ≈ 1.3 tokens, so ~3500 words = 4550 tokens
        # If content > 3500 words (4500+ tokens), auto-enable chunking
        content_word_count = len(raw_content.split())
        if content_word_count > 3500 and not enable_chunking:
            print(f"[AUTO-CHUNKING] Content has {content_word_count} words (>3500 limit). Auto-enabling chunking.")
            enable_chunking = True
        
        self.enable_chunking = enable_chunking  # Enable content chunking for large inputs
        self.enable_chunking = enable_chunking  # Enable content chunking for large inputs
        self.enable_visuals = enable_visuals  # Enable visual suggestions for bullets
        # Get API key from environment or use default
        api_key = os.environ.get('GROQ_API_KEY', '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')
        try:
            self.client = Groq(api_key=api_key)
        except TypeError:
            # Fallback for httpx compatibility issues
            self.client = Groq(api_key=api_key, http_client=None)
        
    def generate(self) -> dict:
        """Generate complete presentation JSON using Groq"""
        
        # VALIDATION LAYER - Ensure all input is properly formatted
        try:
            # Validate num_slides
            if self.num_slides is not None:
                if not isinstance(self.num_slides, int):
                    self.num_slides = int(self.num_slides)
                if self.num_slides < 3 or self.num_slides > 100:
                    raise ValueError(f"num_slides must be between 3 and 100, got {self.num_slides}")
            
            # Validate required fields
            if not self.topic or not isinstance(self.topic, str):
                raise ValueError("topic must be a non-empty string")
            if not self.raw_content or not isinstance(self.raw_content, str):
                raise ValueError("raw_content must be a non-empty string")
            if not self.target_audience or not isinstance(self.target_audience, str):
                raise ValueError("target_audience must be a non-empty string")
            if self.tone not in ['professional', 'casual', 'academic', 'persuasive']:
                raise ValueError(f"tone must be one of ['professional', 'casual', 'academic', 'persuasive'], got {self.tone}")
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"Input validation failed: {str(e)}")
        
        # Check if chunking should be used
        # IMPORTANT: If user specified exact slide count, always use single method
        # because chunking doesn't respect num_slides properly
        if self.enable_chunking and not self.num_slides:
            return self._generate_chunked()
        else:
            return self._generate_single()
    
    def _generate_single(self) -> dict:
        """Generate presentation from single content (standard flow)"""
        
        try:
            prompt = self._build_prompt()
        except Exception as e:
            raise ValueError(f"Failed to build prompt: {str(e)}")
        
        # Conservative token limits to stay under Groq's 6000 TPM limit
        # Calculation: Prompt tokens + response tokens must be < 6000
        # Safe approach: limit response to 3000 tokens max
        max_tokens = 3000
        if self.num_slides and self.num_slides > 20:
            # For very large slide counts, use smaller max_tokens 
            # The content chunking should have been auto-enabled anyway
            max_tokens = 2000
        
        try:
            # Using latest available Groq model
            message = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            
            response_text = message.choices[0].message.content
            
            # Parse JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end <= json_start:
                raise ValueError("No valid JSON object found in Groq response")
            
            json_str = response_text[json_start:json_end]
            
            # Try to repair common JSON issues
            try:
                json_str_repaired = repair_json_string(json_str)
                presentation_json = json.loads(json_str_repaired)
                return presentation_json
            except json.JSONDecodeError as repair_error:
                # If repair didn't work, try original JSON
                try:
                    presentation_json = json.loads(json_str)
                    return presentation_json
                except json.JSONDecodeError as original_error:
                    # Detailed error reporting
                    error_msg = f"JSON parsing failed after repair attempt. "
                    error_msg += f"Repair error: {str(repair_error)}. "
                    error_msg += f"Original error: {str(original_error)}. "
                    error_msg += f"JSON preview: {json_str[:200]}..."
                    raise ValueError(error_msg)
                    
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a token limit error from Groq
            if "rate_limit_exceeded" in error_str or "tokens per minute" in error_str or "Request too large" in error_str:
                # Token limit exceeded - suggest retry with chunking
                suggestion = "Content is too large for single request. Retrying with automatic chunking..."
                print(f"[TOKEN LIMIT ERROR] {suggestion}")
                # Auto-enable chunking and retry
                if not self.enable_chunking:
                    self.enable_chunking = True
                    print("[AUTO-RETRY] Retrying with chunking enabled...")
                    return self._generate_chunked()
                else:
                    raise Exception(f"Even with chunking, token limit exceeded: {str(e)}")
            
            # If it's already a ValueError, re-raise as-is
            if isinstance(e, ValueError):
                raise
            # Otherwise wrap it
            raise Exception(f"Groq API call failed: {str(e)}")
    
    def _generate_chunked(self) -> dict:
        """Generate presentation from chunked content for large inputs"""
        
        chunker = ContentChunker()
        chunks = chunker.chunk_content(self.raw_content)
        
        if len(chunks) == 1:
            # Content fits in single chunk, use normal flow
            return self._generate_single()
        
        # Process each chunk and collect slides
        all_slides = []
        slide_number = 1
        
        try:
            # Create overview slide
            all_slides.append({
                "slide_number": slide_number,
                "slide_type": "title",
                "title": f"Comprehensive Overview: {self.topic}",
                "subtitle": f"Content compiled from {len(chunks)} major sections",
                "bullets": [],
                "speaker_notes": f"This presentation covers {self.topic} across {len(chunks)} comprehensive sections.",
                "visuals": {"icons": ["presentation"], "symbols": []}
            })
            slide_number += 1
            
            # Process each chunk
            for chunk_idx, chunk in enumerate(chunks):
                chunk_prompt = self._build_chunk_prompt(chunk, chunk_idx + 1, len(chunks))
                
                message = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "user",
                            "content": chunk_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                )
                
                response_text = message.choices[0].message.content
                
                # Parse JSON from response
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    chunk_slides = json.loads(json_str)
                    
                    # Renumber slides
                    for slide in chunk_slides:
                        slide['slide_number'] = slide_number
                        all_slides.append(slide)
                        slide_number += 1
            
            # Add conclusion slide
            all_slides.append({
                "slide_number": slide_number,
                "slide_type": "conclusion",
                "title": "Conclusion & Key Takeaways",
                "subtitle": f"{self.topic} Summary",
                "bullets": [
                    "Covered comprehensive material across all sections",
                    "Ready to discuss questions and next steps",
                    "All key points integrated into structured presentation"
                ],
                "speaker_notes": "Thank you for reviewing this comprehensive presentation. We've covered all major aspects.",
                "visuals": {"icons": ["checkmark"], "symbols": []}
            })
            
            # Create final JSON structure
            return {
                "presentation_title": f"{self.topic} - Comprehensive Presentation",
                "topic": self.topic,
                "target_audience": self.target_audience,
                "tone": self.tone,
                "total_slides": slide_number - 1,
                "slides": all_slides,
                "metadata": {
                    "generated_with_chunking": True,
                    "number_of_chunks": len(chunks),
                    "total_tokens_estimated": sum(
                        int(len(chunk.split()) * 1.3) for chunk in chunks
                    )
                }
            }
            
        except Exception as e:
            raise Exception(f"Error generating chunked presentation: {str(e)}")
    
    def _build_chunk_prompt(self, chunk: str, chunk_num: int, total_chunks: int) -> str:
        """Build prompt for processing a single chunk"""
        
        return f"""You are a presentation slide generator for chunked content. Create comprehensive slides for this section.

CRITICAL - CHUNK CONTEXT:
This is chunk {chunk_num} of {total_chunks} - part of a larger presentation.
Generate slides for THIS CHUNK ONLY. Do not reference other chunks.

CHUNK CONTENT:
{chunk}

REQUIREMENTS:
1. Output ONLY valid JSON array of slides - no markdown, no explanations
2. Create 2-4 comprehensive slides from this chunk's content
3. Maximize content coverage - include all information from the chunk
4. Use bullet points (max 12 words each) - directly from chunk content
5. Speaker notes: Expand on the chunk's content only (no external information)
6. Maintain "{self.tone}" tone throughout
7. Professional structure and organization

VISUAL SUGGESTIONS:
- Analyze each bullet's content
- Suggest RELEVANT icons based on bullet's meaning
- Suggest emojis matching the content
- Suggest colors aligned with tone and content
- All visuals MUST relate directly to chunk content

DATA-ONLY CONSTRAINT:
Use ONLY information from the chunk above. Do NOT add external knowledge.

SLIDE FORMAT:
[
  {{
    "slide_type": "content",
    "title": "Section title from chunk",
    "subtitle": "Optional subtitle",
    "bullets": [
      {{
        "text": "Bullet point from chunk (max 12 words)",
        "icon": "relevant-icon-name",
        "emoji": "📊",
        "color": "color-name"
      }},
      {{
        "text": "Another point from chunk",
        "icon": "relevant-icon-name",
        "emoji": "✓",
        "color": "color-name"
      }}
    ],
    "slide_visuals": {{
      "slide_icons": ["icon1"],
      "slide_symbols": ["symbol"],
      "slide_image_ideas": ["Specific image description from chunk"]
    }},
    "speaker_notes": "Detailed explanation from chunk content only"
  }}
]

COMPREHENSIVE COVERAGE:
Ensure ALL information from this chunk is covered across the generated slides.
Use all available space in 2-4 slides to properly present the chunk's content.

NOW GENERATE JSON ARRAY OF SLIDES (JSON ONLY):"""
    
    def _build_prompt(self) -> str:
        """Build the prompt for Groq API with professional guidelines"""
        
        try:
            # Build slide count instruction - STRICT
            if self.num_slides:
                if not isinstance(self.num_slides, int):
                    self.num_slides = int(self.num_slides)
                num_slides = self.num_slides
                num_content_slides = max(1, self.num_slides - 2)  # Ensure at least 1 content slide
                slide_instruction = f"""CRITICAL REQUIREMENT - SLIDE COUNT:
Generate EXACTLY {num_slides} slides (not more, not less).
The {num_slides} slides MUST include:
  - 1 Title slide
  - {num_content_slides} Content slides (comprehensive coverage of all content)
  - 1 Conclusion/Summary slide

You MUST use all {num_slides} slides. Cover ALL content comprehensively across these slides."""
            else:
                slide_instruction = """INTELLIGENT SLIDE COUNT:
Determine the appropriate number of slides based on content volume and complexity:
- For brief content (100-200 words): 3-4 slides
- For moderate content (200-500 words): 5-7 slides  
- For extensive content (500-1000 words): 8-12 slides
- For comprehensive content (1000+ words): 13-20 slides

Always include: 1 Title slide + Content slides + 1 Conclusion slide.
Ensure COMPREHENSIVE coverage - no content should be omitted.
Structure logically with clear sections."""
        except (ValueError, TypeError) as e:
            raise ValueError(f"Error building slide instruction: {str(e)}")
        
        # Build visual instructions based on enable_visuals flag
        if self.enable_visuals:
            visual_requirements = """7. VISUAL SUGGESTIONS: Analyze content carefully and suggest appropriate visuals
8. Per-bullet visuals: Each bullet gets icon, emoji, color recommendation
9. Slide-level visuals: Icons, symbols, and image ideas for the entire slide

VISUAL GUIDELINES:
- Analyze the content of each bullet point
- Suggest RELEVANT icons based on bullet's meaning (not generic)
- Suggest emojis that represent the concept
- Suggest colors that match the tone and content
- Suggest specific image descriptions (not generic "business image")
- All visual suggestions MUST relate to the actual bullet content"""
            
            visual_json = """  "bullets": [
        {{
          "text": "Bullet point from content (max 12 words)",
          "icon": "relevant-icon-name",
          "emoji": "📊",
          "color": "color-name"
        }},
        {{
          "text": "Second bullet from content",
          "icon": "relevant-icon-name",
          "emoji": "✓",
          "color": "color-name"
        }},
        {{
          "text": "Third bullet with evidence from content",
          "icon": "relevant-icon-name", 
          "emoji": "⭐",
          "color": "color-name"
        }}
      ],
      "slide_visuals": {{
        "slide_icons": ["icon1", "icon2"],
        "slide_symbols": ["symbol"],
        "slide_image_ideas": ["Specific image description from content topic"]
      }},"""
            
            visual_examples = """VISUAL EXAMPLE:
If bullet says "Increased sales by 45%":
  - icon: "trending-up" or "chart-line"
  - emoji: "📈"
  - color: "green" (growth color)

If bullet says "Reduce manual work":
  - icon: "automation" or "tools"
  - emoji: "🔧"
  - color: "blue" (efficiency color)

IMPORTANT: Every visual MUST directly relate to the bullet's actual content.
"""
        else:
            visual_requirements = "7. No visual suggestions needed - focus on text content only"
            visual_json = """  "bullets": [
        "Bullet point from content (max 12 words)",
        "Second bullet from content",
        "Third bullet with evidence from content"
      ],
      "visuals": {{
        "icons": [],
        "symbols": [],
        "image_ideas": []
      }},"""
            visual_examples = ""
        
        # Build the complete prompt with proper variable substitution
        # Handle slide count in the prompt sections
        if self.num_slides:
            slide_range = f"2 to {self.num_slides - 1}"
            final_slide_num = self.num_slides
            total_slides_val = self.num_slides
        else:
            slide_range = "2 to (auto_determined_total - 1)"
            final_slide_num = "auto_determined_total"
            total_slides_val = "auto_determined_appropriate_number"
        
        return f"""You are a professional presentation structure organizer. Your task is to create comprehensive, well-structured presentations from user content.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL CONSTRAINTS - MUST FOLLOW EXACTLY
═══════════════════════════════════════════════════════════════════════════════

1. DATA SOURCE ONLY:
   ⚠️ USE ONLY THE PROVIDED CONTENT - DO NOT ADD, INVENT, OR SUPPLEMENT WITH EXTERNAL DATA
   ⚠️ EVERY FACT, POINT, AND STATEMENT MUST COME DIRECTLY FROM THE INPUT CONTENT
   ⚠️ IF THE CONTENT DOESN'T HAVE INFORMATION, DON'T INVENT IT
   ⚠️ DO NOT ADD EXAMPLES, STATISTICS, OR DETAILS NOT PROVIDED BY USER

2. COMPREHENSIVE COVERAGE:
   ⚠️ ALL content from the input MUST be covered in the slides
   ⚠️ No important information should be omitted
   ⚠️ Organize content logically across slides
   ⚠️ Each slide should have 2-4 well-structured bullets (not too many, not too few)

3. SLIDE COUNT RULE:
{slide_instruction}

═══════════════════════════════════════════════════════════════════════════════
PRESENTATION STRUCTURE REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

SLIDE 1 (Title Slide):
  - slide_type: "title"
  - title: Main topic from content
  - subtitle: Brief description from content
  - bullets: [] (empty array)
  - Include compelling opening context

CONTENT SLIDES ({slide_range}):
  - slide_type: "content"
  - Organize content into logical sections
  - Each slide should focus on ONE main topic
  - Use 2-4 bullet points per slide maximum
  - Each bullet: max 12 words, derived directly from content
  - Include speaker notes expanding on bullets (from content only)

FINAL SLIDE:
  - slide_type: "conclusion"
  - title: "Summary" or "Conclusion"
  - Summarize key points from all content
  - Include 2-4 main takeaways from content
  - speaker_notes: Summary of entire presentation

═══════════════════════════════════════════════════════════════════════════════
CONTENT TO STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

Topic: {self.topic}
Target Audience: {self.target_audience}
Tone: {self.tone}

RAW CONTENT:
{self.raw_content}

═══════════════════════════════════════════════════════════════════════════════
REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

1. Output ONLY valid JSON - no markdown, no explanations, no commentary
2. {slide_instruction}
3. Use bullet points (max 12 words each) - from provided content ONLY
4. Maintain "{self.tone}" tone throughout
5. Speaker notes: Expand on content, don't add external information
6. Ensure ALL content is covered comprehensively
7. Professional organization and structure
{visual_requirements}

═══════════════════════════════════════════════════════════════════════════════
JSON OUTPUT STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

{{
  "presentation_title": "Title reflecting main topic from content",
  "overall_tone": "{self.tone}",
  "target_audience": "{self.target_audience}",
  "total_slides": {total_slides_val},
  "presentation_summary": "2-3 sentence overview from content",
  "slides": [
    {{
      "slide_number": 1,
      "slide_type": "title",
      "title": "Main title from content",
      "subtitle": "Subtitle from content",
      "bullets": [],
      "visuals": {{
        "slide_icons": ["icon"],
        "slide_symbols": ["symbol"],
        "slide_image_ideas": ["image description"]
      }},
      "speaker_notes": "Opening statement from content"
    }},
    {{
      "slide_number": 2,
      "slide_type": "content",
      "title": "Content section title",
      "subtitle": "Optional",
{visual_json}
      "speaker_notes": "Detailed explanation from content"
    }},
    {{
      "slide_number": {final_slide_num},
      "slide_type": "conclusion",
      "title": "Conclusion",
      "subtitle": "Key Takeaways",
      "bullets": [
        "Main point 1 from content",
        "Main point 2 from content",
        "Main point 3 from content"
      ],
      "visuals": {{"slide_icons": [], "slide_symbols": [], "slide_image_ideas": []}},
      "speaker_notes": "Summary of all content covered"
    }}
  ]
}}

{visual_examples}

═══════════════════════════════════════════════════════════════════════════════
FINAL CHECKLIST BEFORE OUTPUT
═══════════════════════════════════════════════════════════════════════════════

✓ Is the total_slides set to {total_slides_val}?
✓ Are ALL content points covered across the slides?
✓ Is EVERY bullet point from the provided content only?
✓ Are there no invented examples or external information?
✓ Is the JSON valid and parseable?
✓ Is the presentation professionally structured?
✓ Are speaker notes comprehensive and from content only?

NOW GENERATE THE JSON (JSON ONLY, NO EXPLANATION):"""
