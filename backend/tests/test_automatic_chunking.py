"""
Test automatic content chunking functionality
Validates that content >= 300 words is automatically chunked
Verifies JSON compilation and PPTX compatibility
"""

import os
import json
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'presentation_project.settings')
django.setup()

from presentation_app.content_chunker import ContentChunker
from presentation_app.chunk_json_compiler import ChunkJSONCompiler
from presentation_app.presentation_generator import GroqPresentationGenerator


class TestAutomaticChunking:
    """Test suite for automatic content chunking"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []
    
    def test_word_count_detection(self):
        """Test that auto-chunking threshold is detected correctly"""
        print("\n" + "="*80)
        print("TEST 1: Word Count Detection (300-word threshold)")
        print("="*80)
        
        chunker = ContentChunker()
        
        # Test 1a: Content below threshold (< 300 words)
        short_content = " ".join(["word"] * 250)
        should_chunk = chunker.should_auto_chunk(short_content)
        
        if not should_chunk:
            print("✓ PASS: Content with 250 words NOT auto-chunked")
            self.passed += 1
        else:
            print("✗ FAIL: Content with 250 words should NOT be auto-chunked")
            self.failed += 1
        
        # Test 1b: Content at threshold (300 words)
        threshold_content = " ".join(["word"] * 300)
        should_chunk = chunker.should_auto_chunk(threshold_content)
        
        if should_chunk:
            print("✓ PASS: Content with 300 words IS auto-chunked (meets threshold)")
            self.passed += 1
        else:
            print("✗ FAIL: Content with 300 words should be auto-chunked")
            self.failed += 1
        
        # Test 1c: Content above threshold (> 300 words)
        long_content = " ".join(["word"] * 500)
        should_chunk = chunker.should_auto_chunk(long_content)
        
        if should_chunk:
            print("✓ PASS: Content with 500 words IS auto-chunked")
            self.passed += 1
        else:
            print("✗ FAIL: Content with 500 words should be auto-chunked")
            self.failed += 1
        
        print(f"\nWord Count Detection: {self.passed - 2} passed")
    
    def test_chunk_content_preservation(self):
        """Test that chunking preserves content meaning and structure"""
        print("\n" + "="*80)
        print("TEST 2: Content Preservation During Chunking")
        print("="*80)
        
        chunker = ContentChunker()
        
        # Create meaningful content with logical sections
        content = """
        Introduction. This is the beginning of our content.
        
        Section One. The first major point with detailed explanation. 
        It contains important information that should not be lost.
        
        Section Two. The second major point follows logically.
        Additional details expand on the concept.
        
        Section Three. The third topic builds on previous sections.
        Context is preserved throughout the flow.
        """ * 3  # Repeat to exceed 300 words
        
        chunks = chunker.chunk_content(content)
        reconstructed = " ".join(chunks)
        
        # Check that all key phrases are preserved
        key_phrases = ["Section One", "Section Two", "Section Three", "Introduction"]
        all_preserved = all(phrase in reconstructed for phrase in key_phrases)
        
        if all_preserved:
            print(f"✓ PASS: All content sections preserved across {len(chunks)} chunks")
            self.passed += 1
        else:
            print("✗ FAIL: Some content sections were lost during chunking")
            self.failed += 1
        
        # Check word count is preserved
        original_words = len(content.split())
        reconstructed_words = len(reconstructed.split())
        
        # Allow for minor differences due to splitting
        if abs(original_words - reconstructed_words) < 10:
            print(f"✓ PASS: Word count preserved ({original_words} → {reconstructed_words})")
            self.passed += 1
        else:
            print(f"✗ FAIL: Word count not preserved ({original_words} → {reconstructed_words})")
            self.failed += 1
    
    def test_chunk_json_compiler(self):
        """Test that chunk JSON compiler creates valid unified structure"""
        print("\n" + "="*80)
        print("TEST 3: Chunk JSON Compilation")
        print("="*80)
        
        compiler = ChunkJSONCompiler(
            topic="Test Topic",
            target_audience="General",
            tone="professional"
        )
        
        # Create sample chunk slides
        chunk1_slides = [
            {
                "slide_type": "content",
                "title": "Chunk 1 - Part 1",
                "subtitle": "Introduction",
                "bullets": ["Point 1", "Point 2"],
                "speaker_notes": "Details about chunk 1 part 1"
            },
            {
                "slide_type": "content",
                "title": "Chunk 1 - Part 2",
                "subtitle": "Details",
                "bullets": ["Point 3", "Point 4"],
                "speaker_notes": "Details about chunk 1 part 2"
            }
        ]
        
        chunk2_slides = [
            {
                "slide_type": "content",
                "title": "Chunk 2 - Analysis",
                "subtitle": "Key findings",
                "bullets": ["Finding 1", "Finding 2"],
                "speaker_notes": "Analysis from chunk 2"
            }
        ]
        
        all_chunk_slides = [chunk1_slides, chunk2_slides]
        
        # Compile
        compiled = compiler.compile_chunk_slides(
            chunk_slides_list=all_chunk_slides,
            chunk_count=2
        )
        
        # Validate structure
        required_keys = ["presentation_title", "topic", "target_audience", "tone", "slides", "metadata"]
        has_all_keys = all(key in compiled for key in required_keys)
        
        if has_all_keys:
            print("✓ PASS: Compiled JSON has all required keys")
            self.passed += 1
        else:
            print("✗ FAIL: Compiled JSON missing required keys")
            self.failed += 1
        
        # Validate slide count (overview + 2 from chunk1 + 1 from chunk2 + conclusion = 5)
        expected_slides = 1 + 2 + 1 + 1  # title + chunk1 + chunk2 + conclusion
        actual_slides = len(compiled["slides"])
        
        if actual_slides == expected_slides:
            print(f"✓ PASS: Slide count correct ({actual_slides} slides)")
            self.passed += 1
        else:
            print(f"✗ FAIL: Slide count incorrect (expected {expected_slides}, got {actual_slides})")
            self.failed += 1
        
        # Validate that total_slides is set
        if compiled.get("total_slides") == len(compiled["slides"]):
            print("✓ PASS: total_slides field correctly set")
            self.passed += 1
        else:
            print("✗ FAIL: total_slides field not correct")
            self.failed += 1
    
    def test_json_validation(self):
        """Test that compiled JSON validates correctly for PPTX compatibility"""
        print("\n" + "="*80)
        print("TEST 4: JSON Validation for PPTX Compatibility")
        print("="*80)
        
        compiler = ChunkJSONCompiler(
            topic="Validation Test",
            target_audience="Technical",
            tone="academic"
        )
        
        # Create JSON with potential issues
        test_json = {
            "presentation_title": "Test",
            "topic": "Test Topic",
            "target_audience": "Technical",
            "tone": "academic",
            "total_slides": 0,  # Will be updated
            "slides": [
                {
                    "slide_number": 1,
                    "slide_type": "title",
                    "title": "Title",
                    "subtitle": "Subtitle",
                    "bullets": [],
                    "speaker_notes": "Opening",
                    "visuals": {}
                },
                {
                    "slide_number": 2,
                    "slide_type": "invalid_type",  # Invalid type
                    "title": "Content",
                    "subtitle": "Details",
                    "bullets": ["Bullet 1"],
                    "speaker_notes": "Notes",
                    "visuals": {"icons": []}
                }
            ]
        }
        
        # Validate
        try:
            validated = compiler.validate_compiled_json(test_json)
            
            # Check that invalid slide type was corrected
            if validated["slides"][1]["slide_type"] in ["title", "content", "section", "conclusion"]:
                print("✓ PASS: Invalid slide types corrected to 'content'")
                self.passed += 1
            else:
                print("✗ FAIL: Invalid slide type not corrected")
                self.failed += 1
            
            # Check that total_slides was updated
            if validated["total_slides"] == len(validated["slides"]):
                print("✓ PASS: total_slides updated correctly")
                self.passed += 1
            else:
                print("✗ FAIL: total_slides not updated")
                self.failed += 1
            
            # Check that slide numbers are sequential
            slides = validated["slides"]
            is_sequential = all(
                slides[i]["slide_number"] == i + 1 
                for i in range(len(slides))
            )
            
            if is_sequential:
                print("✓ PASS: Slide numbers are sequential")
                self.passed += 1
            else:
                print("✗ FAIL: Slide numbers are not sequential")
                self.failed += 1
                
        except Exception as e:
            print(f"✗ FAIL: Validation raised exception: {str(e)}")
            self.failed += 1
    
    def test_generator_auto_activation(self):
        """Test that generator automatically enables chunking for 300+ word content"""
        print("\n" + "="*80)
        print("TEST 5: Generator Auto-Activation of Chunking")
        print("="*80)
        
        try:
            # Create generator with 300+ word content (but don't generate, just check auto-activation)
            content = " ".join(["word"] * 350)
            
            generator = GroqPresentationGenerator(
                topic="Auto-Chunking Test",
                raw_content=content,
                target_audience="General",
                tone="professional",
                num_slides=None,  # Don't specify slide count
                enable_chunking=False  # Don't manually enable
            )
            
            # Check if chunking was auto-enabled
            if generator.enable_chunking:
                print("✓ PASS: Chunking auto-enabled for 350-word content")
                self.passed += 1
            else:
                print("✗ FAIL: Chunking NOT auto-enabled for 350-word content")
                self.failed += 1
            
            # Check content word count is stored
            if generator.content_word_count == 350:
                print("✓ PASS: Content word count correctly stored")
                self.passed += 1
            else:
                print("✗ FAIL: Content word count not correctly stored")
                self.failed += 1
                
        except Exception as e:
            print(f"✗ FAIL: Generator initialization raised exception: {str(e)}")
            self.failed += 1
    
    def run_all_tests(self):
        """Run all tests and print summary"""
        self.test_word_count_detection()
        self.test_chunk_content_preservation()
        self.test_chunk_json_compiler()
        self.test_json_validation()
        self.test_generator_auto_activation()
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        total = self.passed + self.failed
        print(f"Tests Passed: {self.passed}/{total}")
        print(f"Tests Failed: {self.failed}/{total}")
        
        if self.failed == 0:
            print("\n✓ ALL TESTS PASSED - Auto-chunking implementation verified!")
        else:
            print(f"\n✗ {self.failed} test(s) failed - review implementation")
        
        return self.failed == 0


if __name__ == "__main__":
    print("\n" + "="*80)
    print("AUTOMATIC CONTENT CHUNKING TEST SUITE")
    print("="*80)
    
    tester = TestAutomaticChunking()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)
