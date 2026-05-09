import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error format:
    {
        "error": "Human-readable message",
        "detail": "Technical detail",
        "code": "error_code"
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': 'An error occurred',
            'detail': response.data,
            'status_code': response.status_code,
        }

        # Flatten single string details
        if isinstance(response.data, dict) and 'detail' in response.data:
            error_data['error'] = str(response.data['detail'])
            error_data['detail'] = response.data

        response.data = error_data
    else:
        # Unhandled exception - log it
        logger.error(f"Unhandled exception in {context.get('view')}: {exc}", exc_info=True)
        response = Response(
            {
                'error': 'Internal server error',
                'detail': 'An unexpected error occurred. Please try again.',
                'status_code': 500,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response