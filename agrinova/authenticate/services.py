from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler

def get_tokens_for_user(user):
    """
    Generate refresh and access tokens for a given user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Format success responses consistently:
    {
        "success": true,
        "message": "...",
        "data": { ... }
    }
    """
    return Response({
        "success": True,
        "message": message,
        "data": data or {}
    }, status=status_code)

def custom_exception_handler(exc, context):
    """
    Custom exception handler to format error responses consistently:
    {
        "success": false,
        "message": "...",
        "errors": { ... }
    }
    """
    # Call REST framework's default exception handler first to get the standard response
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data
        message = "Validation failed"

        # Check for different types of error formats
        if isinstance(errors, dict):
            # If the error is a detail message (e.g. AuthenticationFailed, NotFound, PermissionDenied)
            if 'detail' in errors:
                message = errors['detail']
                # If 'detail' is the only key, clear the errors dict to not duplicate in response
                if len(errors) == 1:
                    errors = {}
            # Standard DRF validation error: check if there's a specific field validation message
            elif len(errors) > 0:
                first_key = list(errors.keys())[0]
                first_error = errors[first_key]
                if isinstance(first_error, list) and len(first_error) > 0:
                    if first_key == 'non_field_errors':
                        message = first_error[0]
                    else:
                        message = f"{first_key.replace('_', ' ').capitalize()}: {first_error[0]}"
                elif isinstance(first_error, str):
                    message = first_error

        elif isinstance(errors, list):
            # If it's a list (e.g., non_field_errors)
            if len(errors) > 0:
                message = errors[0]

        response.data = {
            "success": False,
            "message": message,
            "errors": errors if isinstance(errors, dict) and 'detail' not in errors else errors
        }
    else:
        # Fallback for general unhandled exceptions (server errors)
        response = Response({
            "success": False,
            "message": str(exc),
            "errors": {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
