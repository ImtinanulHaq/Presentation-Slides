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
    Includes special handling for Urdu text and Unicode characters
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Remove any leading/trailing whitespace
    json_str = json_str.strip()
    
    # Remove markdown code blocks if present (```json ... ```)
    if json_str.startswith('```'):
        json_str = re.sub(r'^```.*?\n', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'\n```$', '', json_str, flags=re.MULTILINE)
        json_str = json_str.strip()
    
    # Remove BOM if present (byte order mark)
    if json_str.startswith('\ufeff'):
        json_str = json_str[1:]
    
    # Fix common escaped quote issues while preserving Urdu text
    # Only fix double-escaped quotes (\\" -> "), not single escapes
    json_str = re.sub(r'\\\\"', '"', json_str)
    
    # Fix single quotes to double quotes for JSON compliance
    # First, handle property names: 'key': -> "key":
    json_str = re.sub(r"'([^']*)'(\s*):", r'"\1"\2:', json_str)
    # Handle string values: : 'value', -> : "value",
    json_str = re.sub(r":\s*'([^']*)'(\s*[,\}])", r': "\1"\2', json_str)
    
    # Fix trailing commas before closing brackets/braces (very common issue)
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix missing commas between JSON objects/arrays (major cause of invalid JSON)
    json_str = re.sub(r'(\})\s*(\{)', r'\1,\2', json_str)    # }{ -> },{
    json_str = re.sub(r'(\})\s*(\[)', r'\1,\2', json_str)    # }[ -> },[
    json_str = re.sub(r'(\])\s*(\{)', r'\1,\2', json_str)    # ]{ -> },{
    json_str = re.sub(r'(\])\s*(\[)', r'\1,\2', json_str)    # ][ -> ],[
    
    # Fix missing commas after string values
    json_str = re.sub(r'("\s*)(\{)', r'\1,\2', json_str)     # "{ -> ",{
    json_str = re.sub(r'("\s*)(\[)', r'\1,\2', json_str)     # "[ -> ",[
    
    # Fix escaped newlines within strings - handle both \n and actual newlines
    # Preserve actual newlines in strings by escaping them
    parts = []
    in_string = False
    i = 0
    while i < len(json_str):
        char = json_str[i]
        if char == '\\' and i + 1 < len(json_str):
            # Handle escape sequences
            parts.append(char)
            parts.append(json_str[i + 1])
            i += 2
            continue
        if char == '"' and (i == 0 or json_str[i-1] != '\\'):
            in_string = not in_string
            parts.append(char)
        elif char == '\n' and in_string:
            # Replace literal newline with escaped version
            parts.append('\\n')
        else:
            parts.append(char)
        i += 1
    json_str = ''.join(parts)
    
    # Try to complete incomplete JSON structures
    open_braces = json_str.count('{') - json_str.count('}')
    open_brackets = json_str.count('[') - json_str.count(']')
    
    if open_braces > 0:
        json_str += '}' * open_braces
        logger.debug(f"[JSON REPAIR] Added {open_braces} closing braces")
    
    if open_brackets > 0:
        json_str += ']' * open_brackets
        logger.debug(f"[JSON REPAIR] Added {open_brackets} closing brackets")
    
    return json_str


