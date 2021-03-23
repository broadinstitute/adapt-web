from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status as httpstatus


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # If the status code is 404, edit error message
    if hasattr(response, 'status_code') and response.status_code == 404:
        return Response({'Not Found': 'Please double check your input.'}, status=httpstatus.HTTP_404_NOT_FOUND)
        response.data['status_code'] = response.status_code

    return response
