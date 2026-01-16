from rest_framework import serializers
from .models import Presentation, Slide
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class SlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slide
        fields = [
            'id', 'slide_number', 'slide_type', 'title', 'subtitle',
            'content', 'bullets', 'visuals', 'speaker_notes',
            'order', 'created_at', 'updated_at', 'fonts'
        ]


class PresentationSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    slides = SlideSerializer(many=True, read_only=True)
    total_slides = serializers.SerializerMethodField()

    class Meta:
        model = Presentation
        fields = [
            'id', 'title', 'topic', 'raw_content', 'target_audience',
            'tone', 'subject', 'title_font', 'heading_font', 'content_font',
            'bullet_style', 'template', 'slide_ratio', 'description', 'json_structure', 'slides',
            'total_slides', 'created_by', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'json_structure', 'slides', 'title_font', 'heading_font', 'content_font', 'template', 'slide_ratio', 'bullet_style']

    def get_total_slides(self, obj):
        return obj.slides.count()

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PresentationGenerateSerializer(serializers.Serializer):
    """Serializer for presentation generation request"""
    topic = serializers.CharField(max_length=255, required=True)
    raw_content = serializers.CharField(required=True)
    target_audience = serializers.CharField(max_length=255, required=True)
    tone = serializers.ChoiceField(
        choices=['professional', 'casual', 'academic', 'persuasive'],
        required=True
    )
    subject = serializers.ChoiceField(
        choices=['general', 'english', 'urdu', 'science', 'biology', 'physics', 'medical', 'it', 'engineering'],
        required=False,
        default='general'
    )
    presentation_title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    num_slides = serializers.IntegerField(required=False, allow_null=True, min_value=3, max_value=100)
    enable_chunking = serializers.BooleanField(required=False, default=False)
    enable_visuals = serializers.BooleanField(required=False, default=True)
    template = serializers.CharField(max_length=50, required=False, default='warm_blue')
    slide_ratio = serializers.CharField(max_length=10, required=False, default='16:9')
    bullet_style = serializers.ChoiceField(
        choices=['numbered', 'bullet_elegant', 'bullet_modern', 'bullet_professional'],
        required=False,
        default='numbered'
    )
    
    def validate_num_slides(self, value):
        """Handle num_slides validation and conversion"""
        if value is None or value == '' or value == 'null':
            return None
        if isinstance(value, str):
            try:
                return int(value) if value.strip() else None
            except (ValueError, AttributeError):
                return None
        return value
