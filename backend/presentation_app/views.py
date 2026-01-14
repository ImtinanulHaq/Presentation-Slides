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
        """Generate presentation from raw content using Groq API"""
        
        try:
            serializer = PresentationGenerateSerializer(data=request.data)
            if not serializer.is_valid():
                print(f"[DEBUG] Validation errors: {serializer.errors}")
                print(f"[DEBUG] Request data: {request.data}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"[ERROR] Serializer validation exception: {str(e)}")
            return Response(
                {'error': f'Serializer error: {str(e)}'},
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
            enable_chunking = serializer.validated_data.get('enable_chunking', False)  # Enable for large content
            enable_visuals = serializer.validated_data.get('enable_visuals', True)  # Enable visual suggestions
            
            # Convert num_slides to int if provided
            if num_slides:
                try:
                    num_slides = int(num_slides)
                except (ValueError, TypeError):
                    num_slides = None
            
            # Generate presentation structure using Groq API
            generator = GroqPresentationGenerator(
                topic=topic,
                raw_content=raw_content,
                target_audience=target_audience,
                tone=tone,
                num_slides=num_slides,  # Pass user-specified slide count
                enable_chunking=enable_chunking,  # Enable chunking for large content
                enable_visuals=enable_visuals,  # Enable visual suggestions
            )
            json_structure = generator.generate()
            
            # Use provided title or generated title
            if not presentation_title:
                presentation_title = json_structure['presentation_title']
            
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
            for slide_data in json_structure['slides']:
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
            
            # Serialize and return
            serializer = PresentationSerializer(presentation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
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

