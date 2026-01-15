"""
Custom exception handling for presentation app
Provides professional error responses for API clients
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for REST framework.
    
    Handles:
    - Broken pipe errors (client disconnected)
    - Timeout errors
    - Connection errors
    - Standard REST exceptions
    """
    
    # Log the exception
    logger.error(
        f"Exception in {context.get('view', 'Unknown')}: {str(exc)}",
        exc_info=True
    )
    
    # Get the standard exception response
    response = exception_handler(exc, context)
    
    # Handle broken pipe and connection errors gracefully
    if isinstance(exc, (BrokenPipeError, ConnectionResetError, ConnectionError)):
        logger.warning("Client disconnected before response sent")
        # Don't send a response for broken pipe - client is gone
        return None
    
    # Handle timeout errors
    if isinstance(exc, TimeoutError):
        return Response(
            {'error': 'Request timeout. The operation took too long. Please try again.'},
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )
    
    # If response is None, create a generic 500 response
    if response is None:
        logger.error(f"Unhandled exception type: {type(exc).__name__}")
        return Response(
            {'error': 'An unexpected error occurred. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Add custom data to response
    if status.is_client_error(response.status_code):
        response.data['error_type'] = 'client_error'
    elif status.is_server_error(response.status_code):
        response.data['error_type'] = 'server_error'
    
    return response