def generate_fallback_slides(text: str, topic: str, num_slides: int = 5) -> dict:
    """
    Generate basic slide structure from raw text when JSON parsing fails
    Extracts key sentences/paragraphs and creates valid JSON slide structure
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.warning(f"[FALLBACK] Generating slides from raw text")
    
    # Split text into sentences/paragraphs
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if not sentences:
        sentences = [s.strip() for s in text.split('\n') if s.strip()]
    
    slides = []
    
    # Create title slide
    slides.append({
        'slide_number': 1,
        'title': topic,
        'subtitle': 'Presentation Generated',
        'content': 'Content prepared from text analysis',
        'bullets': ['Key information compiled'],
        'visual_description': 'Title slide with topic'
    })
    
    # Distribute sentences across remaining slides
    if num_slides > 1:
        sentences_per_slide = max(1, len(sentences) // (num_slides - 1))
        slide_num = 2
        
        for i in range(0, len(sentences), sentences_per_slide):
            if slide_num > num_slides:
                break
            
            chunk = sentences[i:i+sentences_per_slide]
            slide_bullets = [s[:100] + ('...' if len(s) > 100 else '') for s in chunk]
            
            slides.append({
                'slide_number': slide_num,
                'title': f'Key Point {slide_num - 1}',
                'subtitle': '',
                'content': ' '.join(chunk)[:500],
                'bullets': slide_bullets[:4],  # Limit to 4 bullets
                'visual_description': f'Content slide {slide_num - 1}'
            })
            slide_num += 1
    
    logger.info(f"[FALLBACK] Created {len(slides)} slides from fallback mechanism")
    
    return {
        'presentation': {
            'title': topic,
            'num_slides': len(slides)
        },
        'slides': slides
    }


class GroqPresentationGenerator:
    """Generate presentation structure using Groq API"""
    
    # Font selection mapping based on subject and professionalism
    SUBJECT_FONT_CONFIGS = {
        # General - Balanced modern look
        'general': {
            'title': 'Calibri',
            'heading': 'Calibri',
            'content': 'Arial'
        },
        
        # English - Literary, elegant serif fonts
        'english': {
            'title': 'Georgia',
            'heading': 'Garamond',
            'content': 'Times New Roman'
        },
        
        # Urdu - Specialized Nastaliq font with professional presentation
        'urdu': {
            'title': 'Noto Nastaliq Urdu',  # Beautiful traditional Urdu script
            'heading': 'Segoe UI',  # Good Unicode support for Urdu
            'content': 'Noto Nastaliq Urdu'  # Consistent Urdu typography
        },
        
        # Science - Professional clean look
        'science': {
            'title': 'Cambria',
            'heading': 'Calibri',
            'content': 'Arial'
        },
        
        # Biology - Professional academic style
        'biology': {
            'title': 'Cambria',
            'heading': 'Calibri',
            'content': 'Garamond'
        },
        
        # Physics - Modern technical look
        'physics': {
            'title': 'Calibri',
            'heading': 'Segoe UI',
            'content': 'Consolas'  # Monospace for equations
        },
        
        # Medical - Professional clinical appearance
        'medical': {
            'title': 'Georgia',
            'heading': 'Cambria',
            'content': 'Arial'
        },
        
        # IT - Technical, modern monospace-friendly
        'it': {
            'title': 'Segoe UI',
            'heading': 'Calibri',
            'content': 'Courier New'
        },
        
        # Engineering - Technical precision
        'engineering': {
            'title': 'Calibri',
            'heading': 'Trebuchet MS',
            'content': 'Arial'
        },
    }
    
    def __init__(self, topic: str, raw_content: str, target_audience: str, tone: str, subject: str = 'general', num_slides: int = None, enable_chunking: bool = False, enable_visuals: bool = True, bullet_style: str = 'numbered'):
        self.topic = topic
        self.raw_content = raw_content
        self.target_audience = target_audience
        self.tone = tone
        self.subject = subject if subject in self.SUBJECT_FONT_CONFIGS else 'general'  # Validate subject
        self.bullet_style = bullet_style  # Store bullet style for LLM prompt
        self.num_slides = num_slides  # User-specified slide count (optional)
        
        # Get font configuration based on subject
        self.font_config = self.SUBJECT_FONT_CONFIGS.get(self.subject, self.SUBJECT_FONT_CONFIGS['general'])
        
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
        
        # Initialize Groq client with only supported parameters
        # Groq v0.10.0 accepts: api_key, base_url, timeout, max_retries, default_headers, default_query, http_client
        try:
            # Create client with minimal parameters to avoid compatibility issues
            self.client = Groq(
                api_key=api_key
            )
        except TypeError as type_error:
            # Handle parameter compatibility issues professionally
            import logging
            logger = logging.getLogger(__name__)
            error_message = str(type_error)
            
            if 'unexpected keyword argument' in error_message:
                logger.error(f"[GROQ CLIENT] Initialization error: {error_message}")
                logger.error("[GROQ CLIENT] Attempting clean initialization with api_key only...")
                # Fallback: Create client with absolute minimum parameters
                try:
                    self.client = Groq(api_key=api_key)
                except Exception as fallback_error:
                    logger.critical(f"[GROQ CLIENT] Failed to initialize: {fallback_error}")
                    raise RuntimeError(f"Cannot initialize Groq client: {fallback_error}")
            else:
                # Re-raise if it's a different type of error
                raise

        
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
            result = self._generate_chunked()
        else:
            result = self._generate_single()
        
        # SAFETY CHECK: Ensure result is always a dict
        if isinstance(result, list):
            # If we got a list of slides, wrap it in proper structure
            result = {
                'presentation_title': self.topic,
                'topic': self.topic,
                'target_audience': self.target_audience,
                'tone': self.tone,
                'subject': self.subject,
                'total_slides': len(result),
                'slides': result,
                'metadata': {
                    'generated_with_chunking': self.enable_chunking,
                    'number_of_chunks': 1
                }
            }
        
        return result
    
    def _generate_single(self) -> dict:
        """Generate presentation from single content (standard flow)"""
        import logging
        logger = logging.getLogger(__name__)
        
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
            
            # Log response for debugging (first 500 chars)
            logger.debug(f"[GROQ RESPONSE] Subject: {self.subject}, Length: {len(response_text)}, Preview: {response_text[:500]}")
            
            # Parse JSON from response - look for array or object
            json_start = response_text.find('[')
            if json_start == -1:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
            else:
                json_end = response_text.rfind(']') + 1
            
            # If JSON not found in response, try fallback immediately
            if json_start == -1 or json_end <= json_start:
                logger.warning(f"[JSON NOT FOUND] Groq returned non-JSON format, using fallback mechanism")
                try:
                    # Use fallback to extract slides from markdown/text response
                    num_slides = self.num_slides or 5
                    fallback_result = generate_fallback_slides(
                        response_text, 
                        self.topic, 
                        num_slides
                    )
                    logger.info(f"[FALLBACK SUCCESS] Generated {len(fallback_result['slides'])} slides from markdown response")
                    return fallback_result
                except Exception as fallback_error:
                    logger.error(f"[FALLBACK FAILED] Could not convert response to slides: {str(fallback_error)[:100]}")
                    raise ValueError(f"No valid JSON found and fallback conversion failed: {str(fallback_error)[:100]}")
            
            json_str = response_text[json_start:json_end]
            
            # Try to repair common JSON issues
            try:
                json_str_repaired = repair_json_string(json_str)
                presentation_json = json.loads(json_str_repaired)
                logger.info(f"[JSON SUCCESS] Repaired and parsed successfully")
                
                # ENFORCE 4-6 BULLET POINT REQUIREMENT
                if 'slides' in presentation_json:
                    for slide in presentation_json['slides']:
                        self._extract_slide_bullets(slide)
                
                return presentation_json
            except json.JSONDecodeError as repair_error:
                # If repair didn't work, try original JSON
                logger.warning(f"[JSON REPAIR FAILED] Trying original: {str(repair_error)[:100]}")
                try:
                    presentation_json = json.loads(json_str)
                    logger.info(f"[JSON ORIGINAL SUCCESS] Original JSON parsed")
                    return presentation_json
                except json.JSONDecodeError as original_error:
                    # Log full response for debugging
                    logger.error(f"[JSON PARSE FAILED] Full response:\n{response_text[:500]}")
                    
                    # Try fallback: extract slides from response text
                    logger.warning(f"[FALLBACK] Attempting to generate slides from raw response text")
                    try:
                        # Use fallback slide generation
                        num_slides = self.num_slides or 5
                        fallback_result = generate_fallback_slides(
                            response_text, 
                            self.topic, 
                            num_slides
                        )
                        logger.info(f"[FALLBACK SUCCESS] Generated {len(fallback_result['slides'])} slides using fallback mechanism")
                        return fallback_result
                    except Exception as fallback_error:
                        # If fallback also fails, raise detailed error
                        error_msg = f"JSON parsing failed. "
                        error_msg += f"Subject: {self.subject}. "
                        error_msg += f"Repair error: {str(repair_error)[:80]}. "
                        error_msg += f"Original error: {str(original_error)[:80]}. "
                        error_msg += f"Fallback error: {str(fallback_error)[:80]}. "
                        error_msg += f"JSON preview: {json_str[:100]}..."
                        raise ValueError(error_msg)
                    
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a token limit error from Groq
            if "rate_limit_exceeded" in error_str or "tokens per minute" in error_str or "Request too large" in error_str:
                # Token limit exceeded - suggest retry with chunking
                suggestion = "Content is too large for single request. Retrying with automatic chunking..."
                logger.warning(f"[TOKEN LIMIT ERROR] {suggestion}")
                # Auto-enable chunking and retry
                if not self.enable_chunking:
                    self.enable_chunking = True
                    logger.info("[AUTO-RETRY] Retrying with chunking enabled...")

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
                
                # ENFORCE 4-6 BULLET POINT REQUIREMENT FOR EACH SLIDE
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
    
    def _get_bullet_style_instruction(self) -> str:
        """Get instruction for LLM based on bullet_style"""
        style = str(self.bullet_style).strip().lower() if self.bullet_style else 'numbered'
        
        instructions = {
            'numbered': 'Start each bullet with numbers: "1. ", "2. ", "3. ", "4. "',
            'bullet_elegant': 'Start each bullet with elegant symbol: "● ", "● ", "● ", "● "',
            'bullet_modern': 'Start each bullet with modern symbol: "▸ ", "▸ ", "▸ ", "▸ "',
            'bullet_professional': 'Start each bullet with professional symbol: "■ ", "■ ", "■ ", "■ "'
        }
        
        return instructions.get(style, instructions['numbered'])
    
    def _get_bullet_example(self) -> str:
        """Get example bullets based on bullet_style"""
        style = str(self.bullet_style).strip().lower() if self.bullet_style else 'numbered'
        
        examples = {
            'numbered': '"1. First point here", "2. Second point here", "3. Third point here"',
            'bullet_elegant': '"● First point here", "● Second point here", "● Third point here"',
            'bullet_modern': '"▸ First point here", "▸ Second point here", "▸ Third point here"',
            'bullet_professional': '"■ First point here", "■ Second point here", "■ Third point here"'
        }
        
        return examples.get(style, examples['numbered'])
    
    def _get_bullet_format_description(self) -> str:
        """Get description of bullet format for instructions"""
        style = str(self.bullet_style).strip().lower() if self.bullet_style else 'numbered'
        
        descriptions = {
            'numbered': 'numbers (1., 2., 3., 4.)',
            'bullet_elegant': 'elegant bullets (●)',
            'bullet_modern': 'modern bullets (▸)',
            'bullet_professional': 'professional bullets (■)'
        }
        
        return descriptions.get(style, descriptions['numbered'])
    
    def _get_subject_guidelines(self) -> str:
        """Return subject-specific guidelines for slide generation"""
        
        guidelines = {
            'general': """• Focus on key takeaways and main ideas
