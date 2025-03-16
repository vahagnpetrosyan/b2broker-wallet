from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None and isinstance(exc, ValidationError):
        error_detail = exc.message_dict if hasattr(exc, "message_dict") else str(exc)
        response = Response({"errors": error_detail}, status=status.HTTP_400_BAD_REQUEST)

    return response
