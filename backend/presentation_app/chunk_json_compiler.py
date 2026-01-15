"""
Chunk JSON Compiler
Compiles chunk-wise slide JSON data into unified, validated JSON structure
Ensures PPTX compatibility and maintains proper slide ordering and hierarchy
"""

import json
from typing import List, Dict, Optional


class ChunkJSONCompiler:
    """Compiles chunk-wise JSON data into unified presentation structure"""
    
    def __init__(self, topic: str, target_audience: str, tone: str):
        """
        Initialize compiler
        
        Args:
            topic: Presentation topic
            target_audience: Target audience
            tone: Presentation tone
        """
        self.topic = topic
        self.target_audience = target_audience
        self.tone = tone
    
    def compile_chunk_slides(
        self,
        chunk_slides_list: List[List[Dict]],
        chunk_count: int,
        overview_data: Optional[Dict] = None
    ) -> Dict:
        """
        Compile multiple chunks' slide data into unified JSON structure
        
        Args:
            chunk_slides_list: List of slide lists, one per chunk
            chunk_count: Total number of chunks
            overview_data: Optional overview slide data
            
        Returns:
            Unified presentation JSON structure
        """
        all_slides = []
        slide_number = 1
        
        # Add overview/title slide
        if overview_data:
            overview_slide = overview_data.copy()
            overview_slide['slide_number'] = slide_number
            all_slides.append(overview_slide)
        else:
            all_slides.append({
                "slide_number": slide_number,
                "slide_type": "title",
                "title": f"Comprehensive Overview: {self.topic}",
                "subtitle": f"Content compiled from {chunk_count} major sections",
                "bullets": [],
                "speaker_notes": f"This presentation covers {self.topic} across {chunk_count} comprehensive sections.",
                "visuals": {"icons": ["presentation"], "symbols": []}
            })
        
        slide_number += 1
        
        # Process and compile chunk slides
        chunk_index = 1
        for chunk_slides in chunk_slides_list:
            for slide in chunk_slides:
                # Validate and normalize slide structure
                normalized_slide = self._normalize_slide(slide, slide_number, chunk_index)
                all_slides.append(normalized_slide)
                slide_number += 1
            chunk_index += 1
        
        # Add conclusion slide with 4-8 bullets
        conclusion_slide = {
            "slide_number": slide_number,
            "slide_type": "conclusion",
            "title": "Conclusion & Key Takeaways",
            "subtitle": f"{self.topic} Summary",
            "bullets": [
                "Comprehensive coverage across all major sections",
                "Integrated key findings into structured presentation",
                "Ready for discussion and strategic decision-making",
                "Actionable insights delivered through professional analysis"
            ],
            "speaker_notes": "Thank you for reviewing this comprehensive presentation. We have covered all major aspects with professional analysis and detailed insights.",
            "visuals": {"icons": ["checkmark"], "symbols": []}
        }
        all_slides.append(conclusion_slide)
        
        # Create unified JSON structure
        return {
            "presentation_title": f"{self.topic} - Comprehensive Presentation",
            "topic": self.topic,
            "target_audience": self.target_audience,
            "tone": self.tone,
            "total_slides": slide_number - 1,
            "slides": all_slides,
            "metadata": {
                "generated_with_chunking": True,
                "number_of_chunks": chunk_count,
                "compilation_status": "unified"
            }
        }
    
    def _normalize_slide(self, slide: Dict, slide_number: int, chunk_index: int) -> Dict:
        """
        Normalize slide structure to ensure PPTX compatibility
        
        Args:
            slide: Raw slide data from chunk
            slide_number: Normalized slide number
            chunk_index: Which chunk this came from
            
        Returns:
            Normalized slide dictionary
        """
        # Ensure required fields exist
        normalized = {
            "slide_number": slide_number,
            "slide_type": slide.get("slide_type", "content"),
            "title": slide.get("title", ""),
            "subtitle": slide.get("subtitle", ""),
            "bullets": slide.get("bullets") or slide.get("slide_bullets", []),
            "speaker_notes": slide.get("speaker_notes", ""),
            "visuals": slide.get("visuals") or slide.get("slide_visuals", {}),
        }
        
        # Handle different bullet formats
        bullets = normalized["bullets"]
        if bullets and isinstance(bullets[0], dict):
            # If bullets are dicts with text/icon/emoji, extract text only for PPTX
            normalized["bullets"] = [
                bullet.get("text", str(bullet)) if isinstance(bullet, dict) else str(bullet)
                for bullet in bullets
            ]
        
        # Ensure visuals is properly structured
        if not isinstance(normalized["visuals"], dict):
            normalized["visuals"] = {}
        
        # Normalize visuals keys
        if not normalized["visuals"].get("icons"):
            normalized["visuals"]["icons"] = []
        if not normalized["visuals"].get("symbols"):
            normalized["visuals"]["symbols"] = []
        
        return normalized
    
    def validate_compiled_json(self, json_data: Dict) -> Dict:
        """
        Validate and clean compiled JSON for PPTX compatibility
        
        Args:
            json_data: Compiled JSON data
            
        Returns:
            Validated and cleaned JSON data
        """
        # Check required top-level fields
        required_fields = ["presentation_title", "topic", "target_audience", "tone", "slides"]
        for field in required_fields:
            if field not in json_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate slides
        slides = json_data.get("slides", [])
        if not slides:
            raise ValueError("No slides in presentation")
        
        # Ensure proper slide numbering
        for i, slide in enumerate(slides):
            slide["slide_number"] = i + 1
        
        # Validate slide types
        valid_types = {"title", "content", "section", "conclusion"}
        for slide in slides:
            if slide.get("slide_type") not in valid_types:
                slide["slide_type"] = "content"
        
        # Ensure title and subtitle are strings
        for slide in slides:
            if not isinstance(slide.get("title"), str):
                slide["title"] = str(slide.get("title", ""))
            if not isinstance(slide.get("subtitle"), str):
                slide["subtitle"] = str(slide.get("subtitle", ""))
        
        # Ensure bullets is a list of strings
        for slide in slides:
            bullets = slide.get("bullets", [])
            if not isinstance(bullets, list):
                slide["bullets"] = []
            else:
                # Convert all bullets to strings
                slide["bullets"] = [str(b) for b in bullets]
        
        # Ensure speaker_notes is a string
        for slide in slides:
            if not isinstance(slide.get("speaker_notes"), str):
                slide["speaker_notes"] = str(slide.get("speaker_notes", ""))
        
        # Update total_slides
        json_data["total_slides"] = len(slides)
        
        return json_data
    
    def save_chunk_json(self, chunk_slides: List[Dict], chunk_number: int, output_dir: str = None) -> str:
        """
        Save chunk-wise JSON data to file
        
        Args:
            chunk_slides: List of slides for this chunk
            chunk_number: Chunk number
            output_dir: Output directory (optional)
            
        Returns:
            Path to saved file
        """
        if output_dir is None:
            output_dir = "/tmp"
        
        chunk_data = {
            "chunk_number": chunk_number,
            "slides": chunk_slides,
            "chunk_metadata": {
                "total_slides_in_chunk": len(chunk_slides)
            }
        }
        
        filename = f"{output_dir}/chunk_{chunk_number}_slides.json"
        with open(filename, 'w') as f:
            json.dump(chunk_data, f, indent=2)
        
        return filename
