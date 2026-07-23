from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileAPIView, 
    FarmViewSet, 
    SelectFarmAPIView, 
    DashboardAPIView
)

app_name = 'farms'

router = DefaultRouter()
router.register('farms', FarmViewSet, basename='farm')

urlpatterns = [
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('farms/select/<int:pk>/', SelectFarmAPIView.as_view(), name='farm-select'),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]
