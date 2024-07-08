# exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'status': 'error',
            'message': 'An error occurred',
            'statusCode': response.status_code,
            'errors': []
        }

        for field, value in response.data.items():
            custom_response_data['errors'].append({
                'field': field,
                'message': value[0] if isinstance(value, list) else value
            })

        response.data = custom_response_data

    return response