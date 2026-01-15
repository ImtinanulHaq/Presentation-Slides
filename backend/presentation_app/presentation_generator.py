"""
Groq-Based Presentation Generator
Converts raw content to structured JSON using Groq LLM API
Automatically chunks content >= 300 words for intelligent processing
Stores chunk-wise JSON and compiles into unified PPTX-compatible format
"""

import json
from groq import Groq
import os
import re
from .content_chunker import ContentChunker, create_chunked_prompt
from .chunk_json_compiler import ChunkJSONCompiler


# Professional symbols and icons library
PROFESSIONAL_SYMBOLS = {
    'bullets': {
        1: ['●'],
        2: ['▸', '►'],
        3: ['▪', '▸', '◆'],
        4: ['■', '▸', '◆', '★']
    },
    'icons': {
        'success': '✓',
        'point': '▸',
        'arrow': '→',
        'checkmark': '✔',
        'star': '★',
        'bullet': '●',
        'square': '■',
        'diamond': '◆',
        'triangle': '▲',
        'circle': '●',
    }
}


def repair_json_string(json_str: str) -> str:
    """
    Attempt to repair common JSON formatting issues
    Handles incomplete structures, missing commas, trailing commas, etc.
    """
    # Remove any leading/trailing whitespace
    json_str = json_str.strip()
    
    # Fix trailing commas before closing brackets/braces
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix escaped newlines within strings
    json_str = json_str.replace('\\"', '"')
    
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
        
        # AUTO-ENABLE CHUNKING: Check both content length criteria
        # 1. Auto-chunk if content >= 300 words (intelligent processing threshold)
        # 2. Auto-chunk if content > 3500 words (token limit safety)
        content_word_count = len(raw_content.split())
        chunker = ContentChunker()
        
        # AUTO-ENABLE at 300+ words OR if exceeds token safety limit
        if (chunker.should_auto_chunk(raw_content) and not num_slides) and not enable_chunking:
            print(f"[AUTO-CHUNKING] Content has {content_word_count} words (>= {ContentChunker.AUTO_CHUNK_THRESHOLD} word threshold). Auto-enabling intelligent chunking.")
            enable_chunking = True
        elif content_word_count > 3500 and not enable_chunking:
            print(f"[AUTO-CHUNKING] Content has {content_word_count} words (>3500 token limit). Auto-enabling chunking.")
            enable_chunking = True
        
        self.enable_chunking = enable_chunking  # Enable content chunking for large inputs
        self.enable_visuals = enable_visuals  # Enable visual suggestions for bullets
        self.content_word_count = content_word_count  # Store for reference
        
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
            
            # Parse JSON from response - look for array or object
            json_start = response_text.find('[')
            if json_start == -1:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
            else:
                json_end = response_text.rfind(']') + 1
            
            if json_start == -1 or json_end <= json_start:
                raise ValueError("No valid JSON found in Groq response")
            
            json_str = response_text[json_start:json_end]
            
            # Try to repair common JSON issues
            try:
                json_str_repaired = repair_json_string(json_str)
                presentation_json = json.loads(json_str_repaired)
                
                # ENFORCE 4-8 BULLET POINT REQUIREMENT
                if 'slides' in presentation_json:
                    for slide in presentation_json['slides']:
                        self._extract_slide_bullets(slide)
                
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
        """Generate presentation from chunked content for large inputs
        
        Automatically:
        1. Chunks content intelligently (preserves context)
        2. Generates slides per chunk
        3. Stores chunk-wise JSON
        4. Compiles into unified, PPTX-compatible format
        """
        
        chunker = ContentChunker()
        chunks = chunker.chunk_content(self.raw_content)
        
        if len(chunks) == 1:
            # Content fits in single chunk, use normal flow
            return self._generate_single()
        
        print(f"[CHUNKING] Processing {len(chunks)} chunks for comprehensive presentation generation")
        
        # Initialize compiler for unified output
        compiler = ChunkJSONCompiler(
            topic=self.topic,
            target_audience=self.target_audience,
            tone=self.tone
        )
        
        # Collect all chunk slides
        all_chunk_slides = []
        
        try:
            # Process each chunk independently
            for chunk_idx, chunk in enumerate(chunks, 1):
                print(f"[CHUNK {chunk_idx}/{len(chunks)}] Processing chunk ({len(chunk.split())} words)...")
                
                chunk_prompt = self._build_chunk_prompt(chunk, chunk_idx, len(chunks))
                
                chunk_slides = []
                retry_count = 0
                max_retries = 2
                
                # Retry logic for failed chunks
                while not chunk_slides and retry_count <= max_retries:
                    try:
                        # Generate slides for this chunk
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
                            
                            try:
                                chunk_slides = json.loads(json_str)
                            except json.JSONDecodeError as e:
                                # Try to repair JSON
                                try:
                                    json_str = repair_json_string(json_str)
                                    chunk_slides = json.loads(json_str)
                                except json.JSONDecodeError:
                                    if retry_count < max_retries:
                                        retry_count += 1
                                        print(f"[CHUNK {chunk_idx}/{len(chunks)}] ⚠ JSON parse failed (attempt {retry_count}), retrying...")
                                        continue
                                    else:
                                        print(f"[CHUNK {chunk_idx}/{len(chunks)}] ⚠ JSON repair failed after {max_retries} retries, using fallback")
                                        chunk_slides = self._generate_fallback_slides(chunk, chunk_idx)
                        else:
                            if retry_count < max_retries:
                                retry_count += 1
                                print(f"[CHUNK {chunk_idx}/{len(chunks)}] ⚠ No JSON found (attempt {retry_count}), retrying...")
                                continue
                            else:
                                print(f"[CHUNK {chunk_idx}/{len(chunks)}] ⚠ No valid JSON found after retries, using fallback")
                                chunk_slides = self._generate_fallback_slides(chunk, chunk_idx)
                        
                        # Successfully parsed JSON, exit retry loop
                        if chunk_slides:
                            break
                    
                    except Exception as e:
                        if retry_count < max_retries:
                            retry_count += 1
                            print(f"[CHUNK {chunk_idx}/{len(chunks)}] ⚠ API error (attempt {retry_count}): {str(e)[:50]}... retrying...")
                            continue
                        else:
                            print(f"[CHUNK {chunk_idx}/{len(chunks)}] ⚠ API failed after retries, using fallback")
                            chunk_slides = self._generate_fallback_slides(chunk, chunk_idx)
                            break
                
                # ENFORCE 4-8 BULLET POINT REQUIREMENT FOR EACH SLIDE
                if isinstance(chunk_slides, list):
                    for slide in chunk_slides:
                        if isinstance(slide, dict):
                            self._extract_slide_bullets(slide)
                            # Clean any chunk-related metadata from slides
                            self._clean_slide_metadata(slide)
                
                # Ensure chunk_slides is a list
                if not isinstance(chunk_slides, list):
                    chunk_slides = chunk_slides.get('slides', []) if isinstance(chunk_slides, dict) else []
                
                # Store chunk-wise JSON
                all_chunk_slides.append(chunk_slides)
                print(f"[CHUNK {chunk_idx}/{len(chunks)}] OK - Generated {len(chunk_slides)} slides")
            
            # Compile all chunks into unified JSON using compiler
            print("[COMPILING] Merging chunk data into unified presentation format...")
            
            presentation_json = compiler.compile_chunk_slides(
                chunk_slides_list=all_chunk_slides,
                chunk_count=len(chunks)
            )
            
            # Validate and clean the compiled JSON
            presentation_json = compiler.validate_compiled_json(presentation_json)
            
            print(f"[SUCCESS] Generated {presentation_json['total_slides']} slides from {len(chunks)} chunks")
            
            return presentation_json
            
        except Exception as e:
            raise Exception(f"Error generating chunked presentation: {str(e)}")
    
    def _calculate_optimal_slides(self, word_count: int) -> dict:
        """
        Calculate optimal slide count based on professional guidelines.
        
        WORD-TO-SLIDE RATIO:
        - 1000+ words: 3 slides per 100 words (30+ slides for 1000+)
        - 500-999 words: 4-5 slides per 100 words (20-50 slides)
        - 300-499 words: 4-5 slides per 100 words (12-25 slides)
        - 100-299 words: 5-8 slides per 100 words (5-24 slides)
        
        Returns: {'min': int, 'max': int, 'recommended': int}
        """
        if word_count >= 1000:
            # 1000+ words: 3 slides per 100 words
            min_slides = max(20, int(word_count / 100 * 3 * 0.85))
            max_slides = max(25, int(word_count / 100 * 3 * 1.15))
            recommended = int(word_count / 100 * 3)
        
        elif word_count >= 500:
            # 500-999 words: 4-5 slides per 100 words
            min_slides = max(15, int(word_count / 100 * 4))
            max_slides = max(20, int(word_count / 100 * 5))
            recommended = int(word_count / 100 * 4.5)
        
        elif word_count >= 300:
            # 300-499 words: 4-5 slides per 100 words
            min_slides = max(12, int(word_count / 100 * 4))
            max_slides = max(15, int(word_count / 100 * 5))
            recommended = int(word_count / 100 * 4.5)
        
        elif word_count >= 100:
            # 100-299 words: 5-8 slides per 100 words
            min_slides = max(5, int(word_count / 100 * 5))
            max_slides = max(8, int(word_count / 100 * 8))
            recommended = int(word_count / 100 * 6.5)
        
        else:
            # < 100 words: minimum viable presentation
            min_slides = 3
            max_slides = 8
            recommended = 5
        
        return {
            'min': max(3, min_slides),
            'max': max(min_slides + 2, max_slides),
            'recommended': max(3, recommended),
            'word_count': word_count
        }
    
    def _extract_slide_bullets(self, slide: dict) -> dict:
        """
        Validate and ensure slide has 4-8 bullet points (except title/conclusion slides).
        
        Professional requirements:
        - Each content slide must have 4-8 bullet points (not less, not more)
        - Title slides can have 0 bullets (by design)
        - Conclusion slides should have 4-8 bullets or get padded
        - Each point should be detailed and informative
        - No points can be empty or trivial
        
        Returns: Validated slide with proper bullet count
        """
        slide_type = slide.get('type', slide.get('slide_type', 'standard')).lower()
        bullets = slide.get('bullets', [])
        
        # Title slides are allowed to have 0 bullets
        if slide_type in ['title', 'intro']:
            return slide
        
        # Ensure bullets is a list
        if not isinstance(bullets, list):
            bullets = []
        
        # Filter out empty bullets
        bullets = [b for b in bullets if b and str(b).strip()]
        
        current_count = len(bullets)
        
        if current_count < 4:
            # Too few bullets - add placeholder guidance
            while len(bullets) < 4:
                bullets.append("Additional point: [Content detail]")
        
        elif current_count > 8:
            # Too many bullets - consolidate or truncate to 8 most important
            bullets = bullets[:8]
        
        slide['bullets'] = bullets
        slide['bullet_count'] = len(bullets)
        
        return slide
        
    
    def _clean_slide_metadata(self, slide: dict) -> None:
        """
        Remove any chunk-related metadata from slide.
        Ensures user only sees content-related information.
        
        Args:
            slide: Slide dictionary to clean
        """
        # Remove chunk-related keys that might appear in slides
        chunk_keys = ['chunk', 'chunk_number', 'chunk_idx', 'chunk_id', 'from_chunk']
        for key in chunk_keys:
            slide.pop(key, None)
        
        # Ensure subtitle and speaker_notes don't contain chunk info
        if 'subtitle' in slide:
            subtitle = str(slide.get('subtitle', '')).strip()
            if 'chunk' in subtitle.lower():
                slide['subtitle'] = ''
        
        if 'speaker_notes' in slide:
            notes = str(slide.get('speaker_notes', '')).strip()
            if 'chunk' in notes.lower():
                slide['speaker_notes'] = ''
    
    def _generate_fallback_slides(self, chunk_text: str, chunk_idx: int) -> list:
        """
        Generate fallback slides when JSON parsing fails
        Extracts key sentences from chunk and creates slides
        
        Args:
            chunk_text: Raw chunk text
            chunk_idx: Chunk index number
            
        Returns:
            List of slide dictionaries with 4-8 bullets
        """
        try:
            sentences = [s.strip() for s in chunk_text.split('.') if len(s.strip()) > 20]
            
            if not sentences:
                # If no sentences, use paragraphs
                sentences = [p.strip() for p in chunk_text.split('\n') if len(p.strip()) > 20]
            
            if not sentences:
                # Last resort: return empty list, compiler will handle it
                print(f"[CHUNK {chunk_idx}] ⚠ Fallback: No extractable content")
                return []
            
            # Group sentences into slides (4-6 bullets per slide)
            slides = []
            bullets_per_slide = 5  # Safe middle ground: 4-8
            
            for i in range(0, len(sentences), bullets_per_slide):
                slide_bullets = sentences[i:i+bullets_per_slide]
                
                # Ensure we have 4-8 bullets
                if len(slide_bullets) < 4 and i + bullets_per_slide < len(sentences):
                    slide_bullets = sentences[i:i+6]
                
                if len(slide_bullets) >= 4:
                    slide = {
                        "slide_type": "content",
                        "title": f"Key Points - Section {i//bullets_per_slide + 1}",
                        "subtitle": "",
                        "bullets": slide_bullets,
                        "speaker_notes": "",
                        "visuals": {"icons": [], "symbols": ["▸"]}
                    }
                    slides.append(slide)
            
            if slides:
                print(f"[CHUNK {chunk_idx}] ✓ Fallback: Generated {len(slides)} slides from text")
            
            return slides
            
        except Exception as e:
            print(f"[CHUNK {chunk_idx}] ⚠ Fallback failed: {str(e)}")
            return []
    
    def _build_chunk_prompt(self, chunk: str, chunk_num: int, total_chunks: int) -> str:
        """Build prompt for processing a single chunk
        
        Dynamically determines slide count and bullet points based on content length.
        Professional implementation with detailed guidelines.
        """
        
        # Calculate optimal slides for this chunk
        chunk_word_count = len(chunk.split())
        slide_calc = self._calculate_optimal_slides(chunk_word_count)
        
        # Determine recommended slide count per chunk
        if total_chunks <= 2:
            slides_per_chunk = f"{max(3, slide_calc['min'])}-{slide_calc['max']}"
            slides_recommended = f"~{slide_calc['recommended']}"
        elif total_chunks <= 3:
            slides_per_chunk = f"{max(2, slide_calc['min']//2)}-{slide_calc['max']//2}"
            slides_recommended = f"~{slide_calc['recommended']//2}"
        elif total_chunks <= 5:
            slides_per_chunk = f"{max(2, slide_calc['min']//3)}-{slide_calc['max']//3}"
            slides_recommended = f"~{slide_calc['recommended']//3}"
        else:
            slides_per_chunk = "2-3"
            slides_recommended = "~3"
        
        return f"""You are a professional presentation slide generator.
Create comprehensive, detailed, corporate-quality slides from this content.

CONTENT TO PROCESS:
{chunk}

================================================================================
SLIDE GENERATION REQUIREMENTS
================================================================================
🎯 BULLET POINTS PER SLIDE:
• Minimum: 4 bullet points per slide
• Maximum: 8 bullet points per slide
• EVERY slide MUST have 4-8 points
• Target: {slides_per_chunk} slides ({slides_recommended} recommended)
• No exceptions - professional standard is 4-8 points

📝 BULLET POINT QUALITY:
1. Each point: 8-15 words (concise but detailed)
2. Start with strong verbs or key concepts
3. Include specific numbers, metrics, or evidence when present in content
4. Reference actual information from the chunk - NO generic filler
5. Maintain consistent structure within a slide
6. Every point must be distinct and non-repetitive
7. Cover all important aspects of the topic

💼 CONTENT COVERAGE:
• Extract and represent ALL significant information from this chunk
• If chunk has 100+ words, spread detail across multiple comprehensive slides
• If chunk has statistics/numbers, include them with context
• If chunk discusses concepts, ensure all are represented
• No important information should be omitted

================================================================================
PROFESSIONAL SYMBOLS & FORMATTING
================================================================================
Use professional symbols instead of basic bullets:
• 4 bullets: ▪ ▸ ◆ ■  (balanced variety)
• 5 bullets: ▪ ▸ ◆ ■ ★  (add emphasis marker)
• 6 bullets: ▪ ▸ ◆ ■ ★ ●  (comprehensive)
• 7 bullets: ▪ ▸ ◆ ■ ★ ● ✓  (checkmark for last)
• 8 bullets: ▪ ▸ ◆ ■ ★ ● ✓ →  (full palette)

================================================================================
EMOJI USAGE (SELECTIVE & PROFESSIONAL)
================================================================================
Use emojis ONLY when contextually appropriate:
✅ When to use:
  • Financial data/metrics: 📊 📈 💰 (when discussing numbers)
  • Technical aspects: 🔧 💻 🔐 (for tech content only)
  • Achievements: ✅ (for milestones/successes only)
  • Strategy/goals: 🎯 (for objectives only)
  • Risk/warning: ⚠️ (for critical warnings only)

❌ Never use:
  • Casual/cute emojis: 😊 😄 👍 🌟
  • Generic decorative emojis
  • Multiple emojis per slide (max 1-2)
  • For regular descriptive text (default to professional symbols)

Default to professional symbols (▸ ▪ ◆ etc.) instead of emojis.

================================================================================
SLIDE STRUCTURE GUIDELINES
================================================================================
✓ Structure each slide around ONE main topic or concept
✓ Organize content logically with progression of ideas
✓ Each slide should build on previous concepts
✓ Use consistent formatting throughout
✓ Ensure visual hierarchy with symbols and structure

================================================================================
OUTPUT REQUIREMENTS
================================================================================
1. Output ONLY valid JSON array of slides - no markdown, explanations, or code
2. Generate {slides_per_chunk} slides total
3. Each slide MUST have exactly 4-8 bullet points (mandatory)
4. All bullets must be from the chunk content (no external info)
5. Maintain "{self.tone}" tone throughout all content
6. Professional, corporate-quality presentation

================================================================================
RESPONSE FORMAT (VALID JSON ARRAY ONLY)
================================================================================
Return a JSON array with 4-8 bullet points per slide. Example structure:
- Each slide has a "title" field
- Each slide has a "type" field set to "standard"
- Each slide has a "bullets" field containing 4-8 text items
- Do NOT include any text outside the JSON array

IMPORTANT: Return ONLY a valid JSON array. Do NOT include any other text.

CRITICAL: Every slide must have 4-8 bullets. No slide should have fewer than 4
or more than 8 points. Content preservation is essential.
"""
    
    def _build_prompt(self) -> str:
        """Build comprehensive prompt for slide generation using Groq API"""
        
        # Calculate optimal slide count
        slide_calc = self._calculate_optimal_slides(self.content_word_count)
        num_slides = slide_calc['recommended']
        
        return f"""You are an expert professional presentation designer. Create comprehensive, high-quality slides.

PRESENTATION GUIDELINES:
Topic: {self.topic}
Audience: {self.target_audience}
Tone: {self.tone}
Word Count: {self.content_word_count} words
Recommended Slides: {num_slides}

PROFESSIONAL WORD-TO-SLIDE RATIOS:
• 1000+ words: 3 slides per 100 words
• 500-999 words: 4-5 slides per 100 words
• 300-499 words: 4-5 slides per 100 words
• 100-299 words: 5-8 slides per 100 words

MANDATORY REQUIREMENTS:
✓ EVERY slide MUST have 4-8 bullet points (NO exceptions)
✓ Each point: 8-15 words max
✓ Include specific numbers, metrics, evidence from content
✓ Content from provided text ONLY
✓ Professional symbols only: ▪ ▸ ◆ ■ ★ ● ✓ →
✓ Emojis ONLY when contextually appropriate (max 1-2 per slide)
✓ ALL information from content must be covered
✓ No typos, no errors, professional quality

CONTENT:
{self.raw_content}

OUTPUT: Valid JSON array with {num_slides} slides, each with 4-8 bullets from content.
"""
