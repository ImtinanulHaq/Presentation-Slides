from django.contrib import admin
from .models import Presentation, Slide


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'presentation', 'order', 'created_at']
    list_filter = ['presentation', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
