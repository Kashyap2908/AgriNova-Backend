from django.urls import path
from .views import (
    CropNutritionPlanView,
    FertilizerRecommendView,
    FertilizerHistoryListView,
    FertilizerMasterListView,
    CropListView,
)

urlpatterns = [
    path('plan/', CropNutritionPlanView.as_view(), name='fertilizer-plan'),
    path('recommend/', FertilizerRecommendView.as_view(), name='fertilizer-recommend'),
    path('history/', FertilizerHistoryListView.as_view(), name='fertilizer-history'),
    path('master/', FertilizerMasterListView.as_view(), name='fertilizer-master'),
    path('crops/', CropListView.as_view(), name='fertilizer-crops'),
]
