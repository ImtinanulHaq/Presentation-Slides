"""
Script Generator using Groq API
Generates professional speaker scripts for presentation slides
"""

import os
import json
import logging
import time
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class GroqScriptGenerator:
    """Generate professional speaker scripts using Groq API"""

    def __init__(self, api_key=None):
        """Initialize Groq client"""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.client = Groq(api_key=self.api_key)
        # Using latest available Groq model
        self.model = "llama-3.1-8b-instant"
    
    def _call_groq_api(self, prompt, max_tokens, chunk_index=0, total_chunks=0):
        """Call Groq API with retry logic for rate limits"""
        max_retries = 3
        retry_count = 0
        base_wait_time = 2  # Start with 2 seconds
        
        while retry_count < max_retries:
            try:
                message = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                return message.choices[0].message.content
            
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error
                if "429" in error_str or "Too Many Requests" in error_str:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = base_wait_time * (2 ** (retry_count - 1))  # Exponential backoff
                        chunk_info = f" on chunk {chunk_index + 1}/{total_chunks}" if total_chunks > 0 else ""
                        logger.warning(f"Rate limited{chunk_info}. "
                                     f"Retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})...")
                        time.sleep(wait_time)
                    else:
                        chunk_info = f" on chunk {chunk_index + 1}/{total_chunks}" if total_chunks > 0 else ""
                        logger.error(f"Max retries exceeded{chunk_info}")
                        raise
                else:
                    # Not a rate limit error, raise immediately
                    raise
        
        raise Exception("Failed to call Groq API after all retries")
    
    def generate_script_for_slides(self, slides, presentation_tone, total_duration, presentation_title=""):
        """
        Generate speaker scripts for presentation slides with automatic chunking for large presentations
        
        Args:
            slides: List of slide dictionaries with title, content, bullets
            presentation_tone: Tone of presentation (professional, casual, academic, persuasive)
            total_duration: Total duration in minutes for the entire presentation
            presentation_title: Title of the presentation
        
        Returns:
            Dictionary with scripts for each slide including timing and explanations
        """
        try:
            num_slides = len(slides)
            logger.info(f"Generating script for {num_slides} slides with {total_duration} minutes duration")
            
            # Use chunking for presentations with more than 15 slides
            # This prevents timeouts and token limit issues for large presentations
            if num_slides > 15:
                return self._generate_scripts_chunked(
                    slides=slides,
                    presentation_tone=presentation_tone,
                    total_duration=total_duration,
                    presentation_title=presentation_title
                )
            else:
                return self._generate_scripts_single_batch(
                    slides=slides,
                    presentation_tone=presentation_tone,
                    total_duration=total_duration,
                    presentation_title=presentation_title
                )
        
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "scripts": []
            }
    
    def _generate_scripts_single_batch(self, slides, presentation_tone, total_duration, presentation_title):
        """Generate scripts for all slides in a single API call (for small presentations)"""
        num_slides = len(slides)
        duration_per_slide = total_duration / num_slides if num_slides > 0 else 0
        
        # Build slide information for the prompt
        slides_info = self._format_slides_for_prompt(slides)
        
        # Create the prompt for script generation
        prompt = self._create_script_prompt(
            slides_info=slides_info,
            presentation_title=presentation_title,
            presentation_tone=presentation_tone,
            total_duration=total_duration,
            duration_per_slide=duration_per_slide,
            num_slides=num_slides
        )
        
        logger.info(f"Single batch mode: Generating scripts for {num_slides} slides")
        
        # Call Groq API
        # For longer presentations, we need more tokens to generate complete scripts
        # Each slide typically needs 200-300 tokens for natural script generation
        max_tokens = max(6000, min(8000, num_slides * 400))
        
        script_text = self._call_groq_api(prompt, max_tokens)
        scripts = self._parse_script_response(script_text, num_slides)
        
        return {
            "success": True,
            "scripts": scripts,
            "metadata": {
                "total_duration": total_duration,
                "duration_per_slide": round(duration_per_slide, 2),
                "num_slides": num_slides,
                "tone": presentation_tone,
                "presentation_title": presentation_title,
                "processing_mode": "single_batch"
            }
        }
    
    def _generate_scripts_chunked(self, slides, presentation_tone, total_duration, presentation_title):
        """Generate scripts for large presentations by processing slides in chunks"""
        num_slides = len(slides)
        
        # Determine chunk size based on number of slides
        # Larger presentations get smaller chunks per API call for better reliability
        if num_slides > 50:
            chunk_size = 10  # For 50+ slides, use 10 slides per chunk
        elif num_slides > 30:
            chunk_size = 12  # For 30-50 slides, use 12 slides per chunk
        else:
            chunk_size = 15  # For 15-30 slides, use 15 slides per chunk
        
        num_chunks = (num_slides + chunk_size - 1) // chunk_size  # Ceiling division
        duration_per_chunk = total_duration / num_chunks
        duration_per_slide = total_duration / num_slides
        
        logger.info(f"Chunked mode: Processing {num_slides} slides in {num_chunks} chunks of ~{chunk_size} slides each")
        
        all_scripts = []
        failed_chunks = []
        
        for chunk_idx in range(num_chunks):
            start_idx = chunk_idx * chunk_size
            end_idx = min((chunk_idx + 1) * chunk_size, num_slides)
            chunk_slides = slides[start_idx:end_idx]
            chunk_num = chunk_idx + 1
            
            logger.info(f"Processing chunk {chunk_num}/{num_chunks} (slides {start_idx + 1}-{end_idx})")
            
            try:
                # Generate scripts for this chunk
                chunk_result = self._generate_chunk_scripts(
                    chunk_slides=chunk_slides,
                    chunk_index=chunk_idx,
                    total_chunks=num_chunks,
                    presentation_tone=presentation_tone,
                    presentation_title=presentation_title,
                    duration_per_slide=duration_per_slide,
                    duration_per_chunk=duration_per_chunk
                )
                
                if chunk_result['success']:
                    all_scripts.extend(chunk_result['scripts'])
                    logger.info(f"Chunk {chunk_num} completed: {len(chunk_result['scripts'])} scripts generated")
                else:
                    failed_chunks.append(chunk_num)
                    logger.error(f"Chunk {chunk_num} failed: {chunk_result.get('error')}")
                    # Add fallback scripts for failed chunk
                    fallback = self._create_fallback_scripts(len(chunk_slides))
                    all_scripts.extend(fallback)
            
            except Exception as e:
                logger.error(f"Error processing chunk {chunk_num}: {str(e)}", exc_info=True)
                failed_chunks.append(chunk_num)
                # Add fallback scripts for this chunk
                fallback = self._create_fallback_scripts(len(chunk_slides))
                all_scripts.extend(fallback)
        
        return {
            "success": len(failed_chunks) == 0,
            "scripts": all_scripts,
            "metadata": {
                "total_duration": total_duration,
                "duration_per_slide": round(duration_per_slide, 2),
                "num_slides": num_slides,
                "tone": presentation_tone,
                "presentation_title": presentation_title,
                "processing_mode": "chunked",
                "num_chunks": num_chunks,
                "chunk_size": chunk_size,
                "failed_chunks": failed_chunks,
                "partial_success": len(failed_chunks) > 0
            }
        }
    
    def _generate_chunk_scripts(self, chunk_slides, chunk_index, total_chunks, presentation_tone, 
                                presentation_title, duration_per_slide, duration_per_chunk):
        """Generate scripts for a single chunk of slides"""
        num_slides_in_chunk = len(chunk_slides)
        
        # Build slide information for the chunk
        slides_info = self._format_slides_for_prompt(chunk_slides)
        
        # Create prompt for chunk
        prompt = f"""You are an expert presentation speaker. Generate completely NATURAL, HUMAN-LIKE scripts for these presentation slides.

HUMANIZATION RULES:
- Sound like a REAL PERSON speaking naturally, NOT AI-generated
- Use conversational language with natural sentence variations
- Mix short and long sentences naturally
- Include casual phrases: "you know", "actually", "so here's the thing", "look"
- Use contractions: "that's", "you'll", "isn't", "won't"
- Add engagement: rhetorical questions, personal language
- Make transitions feel spontaneous and natural
- Include realistic pauses and pacing

PRESENTATION CONTEXT:
- Title: {presentation_title}
- Tone: {presentation_tone}
- This is chunk {chunk_index + 1} of {total_chunks}
- Duration per slide: {duration_per_slide:.1f} minutes ({int(duration_per_slide * 60)} seconds)
- Total duration for this chunk: {duration_per_chunk:.1f} minutes

SLIDES IN THIS CHUNK:
{slides_info}

IMPORTANT:
1. Generate scripts that sound 100% human and conversational
2. Each script should take approximately {int(duration_per_slide * 60)} seconds to deliver
3. Scripts should flow naturally within the context of the full presentation
4. Maintain consistent tone throughout the chunk

Format each script as JSON:
{{
  "slide_number": <number>,
  "slide_title": "<title>",
  "script": "<natural, conversational script - sounds like a real person talking>",
  "key_points": ["point1", "point2", "point3"],
  "talking_points": "<casual speaker notes>",
  "estimated_duration_seconds": <number>,
  "transition_to_next": "<natural transition to next slide>",
  "slide_explanation": "<what this slide is really about>"
}}

Return ONLY valid JSON array format. Generate completely natural, human-sounding scripts:"""
        
        logger.debug(f"Generating chunk {chunk_index + 1}/{total_chunks} with prompt length {len(prompt)}")
        
        # Call Groq API for this chunk
        # Allocate tokens based on chunk size
        max_tokens = min(8000, max(3000, num_slides_in_chunk * 500))
        
        message = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Parse the response
        script_text = message.choices[0].message.content
        scripts = self._parse_script_response(script_text, num_slides_in_chunk)
        
        return {
            "success": True,
            "scripts": scripts,
            "chunk_index": chunk_index
        }
        
        # Build slide information for the chunk
        slides_info = self._format_slides_for_prompt(chunk_slides)
        
        # Create prompt for chunk
        prompt = f"""You are an expert presentation speaker. Generate completely NATURAL, HUMAN-LIKE scripts for these presentation slides.

HUMANIZATION RULES:
- Sound like a REAL PERSON speaking naturally, NOT AI-generated
- Use conversational language with natural sentence variations
- Mix short and long sentences naturally
- Include casual phrases: "you know", "actually", "so here's the thing", "look"
- Use contractions: "that's", "you'll", "isn't", "won't"
- Add engagement: rhetorical questions, personal language
- Make transitions feel spontaneous and natural
- Include realistic pauses and pacing

PRESENTATION CONTEXT:
- Title: {presentation_title}
- Tone: {presentation_tone}
- This is chunk {chunk_index + 1} of {total_chunks}
- Duration per slide: {duration_per_slide:.1f} minutes ({int(duration_per_slide * 60)} seconds)
- Total duration for this chunk: {duration_per_chunk:.1f} minutes

SLIDES IN THIS CHUNK:
{slides_info}

IMPORTANT:
1. Generate scripts that sound 100% human and conversational
2. Each script should take approximately {int(duration_per_slide * 60)} seconds to deliver
3. Scripts should flow naturally within the context of the full presentation
4. Maintain consistent tone throughout the chunk

Format each script as JSON:
{{
  "slide_number": <number>,
  "slide_title": "<title>",
  "script": "<natural, conversational script - sounds like a real person talking>",
  "key_points": ["point1", "point2", "point3"],
  "talking_points": "<casual speaker notes>",
  "estimated_duration_seconds": <number>,
  "transition_to_next": "<natural transition to next slide>",
  "slide_explanation": "<what this slide is really about>"
}}

Return ONLY valid JSON array format. Generate completely natural, human-sounding scripts:"""
        
        logger.debug(f"Generating chunk {chunk_index + 1}/{total_chunks} with prompt length {len(prompt)}")
        
        # Call Groq API for this chunk
        # Allocate tokens based on chunk size
        max_tokens = min(8000, max(3000, num_slides_in_chunk * 500))
        
        message = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Parse the response
        script_text = message.choices[0].message.content
        scripts = self._parse_script_response(script_text, num_slides_in_chunk)
        
        return {
            "success": True,
            "scripts": scripts,
            "chunk_index": chunk_index
        }
    
    def _call_groq_api(self, prompt, max_tokens, chunk_index=0, total_chunks=0):
        """Call Groq API with retry logic for rate limits"""
        max_retries = 3
        retry_count = 0
        base_wait_time = 2  # Start with 2 seconds
        
        while retry_count < max_retries:
            try:
                message = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                return message.choices[0].message.content
            
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error
                if "429" in error_str or "Too Many Requests" in error_str:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = base_wait_time * (2 ** (retry_count - 1))  # Exponential backoff
                        logger.warning(f"Rate limited on chunk {chunk_index + 1}/{total_chunks}. "
                                     f"Retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Max retries exceeded for chunk {chunk_index + 1}/{total_chunks}")
                        raise
                else:
                    # Not a rate limit error, raise immediately
                    raise
        
        raise Exception("Failed to call Groq API after all retries")
    
    def _format_slides_for_prompt(self, slides):
        """Format slides data for the prompt"""
        formatted = []
        for i, slide in enumerate(slides, 1):
            slide_info = {
                "slide_number": i,
                "title": slide.get("title", f"Slide {i}"),
                "subtitle": slide.get("subtitle", ""),
                "content": slide.get("content", ""),
                "bullets": slide.get("bullets", [])
            }
            formatted.append(slide_info)
        
        return json.dumps(formatted, ensure_ascii=False, indent=2)
    
    def _create_script_prompt(self, slides_info, presentation_title, presentation_tone, 
                             total_duration, duration_per_slide, num_slides):
        """Create the prompt for script generation"""
        
        tone_guidelines = {
            "professional": "formal, clear, authoritative, business-appropriate",
            "casual": "conversational, friendly, easy to follow, relatable",
            "academic": "scholarly, detailed, evidence-based, intellectual",
            "persuasive": "compelling, convincing, engaging, motivating"
        }
        
        tone_description = tone_guidelines.get(presentation_tone, "professional and clear")
        
        prompt = f"""You are an expert presentation speaker and coach. Your task is to write completely NATURAL, HUMAN-LIKE speaker scripts that sound like a real person talking to an audience - NOT like AI-generated content.

IMPORTANT GUIDELINES FOR HUMANIZATION:
- Write as if a real human is speaking conversationally to an audience
- Use natural sentence variations (short AND long sentences, mix them up)
- Include casual connectors: "you know", "actually", "I mean", "look", "so here's the thing"
- Add natural pauses indicated by "..." or short sentences
- Use contractions naturally (you'll, that's, isn't, won't)
- Include rhetorical questions to engage the audience
- Use personal language: "I want to show you", "let me share", "think about this"
- Vary pacing - not every sentence should be the same structure
- Include natural verbal filler patterns like "right?", "doesn't it?", "think about it"
- Make transitions feel spontaneous, not scripted
- Use specific, concrete examples that sound real
- Write imperfectly natural (humans don't speak in perfect paragraphs)

PRESENTATION DETAILS:
- Title: {presentation_title}
- Tone: {presentation_tone} ({tone_description})
- Total Duration: {total_duration} minutes
- Number of Slides: {num_slides}
- Approximate Duration per Slide: {duration_per_slide:.1f} minutes

SLIDES INFORMATION:
{slides_info}

SCRIPT GENERATION REQUIREMENTS:
1. Generate natural, conversational speaker scripts for each slide
2. Scripts should be paragraph-wise with natural speaking pauses
3. Each script should take approximately {duration_per_slide:.1f} minutes to deliver naturally
4. Write exactly as a person would say it - not as formal writing

WHAT TO INCLUDE:
   - Natural, engaging opening that connects with audience
   - Clear explanation of slide content in conversational tone
   - Real-world examples or analogies
   - Key points mentioned naturally (not listed robotically)
   - Smooth, natural transitions to next slide
   - Estimated speaking time accounting for pauses

WRITING STYLE FOR {presentation_tone}:
   - Tone: {tone_description}
   - Sound like a REAL PERSON, not AI
   - Write for spoken delivery with natural rhythm
   - Include sentence variations for interesting pacing
   - Use natural connecting phrases
   - Make it engaging and relatable

CRITICAL: Make the script sound 100% human - like someone who knows their content and is sharing it conversationally with an audience. Remove any AI-like patterns, robotic structures, or overly formal language.

Format each script as JSON:
{{
  "slide_number": <number>,
  "slide_title": "<title>",
  "script": "<natural, conversational script with varied sentence structure - sounds like a real person talking>",
  "key_points": ["point1", "point2", "point3"],
  "talking_points": "<casual speaker notes and tips>",
  "estimated_duration_seconds": <number>,
  "transition_to_next": "<natural transition to next topic>",
  "slide_explanation": "<what this slide is really about>"
}}

EXAMPLE OF NATURAL vs AI-LIKE (AVOID THE SECOND ONE):

GOOD (Natural, Human):
"So here's the thing about artificial intelligence... it's not some distant future technology anymore. I mean, you're probably using it right now without even realizing it. Your phone, Netflix, that creepy ad that knew what you were thinking about – all AI. And honestly? It's pretty fascinating when you think about it. Let me show you why it matters."

BAD (AI-like, robotic):
"Artificial intelligence is a transformative technology that is currently reshaping multiple industries and sectors. The implementation of AI algorithms has become increasingly prevalent in consumer-facing applications."

Generate the complete scripts for all {num_slides} slides. Return ONLY valid JSON array format without any markdown code blocks or extra text. Make them sound COMPLETELY HUMAN.

Example format:
[
  {{
    "slide_number": 1,
    "slide_title": "Title Slide",
    "script": "Hey everyone, welcome... [natural, conversational script that sounds like a real person]",
    "key_points": ["point1", "point2"],
    "talking_points": "Quick notes for yourself...",
    "estimated_duration_seconds": 90,
    "transition_to_next": "So moving on to our first real point...",
    "slide_explanation": "This is basically your welcome slide..."
  }},
  ...
]

Now generate completely natural, human-sounding scripts:"""
        
        return prompt
    
    def _parse_script_response(self, response_text, num_slides):
        """Parse the JSON response from Groq with robust error handling"""
        try:
            import re
            
            # Step 1: Extract JSON array from response (remove any text before/after)
            json_match = re.search(r'\[\s*\{[\s\S]*\}\s*\]', response_text)
            if json_match:
                json_text = json_match.group(0)
            else:
                json_text = response_text
            
            # Step 2: Try direct parsing first (best case)
            try:
                scripts = json.loads(json_text)
                if isinstance(scripts, list):
                    logger.info(f"✅ Successfully parsed {len(scripts)} scripts on first attempt")
                    self._validate_scripts(scripts)
                    return scripts
            except json.JSONDecodeError as initial_error:
                logger.debug(f"Initial JSON parse failed: {initial_error}")
            
            # Step 3: More aggressive newline handling
            # This handles unescaped newlines within JSON string values
            json_text_fixed = self._fix_unescaped_newlines(json_text)
            
            try:
                scripts = json.loads(json_text_fixed)
                if isinstance(scripts, list):
                    logger.info(f"✅ Successfully parsed {len(scripts)} scripts after newline fix")
                    self._validate_scripts(scripts)
                    return scripts
            except json.JSONDecodeError as second_error:
                logger.debug(f"After newline fix still failed: {second_error}")
            
            # Step 4: Last resort - attempt to reconstruct JSON field by field
            logger.warning("Attempting field-by-field JSON reconstruction...")
            scripts = self._reconstruct_json_from_text(json_text, num_slides)
            if scripts:
                logger.info(f"✅ Successfully reconstructed {len(scripts)} scripts from text")
                return scripts
            
            # If all parsing attempts fail
            raise json.JSONDecodeError("All JSON parsing strategies failed", json_text, 0)
        
        except Exception as e:
            logger.error(f"Failed to parse script response as JSON: {str(e)}")
            logger.error(f"Response text (first 800 chars): {response_text[:800]}")
            
            # Return fallback error scripts
            return self._create_fallback_scripts(num_slides)
    
    def _fix_unescaped_newlines(self, json_text):
        """Fix unescaped newlines within JSON string values"""
        import re
        
        # Strategy: Find all strings in JSON and escape their internal newlines
        def escape_string_content(match):
            full_string = match.group(0)
            # Don't escape the quotes themselves, just the content
            if full_string.startswith('"') and full_string.endswith('"'):
                content = full_string[1:-1]
                # Escape actual newlines but not already-escaped ones
                content = content.replace('\r\n', '\\n')
                content = content.replace('\n', '\\n')
                content = content.replace('\r', '\\n')
                # Fix double-escaped sequences
                content = content.replace('\\\\n', '\\n')
                return '"' + content + '"'
            return full_string
        
        # Find all quoted strings and fix newlines within them
        # This regex matches quoted strings, accounting for escaped quotes
        json_text = re.sub(r'"(?:[^"\\]|\\.)*"', escape_string_content, json_text)
        return json_text
    
    def _reconstruct_json_from_text(self, text, num_slides):
        """Attempt to reconstruct JSON by extracting field values"""
        import re
        
        scripts = []
        
        # Split by slide entries (look for "slide_number" patterns)
        slide_patterns = re.findall(
            r'\{\s*"slide_number":\s*(\d+)[^}]*?\}',
            text,
            re.DOTALL
        )
        
        if not slide_patterns:
            return None
        
        # Try to extract individual slide objects more carefully
        slide_start_indices = [m.start() for m in re.finditer(r'"slide_number"', text)]
        
        for i, start_idx in enumerate(slide_start_indices):
            end_idx = slide_start_indices[i + 1] if i + 1 < len(slide_start_indices) else len(text)
            slide_text = text[max(0, start_idx - 10):min(len(text), end_idx)]
            
            # Extract slide_number
            slide_match = re.search(r'"slide_number"\s*:\s*(\d+)', slide_text)
            slide_number = int(slide_match.group(1)) if slide_match else i + 1
            
            # Extract other fields with more lenient regex
            script = {
                "slide_number": slide_number,
                "slide_title": self._extract_field(slide_text, "slide_title", f"Slide {slide_number}"),
                "script": self._extract_field(slide_text, "script", "Script unavailable"),
                "key_points": self._extract_array_field(slide_text, "key_points", []),
                "talking_points": self._extract_field(slide_text, "talking_points", ""),
                "estimated_duration_seconds": self._extract_numeric_field(slide_text, "estimated_duration_seconds", 0),
                "transition_to_next": self._extract_field(slide_text, "transition_to_next", ""),
                "slide_explanation": self._extract_field(slide_text, "slide_explanation", "")
            }
            
            scripts.append(script)
        
        return scripts if scripts else None
    
    def _extract_field(self, text, field_name, default):
        """Extract a string field value from text"""
        import re
        pattern = rf'"{field_name}"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'
        match = re.search(pattern, text)
        if match:
            return match.group(1).replace('\\n', '\n').replace('\\/', '/')
        return default
    
    def _extract_array_field(self, text, field_name, default):
        """Extract an array field value from text"""
        import re
        pattern = rf'"{field_name}"\s*:\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            array_content = match.group(1)
            # Extract all quoted strings
            items = re.findall(r'"([^"]*)"', array_content)
            return items if items else default
        return default
    
    def _extract_numeric_field(self, text, field_name, default):
        """Extract a numeric field value from text"""
        import re
        pattern = rf'"{field_name}"\s*:\s*(\d+(?:\.\d+)?)'
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        return default
    
    def _validate_scripts(self, scripts):
        """Validate and fill in missing fields in scripts"""
        for script in scripts:
            if 'script' not in script:
                script['script'] = ""
            if 'key_points' not in script:
                script['key_points'] = []
            if 'estimated_duration_seconds' not in script:
                script['estimated_duration_seconds'] = 0
            if 'slide_explanation' not in script:
                script['slide_explanation'] = ""
            if 'transition_to_next' not in script:
                script['transition_to_next'] = ""
            if 'talking_points' not in script:
                script['talking_points'] = ""
    
    def _create_fallback_scripts(self, num_slides):
        """Create fallback error scripts when parsing completely fails"""
        return [{
            "slide_number": i + 1,
            "slide_title": "Script Generation Error",
            "script": "An error occurred while generating the script. Please try again.",
            "key_points": [],
            "estimated_duration_seconds": 0,
            "slide_explanation": "Error in script generation",
            "transition_to_next": "",
            "talking_points": ""
        } for i in range(num_slides)]
    
    def generate_script_for_single_slide(self, slide, presentation_tone, slide_duration, 
                                        presentation_title="", previous_slide_title="", 
                                        next_slide_title=""):
        """
        Generate script for a single slide
        
        Args:
            slide: Dictionary with slide content (title, content, bullets, etc)
            presentation_tone: Tone of presentation
            slide_duration: Duration in minutes for this slide
            presentation_title: Title of the overall presentation
            previous_slide_title: Title of previous slide for context
            next_slide_title: Title of next slide for context
        
        Returns:
            Dictionary with script for the slide
        """
        try:
            prompt = f"""You are an expert presentation speaker. Write a completely NATURAL, HUMAN-LIKE script for a single presentation slide - sounds like a real person talking, NOT AI.

HUMANIZATION RULES:
- Sound like a REAL PERSON speaking naturally to an audience
- Use conversational language with natural variations
- Mix short and long sentences naturally
- Include casual phrases: "you know", "actually", "so here's the thing", "look"
- Use contractions: "that's", "you'll", "isn't", "won't"
- Add engagement: rhetorical questions, personal language
- Make transitions feel spontaneous and natural
- Include realistic pauses and pacing
- Write imperfectly (humans don't speak in perfect structures)

SLIDE CONTEXT:
- Presentation: {presentation_title}
- Tone: {presentation_tone}
- Duration: {slide_duration} minutes ({int(slide_duration * 60)} seconds)
- Previous Slide: {previous_slide_title if previous_slide_title else "This is the opening"}
- Current Slide: {slide.get('title', 'Slide')}
- Next Slide: {next_slide_title if next_slide_title else "Conclusion"}

SLIDE CONTENT:
Title: {slide.get('title', 'Untitled')}
Subtitle: {slide.get('subtitle', '')}
Content: {slide.get('content', '')}
Bullets: {json.dumps(slide.get('bullets', []), ensure_ascii=False)}

EXAMPLE OF NATURAL SCRIPT (What to Aim For):
"Okay, so we've talked about the basics. Now here's where it gets interesting - and I mean really interesting. So think about what we just covered. That foundation? That's everything. Because when you understand that, suddenly all these other pieces start to make sense. Let me show you why..."

INSTRUCTIONS:
1. Write naturally as if speaking to an audience
2. Sound 100% human - like someone sharing knowledge conversationally
3. Include natural pauses and rhythm variations
4. Make key points naturally (not robotically)
5. Create smooth transitions from previous slide
6. Prepare audience for next topic
7. Speak for {int(slide_duration * 60)} seconds at natural pace

Return as JSON (NATURAL sounding script):
{{
  "slide_number": 1,
  "slide_title": "{slide.get('title', 'Untitled')}",
  "script": "<completely natural, conversational script - sounds like real person talking>",
  "key_points": ["point1", "point2", "point3"],
  "talking_points": "<casual notes for speaker>",
  "estimated_duration_seconds": {int(slide_duration * 60)},
  "transition_to_next": "<natural transition to next slide>",
  "slide_explanation": "<what this slide teaches>"
}}

Generate the script NOW - make it sound COMPLETELY HUMAN:"""
            
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.choices[0].message.content
            
            # Parse JSON response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                json_text = response_text
            
            script = json.loads(json_text)
            
            return {
                "success": True,
                "script": script
            }
        
        except Exception as e:
            logger.error(f"Error generating single slide script: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "script": {}
            }