• Use accessible language for general audience
• Balance theory with practical examples""",
            
            'english': """• Emphasize literary analysis and critical thinking
• Include relevant quotes and textual references
• Focus on themes, motifs, and character development
• Use sophisticated vocabulary and rhetorical devices""",
            
            'urdu': """🇵🇰 URDU LANGUAGE PRESENTATION GUIDELINES:
• تمام عنوانات اور نکات اردو میں ہوں (All titles and points in Urdu)
• اردو لسانی اصول کے مطابق تحریر کریں (Write according to Urdu linguistic rules)
• نستعلیق یا نسخ رسم الخط کو سہل بنائیں (Maintain readable Urdu script)
• ثقافتی اور تاریخی تناظر شامل کریں (Include cultural and historical context)
• اردو ضرب الاثل اور محاورات استعمال کریں (Use Urdu idioms and expressions)
• عام اردو سے رسمی/فارسی اردو میں لکھیں (Write in formal/literary Urdu)
• ہر نکتے کو 8-15 الفاظ میں محدود رکھیں (Keep each point to 8-15 Urdu words)
• جدید اردو تلفظ اور لکھائی اپنائیں (Use modern Urdu pronunciation and writing)
• مقامی حوالہ جات اور مثالیں شامل کریں (Include local references and examples)
• اردو شاعری یا حکمتیں استعمال کریں جہاں موزوں ہو (Use poetry or wisdom where appropriate)""",
            
            'science': """• Include scientific data, statistics, and evidence
