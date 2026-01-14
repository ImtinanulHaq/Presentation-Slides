"""
Content Chunking Utility for handling large content inputs
Divides content into manageable chunks to avoid LLM token limits
"""

import re
from typing import List, Dict


class ContentChunker:
    """Chunks large content into smaller pieces while maintaining semantic meaning"""
    
    # Approximate tokens per word (varies by content, but 1.3 is a safe average)
    TOKENS_PER_WORD = 1.3
    
    # Safe token limit per chunk for Groq API
    # Groq TPM limit is 6000, but we're conservative:
    # - Keep each chunk under 2000 tokens (safe margin)
    # - This allows for prompt overhead and multiple API calls
    SAFE_TOKEN_LIMIT = 2000
    
    # Approximate words per chunk
    WORDS_PER_CHUNK = int(SAFE_TOKEN_LIMIT / TOKENS_PER_WORD)
    
    def __init__(self, max_tokens_per_chunk: int = SAFE_TOKEN_LIMIT):
        """
        Initialize chunker
        
        Args:
            max_tokens_per_chunk: Maximum tokens per chunk (default: 3000)
        """
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.words_per_chunk = int(max_tokens_per_chunk / self.TOKENS_PER_WORD)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        words = len(text.split())
        return int(words * self.TOKENS_PER_WORD)
    
    def chunk_content(self, content: str) -> List[str]:
        """
        Divide content into chunks while maintaining semantic meaning
        
        Args:
            content: Raw content to chunk
            
        Returns:
            List of content chunks
        """
        # Check if chunking is needed
        token_count = self.estimate_tokens(content)
        if token_count <= self.max_tokens_per_chunk:
            return [content]
        
        chunks = []
        
        # Split by double newlines (paragraphs) first
        paragraphs = content.split('\n\n')
        
        current_chunk = []
        current_tokens = 0
        
        for paragraph in paragraphs:
            para_tokens = self.estimate_tokens(paragraph)
            
            # If single paragraph is too large, split it further
            if para_tokens > self.max_tokens_per_chunk:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Split large paragraph by sentences
                sentences = self._split_sentences(paragraph)
                for sentence in sentences:
                    sent_tokens = self.estimate_tokens(sentence)
                    
                    if current_tokens + sent_tokens > self.max_tokens_per_chunk:
                        if current_chunk:
                            chunks.append('\n\n'.join(current_chunk))
                            current_chunk = []
                            current_tokens = 0
                    
                    current_chunk.append(sentence)
                    current_tokens += sent_tokens
            
            else:
                # Add paragraph to current chunk if it fits
                if current_tokens + para_tokens <= self.max_tokens_per_chunk:
                    current_chunk.append(paragraph)
                    current_tokens += para_tokens
                else:
                    # Save current chunk and start new one
                    if current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [paragraph]
                    current_tokens = para_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Split by common sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]
    
    def create_chunk_metadata(self, chunks: List[str]) -> Dict:
        """
        Create metadata about chunks
        
        Args:
            chunks: List of content chunks
            
        Returns:
            Dictionary with chunk information
        """
        return {
            'total_chunks': len(chunks),
            'chunk_tokens': [self.estimate_tokens(chunk) for chunk in chunks],
            'total_tokens': sum(self.estimate_tokens(chunk) for chunk in chunks),
            'safe_limit': self.max_tokens_per_chunk,
        }


def create_chunked_prompt(chunks: List[str], topic: str, audience: str, tone: str) -> str:
    """
    Create a prompt for processing multiple chunks
    
    Args:
        chunks: List of content chunks
        topic: Presentation topic
        audience: Target audience
        tone: Presentation tone
        
    Returns:
        Formatted prompt for LLM
    """
    prompt = f"""You are creating a comprehensive presentation on "{topic}".

The content provided has been divided into {len(chunks)} sections due to length.
Process each section and extract key points for presentation slides.

Target Audience: {audience}
Tone: {tone}

For each section, create slides following this structure:
- One slide per major topic/subtopic
- Clear titles
- 3-5 bullet points per slide
- Professional speaker notes
- Visual suggestions (icons, images)

Here are the content sections:

"""
    
    for i, chunk in enumerate(chunks, 1):
        prompt += f"\n--- Section {i}/{len(chunks)} ---\n{chunk}\n"
    
    prompt += f"""
After processing all sections, create a final JSON structure with:
1. An overview slide
2. Slides for each section's key points
3. Conclusion slide

Use this JSON format for final output:
{{
  "presentation_title": "Suitable title",
  "slides": [
    {{
      "slide_number": 1,
      "slide_type": "title",
      "title": "Title",
      "subtitle": "Subtitle",
      "bullets": [],
      "speaker_notes": "Notes",
      "visuals": {{"icons": [], "symbols": []}}
    }}
  ]
}}
"""
    
    return prompt
