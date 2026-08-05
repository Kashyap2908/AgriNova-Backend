from django.urls import path
from recommendation.views import (
    PredictCropView,
    AvailableCropsView,
    RecommendationHistoryListView,
    RecommendationHistoryDetailView,
    YieldSummaryView
)

urlpatterns = [
    path('predict/', PredictCropView.as_view(), name='predict-crop'),
    path('crops/<int:farm_id>/', AvailableCropsView.as_view(), name='available-crops'),
    path('history/', RecommendationHistoryListView.as_view(), name='recommendation-history-list'),
    path('history/<int:pk>/', RecommendationHistoryDetailView.as_view(), name='recommendation-history-detail'),
    path('yield-summary/', YieldSummaryView.as_view(), name='yield-summary'),
]