• Explain concepts with proper scientific terminology
• Reference peer-reviewed research where applicable
• Use diagrams or visual representations in descriptions
• Include mathematical formulas if relevant (formatted clearly)""",
            
            'biology': """• Focus on biological processes and lifecycles
• Include anatomical details and functional relationships
• Explain mechanisms at molecular, cellular, and organism levels
• Use proper taxonomic classifications
• Highlight evolutionary perspectives""",
            
            'physics': """• Include mathematical formulas and physical equations (formatted properly)
• Define all physical quantities and units clearly
• Explain underlying principles and laws
• Show relationships between variables
• Include experimental evidence and measurements""",
            
            'medical': """• Use correct medical terminology and Latin names
• Focus on clinical significance and patient outcomes
• Include evidence-based treatment approaches
• Explain pathophysiology clearly
• Highlight safety considerations and best practices""",
            
            'it': """• Use technical terminology accurately
• Include code snippets, algorithms, or architecture diagrams (in text)
• Explain system design and technical workflows
• Focus on scalability, security, and performance
• Include best practices and industry standards""",
            
            'engineering': """• Include technical specifications and measurements
• Explain design principles and structural relationships
• Focus on materials, forces, and efficiency
• Include calculations and technical ratios
• Highlight safety margins and quality standards"""
        }
        
        return guidelines.get(self.subject, guidelines['general'])
    
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
        Validate and ensure slide has 4-6 professional bullet points.
        Generates professional bullets if missing or insufficient.
        
        Professional requirements:
        - Each content slide must have 4-6 bullet points (mandatory)
        - Title slides can have 0 bullets (by design)
        - Each point: 8-15 words, specific and actionable
        - No empty or trivial points
        - Professional tone and terminology
        - Font configuration based on subject
        
        Returns: Validated slide with professional bullets and fonts
        """
        slide_type = slide.get('type', slide.get('slide_type', 'standard')).lower()
        bullets = slide.get('bullets', [])
        
        # Title slides are allowed to have 0 bullets
        if slide_type in ['title', 'intro']:
            # Add font config for title slides
            slide['fonts'] = {
                'title_font': self.font_config['title'],
                'subtitle_font': self.font_config['heading'],
                'content_font': self.font_config['content']
            }
            return slide
        
        # Ensure bullets is a list
        if not isinstance(bullets, list):
            bullets = []
        
        # Filter out empty bullets and clean up
        bullets = [
            str(b).strip() 
            for b in bullets 
            if b and str(b).strip() and str(b).strip() not in ['None', 'null', '']
        ]
        
        current_count = len(bullets)
        
        # Generate professional bullets if missing or insufficient
        if current_count < 4:
            content = slide.get('content', slide.get('subtitle', ''))
            title = slide.get('title', 'Topic')
            
            # Generate professional bullets from content/title
            generated_bullets = self._generate_professional_bullets(
                title=title,
                content=content,
                subject=self.subject,
                needed_count=4 - current_count
            )
            
            bullets.extend(generated_bullets)
        
        # Trim to max 6 bullets per slide
        if len(bullets) > 6:
            bullets = bullets[:6]
        
        slide['bullets'] = bullets
        slide['bullet_count'] = len(bullets)
        
        # Add professional font configuration
        slide['fonts'] = {
            'title_font': self.font_config['title'],
            'heading_font': self.font_config['heading'],
            'content_font': self.font_config['content']
        }
        
        return slide
    
    def _generate_professional_bullets(self, title: str, content: str, subject: str, needed_count: int = 4) -> list:
        """
        Generate professional bullet points from slide title and content.
        
        Args:
            title: Slide title
            content: Slide content/description
            subject: Subject area for context
            needed_count: Number of bullets to generate
        
        Returns: List of professional bullet strings
        """
        bullets = []
        
        # Extract key phrases from content
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        # Priority 1: Key phrase from title
        if title and len(title) > 5:
            bullets.append(f"Key focus: {title.strip()}")
        
        # Priority 2: First/main content points
        if sentences:
            for i, sentence in enumerate(sentences[:needed_count-1]):
                if len(sentence) > 10:
                    # Clean and truncate to 15 words max
                    words = sentence.split()[:15]
                    bullet_text = ' '.join(words)
                    if len(bullet_text) > 8:
                        bullets.append(bullet_text)
        
        # Priority 3: Subject-specific professional bullets
        subject_bullets = self._get_subject_bullets(subject)
        while len(bullets) < needed_count and subject_bullets:
            bullets.append(subject_bullets.pop(0))
        
        # Priority 4: Generic professional bullets if still needed
        generic_bullets = [
            "Relevant application to real-world scenarios",
            "Professional implementation considerations",
            "Performance and efficiency metrics",
            "Quality assurance and validation",
            "Risk management and mitigation strategies",
            "Stakeholder communication and reporting"
        ]
        
        while len(bullets) < needed_count and generic_bullets:
            bullets.append(generic_bullets.pop(0))
        
        # Return exactly the needed count
        return bullets[:needed_count]
    
    def _get_subject_bullets(self, subject: str) -> list:
        """Get professional subject-specific bullet templates"""
        subject_bullets_map = {
            'urdu': [
                'اہم نکات اور تفصیلات',
                'عملی استعمال اور مثالیں',
                'مختلف نقطہ نظر اور تجزیہ',
                'حقائق اور شواہد'
            ],
            'english': [
                'Core concepts and details',
                'Practical applications',
                'Comparative analysis',
                'Evidence and examples'
            ],
            'science': [
                'Scientific principles involved',
                'Experimental methodology',
                'Quantifiable results and metrics',
                'Practical applications'
            ],
            'biology': [
                'Biological mechanisms',
                'Cellular processes',
                'Organismal responses',
                'Evolutionary significance'
            ],
            'physics': [
                'Physical principles at work',
                'Mathematical relationships',
                'Real-world applications',
                'Energy and force considerations'
            ],
            'medical': [
                'Clinical significance',
                'Diagnostic indicators',
                'Treatment approaches',
                'Patient outcomes'
            ],
            'it': [
                'Technical architecture',
                'System components',
                'Performance optimization',
                'Security considerations'
            ],
            'engineering': [
                'Engineering principles',
                'Design specifications',
                'Material considerations',
                'Performance standards'
            ]
        }
        
        return subject_bullets_map.get(subject.lower(), [])
        
    
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
            List of slide dictionaries with 4-6 bullets
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
                
                # Ensure we have 4-6 bullets
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
• Maximum: 6 bullet points per slide
• EVERY slide MUST have 4-6 points
• Target: {slides_per_chunk} slides ({slides_recommended} recommended)
• No exceptions - professional standard is 4-6 points
• FORMAT: Use numbered bullets (1. 2. 3. 4.) or professional icons (▸ ▪ ◆ ■)

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
• 6 bullets: ▪ ▸ ◆ ■ ★ ●  (comprehensive - maximum)

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
3. Each slide MUST have exactly 4-6 bullet points (mandatory)
4. All bullets must be from the chunk content (no external info)
5. Maintain "{self.tone}" tone throughout all content
6. Professional, corporate-quality presentation
7. BULLET FORMAT: Each bullet MUST include number or icon prefix
   Example: "1. First point" or "▸ First point" NOT just "First point"

