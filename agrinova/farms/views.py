from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.db import transaction
from authenticate.services import success_response

from .models import FarmerProfile, Farm
from .serializers import (
    FarmerProfileSerializer, 
    FarmSerializer, 
    DashboardSerializer
)

class ProfileAPIView(APIView):
    """
    API view to retrieve, create, or update the authenticated farmer's profile.
    GET /api/profile/
    POST / PUT / PATCH /api/profile/
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        profile, created = FarmerProfile.objects.get_or_create(user=request.user)
        serializer = FarmerProfileSerializer(profile, context={'request': request})
        return success_response(
            data=serializer.data,
            message="User profile retrieved successfully"
        )

    def post(self, request):
        return self.update_profile(request)

    def put(self, request):
        return self.update_profile(request)

    def patch(self, request):
        return self.update_profile(request)

    def update_profile(self, request):
        profile, created = FarmerProfile.objects.get_or_create(user=request.user)
        serializer = FarmerProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(
            data=serializer.data,
            message="Profile saved successfully",
            status_code=status.HTTP_200_OK if not created else status.HTTP_201_CREATED
        )


class FarmViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Farm records.
    Scoped strictly to request.user.
    GET /api/farms/
    POST /api/farms/
    PUT /api/farms/<id>/
    DELETE /api/farms/<id>/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FarmSerializer

    def get_queryset(self):
        return Farm.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data=serializer.data,
            message="Farms retrieved successfully"
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message="Farm details retrieved successfully"
        )

    def perform_create(self, serializer):
        user_farms_count = Farm.objects.filter(user=self.request.user).count()
        # Automatically make active if it's the user's first farm
        is_first = (user_farms_count == 0)
        serializer.save(user=self.request.user, is_active=is_first)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message="Farm registered successfully",
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Farm updated successfully"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        was_active = instance.is_active
        instance.delete()

        # If deleted farm was active, activate another farm if available
        if was_active:
            next_farm = Farm.objects.filter(user=request.user).first()
            if next_farm:
                next_farm.is_active = True
                next_farm.save()

        return success_response(
            message="Farm deleted successfully",
            status_code=status.HTTP_200_OK
        )


class SelectFarmAPIView(APIView):
    """
    Endpoint to activate a specific farm while deactivating all other farms for the user.
    POST /api/farms/select/<int:pk>/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            target_farm = Farm.objects.get(pk=pk, user=request.user)
        except Farm.DoesNotExist:
            return Response({
                "success": False,
                "message": "Farm not found or does not belong to user.",
                "errors": {"id": ["Invalid farm ID."]}
            }, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            # Deactivate all farms belonging to this user
            Farm.objects.filter(user=request.user).update(is_active=False)
            # Activate selected farm
            target_farm.is_active = True
            target_farm.save()

        serializer = FarmSerializer(target_farm, context={'request': request})
        return success_response(
            data=serializer.data,
            message=f"Farm '{target_farm.farm_name}' selected as active farm."
        )


class DashboardAPIView(APIView):
    """
    Returns unified Dashboard payload containing user profile, active farm,
    total farms count, and onboarding completion status.
    GET /api/dashboard/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        
        # Get active selected farm or default to first farm
        selected_farm = Farm.objects.filter(user=user, is_active=True).first()
        if not selected_farm:
            selected_farm = Farm.objects.filter(user=user).first()
            if selected_farm:
                selected_farm.is_active = True
                selected_farm.save()

        total_farms = Farm.objects.filter(user=user).count()
        profile_completed = profile.profile_completed if profile else False

        dashboard_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "profile": FarmerProfileSerializer(profile, context={'request': request}).data if profile else None,
            "selected_farm": FarmSerializer(selected_farm, context={'request': request}).data if selected_farm else None,
            "total_farms": total_farms,
            "profile_completed": profile_completed
        }

        return success_response(
            data=dashboard_data,
            message="Dashboard summary retrieved successfully"
        )
