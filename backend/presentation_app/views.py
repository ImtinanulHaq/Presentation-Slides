from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http import FileResponse
from .models import Presentation, Slide
from .serializers import PresentationSerializer, SlideSerializer, PresentationGenerateSerializer
from .presentation_generator import GroqPresentationGenerator
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
            presentation_title = serializer.validated_data.get('presentation_title', '')
            num_slides = serializer.validated_data.get('num_slides')  # Optional user input
            enable_chunking = serializer.validated_data.get('enable_chunking', False)  # Optional override
            enable_visuals = serializer.validated_data.get('enable_visuals', True)  # Enable visual suggestions
            
            # Convert num_slides to int if provided
            if num_slides:
                try:
                    num_slides = int(num_slides)
                except (ValueError, TypeError):
                    num_slides = None
            
            # Log input for monitoring
            content_word_count = len(raw_content.split())
            logger.info(f"Presentation request: topic={topic}, words={content_word_count}, audience={target_audience}, tone={tone}")
            
            try:
                # Generate presentation structure using Groq API
                # Auto-chunking will activate automatically for 300+ words
                generator = GroqPresentationGenerator(
                    topic=topic,
                    raw_content=raw_content,
                    target_audience=target_audience,
                    tone=tone,
                    num_slides=num_slides,  # Pass user-specified slide count (disables auto-chunking)
                    enable_chunking=enable_chunking,  # Optional manual override
                    enable_visuals=enable_visuals,  # Enable visual suggestions
                )
                
                # Generate presentation with automatic chunking if applicable
                json_structure = generator.generate()
                
                # Log generation metadata
                if json_structure.get('metadata', {}).get('generated_with_chunking'):
                    num_chunks = json_structure['metadata'].get('number_of_chunks', 0)
                    logger.info(f"Chunking applied: {num_chunks} chunks, {json_structure['total_slides']} slides generated")
                else:
                    logger.info(f"Single request processing: {json_structure['total_slides']} slides generated")
            
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Connection error during generation: {str(e)}")
                return Response(
                    {'error': 'Backend service temporarily unavailable. Please try again.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            except Exception as e:
                logger.error(f"Presentation generation error: {str(e)}", exc_info=True)
                return Response(
                    {'error': f'Failed to generate presentation'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use provided title or generated title
            if not presentation_title:
                presentation_title = json_structure['presentation_title']
            
            try:
                # Create presentation object
                presentation = Presentation.objects.create(
                    title=presentation_title,
                    topic=topic,
                    raw_content=raw_content,
                    target_audience=target_audience,
                    tone=tone,
                    json_structure=json_structure,
                    created_by=request.user,
                )
                
                # Create slide objects from JSON structure
                slides_created = 0
                for slide_data in json_structure['slides']:
                    try:
                        # Handle both 'visuals' and 'slide_visuals' keys from LLM response
                        visuals = slide_data.get('visuals') or slide_data.get('slide_visuals', {})
                        
                        Slide.objects.create(
                            presentation=presentation,
                            slide_number=slide_data['slide_number'],
                            slide_type=slide_data['slide_type'],
                            title=slide_data['title'],
                            subtitle=slide_data.get('subtitle', ''),
                            bullets=slide_data.get('bullets', []),
                            visuals=visuals,
                            speaker_notes=slide_data.get('speaker_notes', ''),
                            order=slide_data['slide_number'],
                        )
                        slides_created += 1
                    except Exception as slide_error:
                        logger.warning(f"Failed to create slide {slide_data.get('slide_number')}: {str(slide_error)}")
                        continue
                
                logger.info(f"Presentation created: ID={presentation.id}, slides={slides_created}")
                
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
            pptx_file = generate_pptx(presentation)
            filename = f"{presentation.title.replace(' ', '_')}.pptx"
            return FileResponse(
                pptx_file,
                as_attachment=True,
                filename=filename,
                content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PPTX: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
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

