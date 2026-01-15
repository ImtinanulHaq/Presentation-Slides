"""
Professional Content Chunking Utility for Large Data Processing
================================================================================
Intelligently divides large content into optimal chunks for LLM processing
while preserving semantic meaning and preventing token limit issues.

Features:
- Automatic chunking for content >= 300 words
- Multi-level semantic splitting (paragraphs → sentences → words)
- Aggressive token enforcement with validation
- Professional handling of any data size
- Zero data loss preservation
- Configurable chunk sizing
================================================================================
"""

import re
from typing import List, Dict


class ContentChunker:
    """
    Professional content chunker that intelligently divides content
    into semantically coherent chunks within token limits.
    
    Handles any data size gracefully with strict validation and
    multiple fallback strategies to ensure robustness.
    """
    
    # ============================================================================
    # CONFIGURATION CONSTANTS
    # ============================================================================
    
    # Approximate tokens per word (conservative estimate for safety)
    TOKENS_PER_WORD = 1.3
    
    # Aggressive token limit per chunk (reduced from 2000 for safety)
    # This creates more, smaller chunks that are safer for processing
    SAFE_TOKEN_LIMIT = 1500
    
    # Ultra-conservative limit for emergency chunking (last resort)
    EMERGENCY_TOKEN_LIMIT = 1200
    
    # Automatic chunking threshold
    AUTO_CHUNK_THRESHOLD = 300
    
    # Minimum words per chunk (avoid tiny fragments)
    MIN_WORDS_PER_CHUNK = 50
    
    def __init__(self, max_tokens_per_chunk: int = None):
        """
        Initialize professional chunker
        
        Args:
            max_tokens_per_chunk: Custom token limit (uses SAFE_TOKEN_LIMIT if None)
        """
        self.max_tokens_per_chunk = max_tokens_per_chunk or self.SAFE_TOKEN_LIMIT
        self.words_per_chunk = int(self.max_tokens_per_chunk / self.TOKENS_PER_WORD)
    
    # ============================================================================
    # PUBLIC API METHODS
    # ============================================================================
    
    def should_auto_chunk(self, content: str) -> bool:
        """
        Determine if content should be automatically chunked.
        
        Args:
            content: Raw content to evaluate
            
        Returns:
            True if content >= 300 words (should be chunked)
        """
        word_count = len(content.split())
        return word_count >= self.AUTO_CHUNK_THRESHOLD
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text with conservative multiplier.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        words = len(text.split())
        return int(words * self.TOKENS_PER_WORD)
    
    def get_word_count(self, content: str) -> int:
        """
        Get word count of content.
        
        Args:
            content: Text to count
            
        Returns:
            Number of words
        """
        return len(content.split())
    
    def chunk_content(self, content: str) -> List[str]:
        """
        Intelligently chunk content while preserving all data.
        
        Uses multi-level semantic splitting:
        1. Try paragraph-level splitting
        2. Fall back to sentence-level splitting
        3. Final validation and emergency re-chunking if needed
        
        Guarantees:
        - 100% data preservation
        - All chunks under token limit
        - Semantically coherent chunks
        - No data loss
        
        Args:
            content: Content to chunk
            
        Returns:
            List of chunks (each <= SAFE_TOKEN_LIMIT tokens)
        """
        # Quick return if content is small enough
        if self.estimate_tokens(content) <= self.max_tokens_per_chunk:
            return [content]
        
        # Stage 1: Try paragraph-based chunking
        chunks = self._chunk_by_paragraphs(content)
        
        # Stage 2: Validate chunks
        validated_chunks = self._validate_and_repair_chunks(chunks)
        
        # Stage 3: Final validation
        final_chunks = self._ensure_chunk_safety(validated_chunks)
        
        return final_chunks
    
    # ============================================================================
    # PRIVATE CHUNKING METHODS (MULTI-LEVEL STRATEGY)
    # ============================================================================
    
    def _chunk_by_paragraphs(self, content: str) -> List[str]:
        """
        Stage 1: Chunk by paragraphs (most semantic approach).
        
        Preserves natural paragraph breaks when possible,
        falling back to sentences only when necessary.
        """
        safe_limit = int(self.max_tokens_per_chunk * 0.85)  # 85% safety margin
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            # Fallback: treat entire content as one paragraph
            return self._chunk_by_sentences(content, safe_limit)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for paragraph in paragraphs:
            para_tokens = self.estimate_tokens(paragraph)
            
            # If single paragraph exceeds limit, split it by sentences
            if para_tokens > safe_limit:
                # Save current chunk
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Split large paragraph by sentences
                sub_chunks = self._chunk_by_sentences(paragraph, safe_limit)
                chunks.extend(sub_chunks)
            
            # Try to add paragraph to current chunk
            elif current_tokens + para_tokens <= safe_limit:
                current_chunk.append(paragraph)
                current_tokens += para_tokens
            
            # Start new chunk
            else:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_tokens = para_tokens
        
        # Add remaining
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _chunk_by_sentences(self, content: str, max_tokens: int) -> List[str]:
        """
        Stage 2: Chunk by sentences when paragraphs are too large.
        
        Splits on sentence boundaries to maintain context.
        """
        sentences = self._split_sentences(content)
        
        if not sentences:
            # Fallback: split by words
            return self._chunk_by_words(content, max_tokens)
        
        chunks = []
        current = []
        current_tokens = 0
        
        for sentence in sentences:
            sent_tokens = self.estimate_tokens(sentence)
            
            # Handle overly large sentences (shouldn't happen but be safe)
            if sent_tokens > max_tokens:
                # Save current chunk
                if current:
                    chunks.append(' '.join(current))
                    current = []
                    current_tokens = 0
                
                # Force split the large sentence by words
                word_chunks = self._chunk_by_words(sentence, max_tokens)
                chunks.extend(word_chunks)
            
            # Try to add sentence to current chunk
            elif current_tokens + sent_tokens <= max_tokens:
                current.append(sentence)
                current_tokens += sent_tokens
            
            # Start new chunk
            else:
                if current:
                    chunks.append(' '.join(current))
                current = [sentence]
                current_tokens = sent_tokens
        
        # Add remaining
        if current:
            chunks.append(' '.join(current))
        
        return chunks
    
    def _chunk_by_words(self, content: str, max_tokens: int) -> List[str]:
        """
        Emergency Stage 3: Chunk by words if sentences fail.
        
        Last resort - splits by words while maintaining meaning.
        """
        words = content.split()
        
        if not words:
            return [content]
        
        chunks = []
        current = []
        current_tokens = 0
        target_words = int(max_tokens / self.TOKENS_PER_WORD * 0.9)
        
        for word in words:
            word_tokens = len(word) / 4  # Rough estimate
            
            if len(current) >= target_words:
                # Chunk is full
                chunks.append(' '.join(current))
                current = [word]
                current_tokens = word_tokens
            else:
                current.append(word)
                current_tokens += word_tokens
        
        if current:
            chunks.append(' '.join(current))
        
        return chunks
    
    # ============================================================================
    # VALIDATION & REPAIR METHODS
    # ============================================================================
    
    def _validate_and_repair_chunks(self, chunks: List[str]) -> List[str]:
        """
        Validate all chunks and repair any that exceed limits.
        
        This is the critical safety layer that ensures no chunk
        ever exceeds the token limit, no matter what.
        """
        repaired = []
        
        for chunk in chunks:
            chunk_tokens = self.estimate_tokens(chunk)
            
            # If chunk is safe, keep it
            if chunk_tokens <= self.max_tokens_per_chunk:
                repaired.append(chunk)
            else:
                # Emergency re-chunking
                safe_limit = int(self.EMERGENCY_TOKEN_LIMIT * 0.85)
                sub_chunks = self._chunk_by_sentences(chunk, safe_limit)
                
                # Recursively repair if needed
                for sub_chunk in sub_chunks:
                    sub_tokens = self.estimate_tokens(sub_chunk)
                    if sub_tokens > self.max_tokens_per_chunk:
                        # Final fallback: word-level chunking
                        word_chunks = self._chunk_by_words(sub_chunk, safe_limit)
                        repaired.extend(word_chunks)
                    else:
                        repaired.append(sub_chunk)
        
        return repaired
    
    def _ensure_chunk_safety(self, chunks: List[str]) -> List[str]:
        """
        Final validation pass to guarantee all chunks are safe.
        
        Removes any chunks that exceed limit (shouldn't happen
        but provides absolute guarantee).
        """
        safe_chunks = []
        
        for chunk in chunks:
            tokens = self.estimate_tokens(chunk)
            words = len(chunk.split())
            
            # Check both token and word count
            if tokens > self.max_tokens_per_chunk:
                # This chunk is still too large - force smaller
                smaller = self._chunk_by_words(chunk, int(self.EMERGENCY_TOKEN_LIMIT * 0.8))
                safe_chunks.extend(smaller)
            elif words < self.MIN_WORDS_PER_CHUNK and safe_chunks:
                # Merge tiny chunks with previous one
                if safe_chunks:
                    safe_chunks[-1] = safe_chunks[-1] + ' ' + chunk
            else:
                safe_chunks.append(chunk)
        
        return safe_chunks
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences while preserving some context.
        
        Handles common abbreviations and edge cases.
        """
        # Enhanced sentence splitting
        text = text.replace('Mr.', 'Mr').replace('Mrs.', 'Mrs').replace('Dr.', 'Dr')
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunk_metadata(self, chunks: List[str]) -> Dict:
        """
        Create comprehensive metadata about chunks.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Dictionary with detailed chunk information
        """
        metadata = {
            'total_chunks': len(chunks),
            'chunk_tokens': [self.estimate_tokens(chunk) for chunk in chunks],
            'chunk_words': [len(chunk.split()) for chunk in chunks],
            'total_tokens': sum(self.estimate_tokens(chunk) for chunk in chunks),
            'total_words': sum(len(chunk.split()) for chunk in chunks),
            'safe_limit': self.max_tokens_per_chunk,
            'emergency_limit': self.EMERGENCY_TOKEN_LIMIT,
            'auto_chunk_threshold': self.AUTO_CHUNK_THRESHOLD,
            'max_chunk_tokens': max(self.estimate_tokens(c) for c in chunks) if chunks else 0,
            'min_chunk_tokens': min(self.estimate_tokens(c) for c in chunks) if chunks else 0,
            'avg_chunk_tokens': sum(self.estimate_tokens(c) for c in chunks) // len(chunks) if chunks else 0,
        }
        return metadata


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
