"""
Script Generator using Groq API
Generates professional speaker scripts for presentation slides
"""

import os
import json
import logging
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
    
    def generate_script_for_slides(self, slides, presentation_tone, total_duration, presentation_title=""):
        """
        Generate speaker scripts for presentation slides
        
        Args:
            slides: List of slide dictionaries with title, content, bullets
            presentation_tone: Tone of presentation (professional, casual, academic, persuasive)
            total_duration: Total duration in minutes for the entire presentation
            presentation_title: Title of the presentation
        
        Returns:
            Dictionary with scripts for each slide including timing and explanations
        """
        try:
            # Calculate duration per slide
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
            
            logger.info(f"Generating script for {num_slides} slides with {total_duration} minutes duration")
            
            # Call Groq API
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the response
            script_text = message.choices[0].message.content
            scripts = self._parse_script_response(script_text, num_slides)
            
            return {
                "success": True,
                "scripts": scripts,
                "metadata": {
                    "total_duration": total_duration,
                    "duration_per_slide": round(duration_per_slide, 2),
                    "num_slides": num_slides,
                    "tone": presentation_tone,
                    "presentation_title": presentation_title
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "scripts": []
            }
    
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
        """Parse the JSON response from Groq"""
        try:
            # Try to extract JSON from the response
            # Sometimes the API might include extra text
            import re
            
            # Find JSON array in response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                json_text = response_text
            
            # Clean up the JSON text - fix unescaped newlines within strings
            # Replace literal newlines within quoted strings with \n
            json_text = re.sub(r'(?<=["\'])\n(?=["\'])', '\\n', json_text)
            # More aggressive cleanup: escape newlines in script content
            lines = json_text.split('\n')
            cleaned_lines = []
            in_string = False
            
            for line in lines:
                # Simple heuristic: if line looks like it's inside a string, escape the quotes properly
                cleaned_lines.append(line)
            
            json_text = '\n'.join(cleaned_lines)
            
            # Try to parse multiple times with different approaches
            try:
                scripts = json.loads(json_text)
            except json.JSONDecodeError:
                # Try to fix by escaping newlines in the content
                json_text = json_text.replace('\n', '\\n')
                # But unescape the newlines that should be there (like at end of lines)
                json_text = re.sub(r'\\n\s*"', '"', json_text)
                json_text = re.sub(r'\\n\s*}', '}', json_text)
                scripts = json.loads(json_text)
            
            # Validate that we got scripts for all slides
            if not isinstance(scripts, list):
                logger.warning("Response is not a list, wrapping in list")
                scripts = [scripts]
            
            # Ensure all required fields are present
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
            
            logger.info(f"Successfully parsed {len(scripts)} scripts from response")
            return scripts
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse script response as JSON: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}")
            
            # Return empty scripts if parsing fails
            return [{
                "slide_number": i + 1,
                "slide_title": "Script Generation Failed",
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