================================================================================
RESPONSE FORMAT (VALID JSON ARRAY ONLY)
================================================================================
Return a JSON array with 4-8 bullet points per slide. Example structure:
- Each slide has a "title" field
- Each slide has a "type" field set to "standard"
- Each slide has a "bullets" field containing 4-8 text items
- Do NOT include any text outside the JSON array

IMPORTANT: Return ONLY a valid JSON array. Do NOT include any other text.

CRITICAL: Every slide must have 4-6 bullets. No slide should have fewer than 4
or more than 6 points. Content preservation is essential.
"""
    
    def _build_prompt(self) -> str:
        """Build comprehensive prompt for slide generation using Groq API"""
        
        # Determine slide count
        if self.num_slides:
            # User specified exact slide count - MUST respect this
            num_slides = self.num_slides
            slide_instruction = f"EXACT number of slides required: {num_slides} slides (NOT more, NOT less)"
        else:
            # Calculate recommended slides
            slide_calc = self._calculate_optimal_slides(self.content_word_count)
            num_slides = slide_calc['recommended']
            slide_instruction = f"Target slides: {num_slides} slides (recommended based on content length)"
        
        # Build subject-specific guidelines
        subject_guidelines = self._get_subject_guidelines()
        
        # Language instruction - ONLY add Urdu if subject is 'urdu', otherwise enforce English
        language_instruction = ""
        if self.subject == 'urdu':
            language_instruction = """
