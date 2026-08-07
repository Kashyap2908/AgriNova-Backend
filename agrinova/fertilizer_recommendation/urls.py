from django.urls import path
from .views import (
    CropNutritionPlanView,
    FertilizerRecommendView,
    FertilizerHistoryListView,
    FertilizerHistoryDetailView,
    FertilizerMasterListView,
    CropListView,
)

urlpatterns = [
    path('plan/', CropNutritionPlanView.as_view(), name='fertilizer-plan'),
    path('recommend/', FertilizerRecommendView.as_view(), name='fertilizer-recommend'),
    path('history/', FertilizerHistoryListView.as_view(), name='fertilizer-history'),
    path('history/<int:pk>/', FertilizerHistoryDetailView.as_view(), name='fertilizer-history-detail'),
    path('master/', FertilizerMasterListView.as_view(), name='fertilizer-master'),
    path('crops/', CropListView.as_view(), name='fertilizer-crops'),
]
