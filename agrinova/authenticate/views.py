from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    UserRegistrationSerializer, 
    LoginSerializer, 
    UserProfileSerializer
)
from .services import (
    get_tokens_for_user, 
    success_response
)

class RegisterAPIView(APIView):
    """
    Endpoint for new user registration.
    Accessible to everyone.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return registered user profile details
        profile_serializer = UserProfileSerializer(user)
        return success_response(
            data={"user": profile_serializer.data},
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED
        )


class LoginAPIView(APIView):
    """
    Endpoint for user authentication using Username/Email and Password.
    Returns access token, refresh token, and user details.
    Accessible to everyone.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        tokens = get_tokens_for_user(user)
        
        # Serialize user profile info
        profile_serializer = UserProfileSerializer(user)
        
        response_data = {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": profile_serializer.data
        }
        
        return success_response(
            data=response_data,
            message="Login successful",
            status_code=status.HTTP_200_OK
        )


class LogoutAPIView(APIView):
    """
    Endpoint to invalidate (blacklist) a user's refresh token.
    Accessible only to authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                "success": False,
                "message": "Refresh token is required to logout",
                "errors": {"refresh": ["This field is required."]}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response(
                message="Logout successful. Refresh token blacklisted."
            )
        except TokenError as e:
            # Handle expired or invalid token gracefully
            return Response({
                "success": False,
                "message": "Invalid or expired refresh token",
                "errors": {"refresh": [str(e)]}
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(APIView):
    """
    Endpoint to retrieve the current user's profile details.
    Accessible only to authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return success_response(
            data=serializer.data,
            message="User profile retrieved successfully"
        )