LANGUAGE REQUIREMENT - URDU ONLY:
✓ Generate ALL slide content ENTIRELY in Urdu language
✓ Use formal/literary Urdu (اردو فارسی کے ساتھ)
✓ Apply correct Urdu grammar rules and syntax
✓ Use Urdu script consistently (نستعلیق یا نسخ)
✓ Translate/adapt English technical terms professionally into Urdu
✓ Each bullet point MUST be in Urdu (8-15 اردو الفاظ کی حد تک)
✓ Titles in Urdu with proper Urdu capitalization
✓ Include culturally relevant examples and metaphors
✓ Use professional Urdu terminology for the subject matter
✓ Maintain proper diacritics (اعراب) where helpful for clarity
✓ JSON keys remain in English, but all text content in Urdu
"""
        else:
            # For ALL other subjects (general, english, science, etc.) - ENFORCE ENGLISH
            language_instruction = """
LANGUAGE REQUIREMENT - ENGLISH ONLY:
✓ Generate ALL slide content ENTIRELY in professional English
✓ Use clear, accessible English language
✓ Write in formal, professional tone
✓ Use proper English grammar and spelling
✓ Create humanized, engaging content
✓ Each bullet point in English (8-15 words maximum)
✓ NO Urdu, NO mixed language, NO translations
✓ Titles in English with proper English capitalization
✓ Include relevant examples and practical applications
✓ Use professional terminology appropriate for {self.subject.upper()} subject
✓ Make content engaging and easy to understand
"""
        
        return f"""You are an expert professional presentation designer. Create comprehensive, high-quality slides.

