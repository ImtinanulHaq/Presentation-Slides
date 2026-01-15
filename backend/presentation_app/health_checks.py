"""
Health check views for monitoring system status
"""
from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError
import logging
from decouple import config

logger = logging.getLogger(__name__)


def database_health():
    """Check database connectivity"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True, "Connected"
    except OperationalError as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False, str(e)


def groq_api_health():
    """Check Groq API key configuration"""
    try:
        groq_key = config('GROQ_API_KEY', default='')
        if not groq_key:
            return False, "GROQ_API_KEY not configured"
        if groq_key.startswith('gsk_'):
            return True, "Configured"
        return False, "Invalid API key format"
    except Exception as e:
        return False, str(e)


def health_check_detailed(request):
    """Comprehensive health check endpoint"""
    db_ok, db_msg = database_health()
    groq_ok, groq_msg = groq_api_health()
    
    status = 'ok' if (db_ok and groq_ok) else 'degraded'
    
    return JsonResponse({
        'status': status,
        'message': 'Presentation Slides API',
        'version': '1.0',
        'checks': {
            'database': {
                'status': 'ok' if db_ok else 'error',
                'message': db_msg
            },
            'groq_api': {
                'status': 'ok' if groq_ok else 'warning',
                'message': groq_msg
            },
            'api_server': {
                'status': 'ok',
                'message': 'Running'
            }
        }
    })


def quick_health(request):
    """Quick health check for Render monitoring"""
    return JsonResponse({
        'status': 'ok',
        'message': 'API is running'
    })
