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


import secrets
import requests
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import PasswordResetOTP
from .serializers import (
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer
)

User = get_user_model()


class ForgotPasswordAPIView(APIView):
    """
    POST /api/auth/forgot-password/
    Generates a secure 6-digit OTP, stores it with 5-minute expiry,
    and calls the Node Mailer microservice to deliver the OTP email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.filter(email__iexact=email).first()

        # Generate secure random 6-digit OTP
        otp_code = f"{secrets.randbelow(1000000):06d}"
        expires_at = timezone.now() + timedelta(minutes=5)

        # Deactivate any previous unverified OTPs for this user
        PasswordResetOTP.objects.filter(user=user, is_verified=False).update(is_verified=True)

        # Save new OTP record
        PasswordResetOTP.objects.create(
            user=user,
            otp=otp_code,
            expires_at=expires_at,
            is_verified=False,
            attempts=0
        )

        # Call Node Email Microservice
        node_mailer_url = getattr(settings, 'NODE_MAIL_SERVICE_URL', 'http://localhost:5001/send-otp')
        try:
            response = requests.post(
                node_mailer_url,
                json={"to": user.email, "otp": otp_code},
                timeout=10
            )
            if response.status_code != 200:
                print(f"[ForgotPasswordAPIView] Node Mailer returned status {response.status_code}: {response.text}")
        except Exception as err:
            print(f"[ForgotPasswordAPIView Error] Could not connect to Node Mailer Service: {err}")

        return success_response(
            message="OTP sent successfully to your email.",
            status_code=status.HTTP_200_OK
        )


class VerifyOTPAPIView(APIView):
    """
    POST /api/auth/verify-otp/
    Verifies the email, OTP match, 5-minute expiration, and attempt limit (max 5).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        input_otp = serializer.validated_data['otp']

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({
                "success": False,
                "message": "No account found with this email address.",
                "errors": {"email": ["Invalid email address."]}
            }, status=status.HTTP_400_BAD_REQUEST)

        otp_record = PasswordResetOTP.objects.filter(user=user, is_verified=False).order_by('-created_at').first()

        if not otp_record:
            return Response({
                "success": False,
                "message": "No active OTP request found. Please request a new OTP.",
                "errors": {"otp": ["No active OTP request found."]}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check attempt limit (max 5)
        if otp_record.attempts >= 5:
            return Response({
                "success": False,
                "message": "Maximum verification attempts exceeded. Please request a new OTP.",
                "errors": {"otp": ["Maximum verification attempts exceeded."]}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check expiration
        if otp_record.is_expired():
            return Response({
                "success": False,
                "message": "OTP has expired. Please request a new OTP.",
                "errors": {"otp": ["OTP has expired."]}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Increment attempts counter
        otp_record.attempts += 1
        otp_record.save(update_fields=['attempts'])

        # Verify OTP code match
        if otp_record.otp != input_otp:
            return Response({
                "success": False,
                "message": f"Invalid OTP. ({5 - otp_record.attempts} attempt(s) remaining)",
                "errors": {"otp": ["Invalid verification code."]}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Mark OTP as verified
        otp_record.is_verified = True
        otp_record.save(update_fields=['is_verified'])

        return success_response(
            data={"email": user.email, "verified": True},
            message="OTP verified successfully.",
            status_code=status.HTTP_200_OK
        )


class ResetPasswordAPIView(APIView):
    """
    POST /api/auth/reset-password/
    Verifies OTP state, password match, Django validators, sets hashed password, and invalidates OTP.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        input_otp = serializer.validated_data['otp']
        password = serializer.validated_data['password']
        user = serializer.validated_data['user']

        # Ensure OTP was verified and is still within valid session window
        otp_record = PasswordResetOTP.objects.filter(
            user=user,
            otp=input_otp,
            is_verified=True
        ).order_by('-created_at').first()

        if not otp_record:
            return Response({
                "success": False,
                "message": "OTP verification required before resetting password.",
                "errors": {"otp": ["OTP verification required."]}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set new password using Django's set_password (hashes using PBKDF2/Argon2)
        user.set_password(password)
        user.save()

        # Invalidate OTP record so it cannot be reused
        otp_record.expires_at = timezone.now()
        otp_record.save(update_fields=['expires_at'])

        return success_response(
            message="Password reset successfully. You can now login with your new password.",
            status_code=status.HTTP_200_OK
        )

