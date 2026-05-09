import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': 'An error occurred',
            'detail': response.data,
            'status_code': response.status_code,
        }
        if isinstance(response.data, dict) and 'detail' in response.data:
            error_data['error'] = str(response.data['detail'])
        response.data = error_data
    else:
        logger.error(
            f"Unhandled exception in {context.get('view')}: {exc}",
            exc_info=True
        )
        response = Response(
            {
                'error': 'Internal server error',
                'detail': 'An unexpected error occurred. Please try again.',
                'status_code': 500,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response