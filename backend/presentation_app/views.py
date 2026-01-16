from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http import FileResponse
from .models import Presentation, Slide
from .serializers import PresentationSerializer, SlideSerializer, PresentationGenerateSerializer
from .presentation_generator import GroqPresentationGenerator
from .script_generator import GroqScriptGenerator
from .pptx_generator import generate_pptx
import json
import logging
import traceback

logger = logging.getLogger(__name__)


class PresentationViewSet(viewsets.ModelViewSet):
    """ViewSet for Presentation CRUD operations"""
    queryset = Presentation.objects.all()
    serializer_class = PresentationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Presentation.objects.filter(created_by=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def generate(self, request):
        """Generate presentation from raw content using Groq API
        
        AUTOMATIC FEATURES (no user interaction needed):
        - Auto-chunks content >= 300 words for intelligent processing
        - Preserves context and logical flow during chunking
        - Generates professional slides from each chunk
        - Compiles chunk data into unified JSON format
        - Validates output for PPTX compatibility
        
        User can optionally specify num_slides for fixed slide count,
        which disables auto-chunking to ensure slide count accuracy.
        """
        
        try:
            # Validate request data
            serializer = PresentationGenerateSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Serializer validation failed: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Invalid request data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Extract data
            topic = serializer.validated_data['topic']
            raw_content = serializer.validated_data['raw_content']
            target_audience = serializer.validated_data['target_audience']
            tone = serializer.validated_data['tone']
            subject = serializer.validated_data.get('subject', 'general')
            presentation_title = serializer.validated_data.get('presentation_title', '')
            num_slides = serializer.validated_data.get('num_slides')
            enable_chunking = serializer.validated_data.get('enable_chunking', False)
            enable_visuals = serializer.validated_data.get('enable_visuals', True)
            template = serializer.validated_data.get('template', 'rose_elegance')  # Get template choice
            slide_ratio = serializer.validated_data.get('slide_ratio', '16:9')  # Get slide ratio
            bullet_style = serializer.validated_data.get('bullet_style', 'numbered')  # Get bullet style
            
            # Validate and log bullet_style
            valid_bullet_styles = ['numbered', 'bullet_elegant', 'bullet_modern', 'bullet_professional']
            if bullet_style not in valid_bullet_styles:
                logger.warning(f"⚠️ Invalid bullet_style='{bullet_style}', resetting to 'numbered'")
                bullet_style = 'numbered'
            
            logger.info(f"✅ Extracted from request: bullet_style='{bullet_style}' (valid={bullet_style in valid_bullet_styles}), template='{template}', slide_ratio='{slide_ratio}'")
            # Convert num_slides to int if provided
            if num_slides:
                try:
                    num_slides = int(num_slides)
                except (ValueError, TypeError):
                    num_slides = None
            
            # Log input for monitoring
            content_word_count = len(raw_content.split())
            logger.info(f"Presentation request: topic={topic}, template={template}, subject={subject}, words={content_word_count}, audience={target_audience}, tone={tone}")
            
            try:
                # Generate presentation structure using Groq API
                # Auto-chunking will activate automatically for 300+ words
                generator = GroqPresentationGenerator(
                    topic=topic,
                    raw_content=raw_content,
                    target_audience=target_audience,
                    tone=tone,
                    subject=subject,  # New subject parameter for specialized formatting
                    num_slides=num_slides,  # Pass user-specified slide count (disables auto-chunking)
                    enable_chunking=enable_chunking,  # Optional manual override
                    enable_visuals=enable_visuals,  # Enable visual suggestions
                    bullet_style=bullet_style,  # Pass bullet style to LLM

                )
                
                # Generate presentation with automatic chunking if applicable
                json_structure = generator.generate()
                
                # Validate json_structure is a dictionary
                if not isinstance(json_structure, dict):
                    logger.error(f"Invalid json_structure type: {type(json_structure)}, expected dict")
                    return Response(
                        {'error': 'Invalid presentation structure generated'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Extract slides list early for logging and validation
                slides_list = json_structure.get('slides', [])
                
                # Validate slides is a list
                if not isinstance(slides_list, list):
                    logger.error(f"Invalid slides type: {type(slides_list)}, expected list")
                    return Response(
                        {'error': 'Invalid slides structure in presentation'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Log generation metadata
                if json_structure.get('metadata', {}).get('generated_with_chunking'):
                    num_chunks = json_structure['metadata'].get('number_of_chunks', 0)
                    logger.info(f"Chunking applied: {num_chunks} chunks, {len(slides_list)} slides in structure")
                else:
                    logger.info(f"Single request processing: {len(slides_list)} slides generated")
            
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Connection error during generation: {str(e)}")
                return Response(
                    {'error': 'Backend service temporarily unavailable. Please try again.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            except Exception as e:
                error_details = f"{type(e).__name__}: {str(e)}"
                logger.error(f"Presentation generation error: {error_details}", exc_info=True)
                return Response(
                    {'error': f'Failed to generate presentation', 'details': error_details},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use provided title or generated title
            if not presentation_title:
                presentation_title = json_structure.get('presentation_title', 'Untitled Presentation')
            
            try:
                # Create presentation object
                presentation = Presentation.objects.create(
                    title=presentation_title,
                    topic=topic,
                    raw_content=raw_content,
                    target_audience=target_audience,
                    tone=tone,
                    subject=subject,
                    template=template,  # Store selected template
                    slide_ratio=slide_ratio,  # Store selected slide ratio
                    bullet_style=bullet_style,  # Store selected bullet style
                    json_structure=json_structure,
                    created_by=request.user,
                )
                
                # Immediately verify what was actually saved to the database
                saved_value = presentation.bullet_style
                logger.info(f"💾 VERIFICATION: Tried to save bullet_style='{bullet_style}', actually saved='{saved_value}' (equal={bullet_style == saved_value})")
                logger.info(f"📝 Verification: DB read-back shows bullet_style='{presentation.bullet_style}', template='{presentation.template}', slide_ratio='{presentation.slide_ratio}'")
                
                # Create slide objects from JSON structure
                slides_created = 0
                
                # Process each slide from the structure
                
                for slide_data in slides_list:
                    try:
                        # Handle both 'visuals' and 'slide_visuals' keys from LLM response
                        visuals = slide_data.get('visuals') or slide_data.get('slide_visuals', {})
                        fonts = slide_data.get('fonts', {})  # Get font configuration from slide
                        
                        # Determine slide_type with intelligent fallback
                        slide_type = slide_data.get('slide_type')
                        if not slide_type:
                            # Infer slide_type if missing
                            slide_number = slide_data.get('slide_number', 1)
                            if slide_number == 1:
                                slide_type = 'title'  # First slide is usually title
                            elif slide_data.get('title') and not slide_data.get('bullets'):
                                slide_type = 'section'  # Section slides typically have no bullets
                            else:
                                slide_type = 'content'  # Default to content
                        
                        Slide.objects.create(
                            presentation=presentation,
                            slide_number=slide_data.get('slide_number', slides_created + 1),
                            slide_type=slide_type,
                            title=slide_data.get('title', f'Slide {slides_created + 1}'),
                            subtitle=slide_data.get('subtitle', ''),
                            bullets=slide_data.get('bullets', []),
                            visuals=visuals,
                            fonts=fonts,  # Store font configuration
                            speaker_notes=slide_data.get('speaker_notes', ''),
                            order=slide_data.get('slide_number', slides_created + 1),
                        )
                        slides_created += 1
                    except Exception as slide_error:
                        logger.warning(f"Failed to create slide {slide_data.get('slide_number')}: {str(slide_error)}")
                        continue
                
                # Store fonts in presentation object
                font_config = getattr(generator, 'font_config', {})
                presentation.title_font = font_config.get('title', 'Calibri') if isinstance(font_config, dict) else 'Calibri'
                presentation.heading_font = font_config.get('heading', 'Calibri') if isinstance(font_config, dict) else 'Calibri'
                presentation.content_font = font_config.get('content', 'Arial') if isinstance(font_config, dict) else 'Arial'
                presentation.subject = subject  # Store the selected subject
                presentation.save()
                
                logger.info(f"Presentation created: ID={presentation.id}, slides={slides_created}, subject={subject}, fonts={presentation.title_font}, {presentation.heading_font}, {presentation.content_font}")
                
                # Serialize and return
                serializer = PresentationSerializer(presentation)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except Exception as db_error:
                logger.error(f"Database error: {str(db_error)}", exc_info=True)
                return Response(
                    {'error': 'Failed to save presentation'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        presentation = self.get_object()
        presentation.is_published = True
        presentation.save()
        return Response({'status': 'Presentation published'})

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        presentation = self.get_object()
        presentation.is_published = False
        presentation.save()
        return Response({'status': 'Presentation unpublished'})

    @action(detail=True, methods=['get'])
    def json_structure(self, request, pk=None):
        """Return just the JSON structure"""
        presentation = self.get_object()
        return Response(presentation.json_structure)

    @action(detail=True, methods=['get'])
    def export_pptx(self, request, pk=None):
        """Export presentation as PPTX file"""
        presentation = self.get_object()
        try:
            # Get template from presentation or use default
            template_name = presentation.template or 'rose_elegance'
            
            # Get slide ratio from query params, presentation settings, or use default
            slide_ratio = request.query_params.get('slide_ratio', presentation.slide_ratio or '16:9')
            
            # Get bullet style from presentation - CRITICAL: This must match what was stored during creation
            bullet_style = presentation.bullet_style
            # Handle empty or None values
            if not bullet_style or bullet_style.strip() == '':
                bullet_style = 'numbered'
                logger.warning(f"⚠️ bullet_style was empty/None, defaulting to 'numbered'")
            
            logger.info(f"📋 export_pptx: presentation.bullet_style from DB = '{bullet_style}'")
            logger.info(f"📋 export_pptx: All DB fields - id={presentation.id}, template='{presentation.template}', slide_ratio='{presentation.slide_ratio}', bullet_style='{bullet_style}'")
            
            # Validate slide ratio
            if slide_ratio not in ['16:9', '4:3', '1:1', '2:3']:
                slide_ratio = '16:9'
            
            logger.info(f"🚀 export_pptx calling generate_pptx: template={template_name}, slide_ratio={slide_ratio}, bullet_style={bullet_style}")
            pptx_file = generate_pptx(presentation, template_name=template_name, slide_ratio=slide_ratio, bullet_style=bullet_style)
            filename = f"{presentation.title.replace(' ', '_')}.pptx"
            return FileResponse(
                pptx_file,
                as_attachment=True,
                filename=filename,
                content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
            )
        except Exception as e:
            logger.error(f"PPTX export failed for presentation {presentation.id}: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to generate PPTX: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def generate_script(self, request, pk=None):
        """Generate speaker script for presentation slides
        
        POST data:
        {
            "total_duration": <minutes>,  # Total presentation duration in minutes
            "selected_slides": [1, 2, 3],  # Optional: specific slide numbers to generate script for
        }
        """
        presentation = self.get_object()
        
        try:
            # Get request parameters
            total_duration = request.data.get('total_duration')
            selected_slides = request.data.get('selected_slides', [])
            
            # Validate duration
            if not total_duration:
                return Response(
                    {'error': 'total_duration is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                total_duration = float(total_duration)
                if total_duration <= 0:
                    return Response(
                        {'error': 'total_duration must be greater than 0'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'total_duration must be a valid number'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get presentation slides
            all_slides = presentation.slides.all().order_by('slide_number')
            
            # Filter slides if specific ones were selected
            if selected_slides:
                slides_to_process = all_slides.filter(slide_number__in=selected_slides)
            else:
                slides_to_process = all_slides
            
            if not slides_to_process.exists():
                return Response(
                    {'error': 'No slides found in presentation'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convert slide objects to dictionaries for script generator
            slides_data = []
            for slide in slides_to_process:
                slide_dict = {
                    'slide_number': slide.slide_number,
                    'title': slide.title,
                    'subtitle': slide.subtitle,
                    'content': slide.content,
                    'bullets': slide.bullets or [],
                }
                slides_data.append(slide_dict)
            
            logger.info(f"Generating script for presentation {presentation.id}: {len(slides_data)} slides, {total_duration} minutes")
            
            # Generate script using Groq
            try:
                script_generator = GroqScriptGenerator()
                result = script_generator.generate_script_for_slides(
                    slides=slides_data,
                    presentation_tone=presentation.tone,
                    total_duration=total_duration,
                    presentation_title=presentation.title
                )
                
                if result['success']:
                    logger.info(f"✅ Script generated successfully for presentation {presentation.id}")
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    logger.error(f"Script generation failed: {result.get('error')}")
                    return Response(
                        {'error': f"Failed to generate script: {result.get('error')}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            except Exception as e:
                logger.error(f"Error in script generation: {str(e)}", exc_info=True)
                return Response(
                    {'error': f'Script generation failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            logger.error(f"Error processing script request: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Request processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def generate_single_slide_script(self, request, pk=None):
        """Generate script for a single slide
        
        POST data:
        {
            "slide_id": <slide_id>,
            "slide_duration": <minutes>,  # Duration for this specific slide
        }
        """
        presentation = self.get_object()
        
        try:
            # Get request parameters
            slide_id = request.data.get('slide_id')
            slide_duration = request.data.get('slide_duration')
            
            if not slide_id or not slide_duration:
                return Response(
                    {'error': 'slide_id and slide_duration are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                slide_duration = float(slide_duration)
                if slide_duration <= 0:
                    return Response(
                        {'error': 'slide_duration must be greater than 0'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'slide_duration must be a valid number'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the slide
            try:
                slide = presentation.slides.get(id=slide_id)
            except Slide.DoesNotExist:
                return Response(
                    {'error': 'Slide not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get adjacent slides for context
            previous_slide = presentation.slides.filter(slide_number__lt=slide.slide_number).order_by('-slide_number').first()
            next_slide = presentation.slides.filter(slide_number__gt=slide.slide_number).order_by('slide_number').first()
            
            slide_data = {
                'title': slide.title,
                'subtitle': slide.subtitle,
                'content': slide.content,
                'bullets': slide.bullets or [],
            }
            
            logger.info(f"Generating script for slide {slide.id} in presentation {presentation.id}")
            
            try:
                script_generator = GroqScriptGenerator()
                result = script_generator.generate_script_for_single_slide(
                    slide=slide_data,
                    presentation_tone=presentation.tone,
                    slide_duration=slide_duration,
                    presentation_title=presentation.title,
                    previous_slide_title=previous_slide.title if previous_slide else "Opening",
                    next_slide_title=next_slide.title if next_slide else "Closing"
                )
                
                if result['success']:
                    logger.info(f"✅ Single slide script generated successfully for slide {slide.id}")
                    return Response(result['script'], status=status.HTTP_200_OK)
                else:
                    logger.error(f"Single slide script generation failed: {result.get('error')}")
                    return Response(
                        {'error': f"Failed to generate script: {result.get('error')}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            except Exception as e:
                logger.error(f"Error in single slide script generation: {str(e)}", exc_info=True)
                return Response(
                    {'error': f'Script generation failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            logger.error(f"Error processing single slide script request: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Request processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SlideViewSet(viewsets.ModelViewSet):
    """ViewSet for Slide CRUD operations"""
    queryset = Slide.objects.all()
    serializer_class = SlideSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        presentation_id = self.request.query_params.get('presentation_id')
        if presentation_id:
            return Slide.objects.filter(presentation_id=presentation_id).order_by('slide_number')
        return Slide.objects.all()