PRESENTATION DETAILS:
Topic: {self.topic}
Subject: {self.subject.upper()}
Audience: {self.target_audience}
Tone: {self.tone}
Content Length: {self.content_word_count} words
Bullet Style: {self.bullet_style}
{slide_instruction}

SUBJECT-SPECIFIC GUIDELINES:
{subject_guidelines}

{language_instruction}

CRITICAL JSON FORMAT REQUIREMENT:
⚠️ RESPOND WITH ONLY A JSON ARRAY - NO MARKDOWN, NO TEXT BEFORE/AFTER
⚠️ START WITH [ IMMEDIATELY
⚠️ END WITH ] IMMEDIATELY
⚠️ NO explanations, NO markdown formatting, ONLY VALID JSON

EXACT RESPONSE FORMAT (REQUIRED):
[
  {{"slide_number": 1, "title": "Title", "subtitle": "", "content": "Description", "bullets": ["Point 1", "Point 2", "Point 3", "Point 4"], "slide_type": "title"}},
  {{"slide_number": 2, "title": "Title 2", "subtitle": "", "content": "Description 2", "bullets": ["Point 1", "Point 2", "Point 3", "Point 4"], "slide_type": "content"}}
]

MANDATORY SLIDE REQUIREMENTS:
✓ EXACTLY {num_slides} slides in the array (NOT more, NOT less)
✓ EVERY slide has 4-8 bullet points EXACTLY
✓ BULLET STYLE: {self._get_bullet_style_instruction()}
✓ Example bullets: {self._get_bullet_example()}
✓ Each bullet: 8-15 words maximum (not counting number/icon prefix)
✓ slide_number: 1, 2, 3... in sequence
✓ title: Main heading for the slide
✓ subtitle: Secondary title (can be empty string)
✓ content: Brief summary of slide (2-3 sentences)
✓ bullets: Array of 4-8 string bullet points WITH {self._get_bullet_format_description()}
✓ slide_type: "title" for first, "content" for others
✓ No markdown in any field
✓ No asterisks, no formatting, plain text only

PROFESSIONAL CONTENT REQUIREMENTS:
✓ Use ONLY content from the provided text
✓ Maintain logical flow from slide to slide
✓ 4-6 bullet points per slide (NOT less, NOT more)
✓ Bullet numbering/icons: "1. 2. 3. 4." or "▸ ▪ ◆ ■" format
✓ Professional language and correct terminology
✓ NO repetition between slides
✓ NO placeholder text like "Lorem ipsum"
✓ Humanized and engaging presentation style

CONTENT TO CONVERT:
{self.raw_content}

RESPOND NOW WITH ONLY THE JSON ARRAY - NOTHING ELSE."""
