"""
URL configuration for presentation_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from presentation_app.health_checks import health_check_detailed, quick_health

urlpatterns = [
    # Health check endpoints
    path('', quick_health, name='health-check'),
    path('health/', health_check_detailed, name='health-detailed'),
    path('health/status/', quick_health, name='health-status'),
    
    # Admin and API docs
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API routes
    path('api/', include('presentation_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
