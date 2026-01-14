from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PresentationViewSet, SlideViewSet

router = DefaultRouter()
router.register(r'presentations', PresentationViewSet, basename='presentation')
router.register(r'slides', SlideViewSet, basename='slide')

urlpatterns = [
    path('', include(router.urls)),
]
