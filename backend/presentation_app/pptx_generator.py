from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from io import BytesIO


def generate_pptx(presentation_obj):
    """
    Generate a PPTX file from a presentation object
    
    Args:
        presentation_obj: Presentation model instance
    
    Returns:
        BytesIO: PPTX file in memory
    """
    
    # Create presentation
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # Define color scheme
    TITLE_COLOR = RGBColor(0, 51, 102)  # Dark blue
    ACCENT_COLOR = RGBColor(0, 102, 204)  # Medium blue
    TEXT_COLOR = RGBColor(50, 50, 50)  # Dark gray
    
    # Get slides from presentation
    slides = presentation_obj.slides.all().order_by('slide_number')
    
    for slide_obj in slides:
        # Choose layout based on slide type
        if slide_obj.slide_type == 'title':
            # Title slide layout
            slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(slide_layout)
            
            # Add background
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = TITLE_COLOR
            
            # Add title
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(1.5))
            title_frame = title_box.text_frame
            title_frame.word_wrap = True
            p = title_frame.paragraphs[0]
            p.text = slide_obj.title or presentation_obj.title
            p.font.size = Pt(54)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            
            # Add subtitle
            if slide_obj.subtitle:
                subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9), Inches(1))
                subtitle_frame = subtitle_box.text_frame
                p = subtitle_frame.paragraphs[0]
                p.text = slide_obj.subtitle
                p.font.size = Pt(32)
                p.font.color.rgb = ACCENT_COLOR
                p.alignment = PP_ALIGN.CENTER
            
            # Add metadata
            meta_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(9), Inches(0.8))
            meta_frame = meta_box.text_frame
            p = meta_frame.paragraphs[0]
            p.text = f"{presentation_obj.topic} | Audience: {presentation_obj.target_audience}"
            p.font.size = Pt(14)
            p.font.color.rgb = RGBColor(200, 200, 200)
            p.alignment = PP_ALIGN.CENTER
            
        elif slide_obj.slide_type == 'section':
            # Section divider slide
            slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(slide_layout)
            
            # Add background
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = ACCENT_COLOR
            
            # Add title
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(3), Inches(9), Inches(1.5))
            title_frame = title_box.text_frame
            title_frame.word_wrap = True
            p = title_frame.paragraphs[0]
            p.text = slide_obj.title
            p.font.size = Pt(48)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            
        else:
            # Content slide layout
            slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(slide_layout)
            
            # Add white background
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(255, 255, 255)
            
            # Add title bar
            title_bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.8))
            title_bar.fill.solid()
            title_bar.fill.fore_color.rgb = TITLE_COLOR
            title_bar.line.color.rgb = TITLE_COLOR
            
            # Add title
            title_frame = title_bar.text_frame
            title_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = title_frame.paragraphs[0]
            p.text = slide_obj.title
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.LEFT
            title_frame.margin_left = Inches(0.3)
            
            # Add slide number at top right
            slide_num_box = slide.shapes.add_textbox(Inches(8.5), Inches(0.2), Inches(1.2), Inches(0.5))
            slide_num_frame = slide_num_box.text_frame
            p = slide_num_frame.paragraphs[0]
            p.text = f"Slide {slide_obj.slide_number}"
            p.font.size = Pt(10)
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.RIGHT
            
            # Add content
            content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(9), Inches(5.5))
            text_frame = content_box.text_frame
            text_frame.word_wrap = True
            
            # Add bullets
            if slide_obj.bullets:
                for i, bullet in enumerate(slide_obj.bullets):
                    if isinstance(bullet, dict):
                        bullet_text = bullet.get('text', '')
                        level = bullet.get('level', 0)
                    else:
                        bullet_text = str(bullet)
                        level = 0
                    
                    if i == 0:
                        p = text_frame.paragraphs[0]
                    else:
                        p = text_frame.add_paragraph()
                    
                    p.text = bullet_text
                    p.level = level
                    p.font.size = Pt(20 - (level * 2))
                    p.font.color.rgb = TEXT_COLOR
                    p.space_before = Pt(6)
                    p.space_after = Pt(6)
            
            # Add speaker notes if present
            if slide_obj.speaker_notes:
                notes_slide = slide.notes_slide
                text_frame = notes_slide.notes_text_frame
                text_frame.text = slide_obj.speaker_notes
    
    # Save to BytesIO
    output = BytesIO()
    prs.save(output)
    output.seek(0)
    return output
