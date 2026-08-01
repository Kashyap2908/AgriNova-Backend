from django.urls import path
from recommendation.views import PredictCropView, RecommendationHistoryListView, RecommendationHistoryDetailView

urlpatterns = [
    path('predict/', PredictCropView.as_view(), name='predict_crop'),
    path('history/', RecommendationHistoryListView.as_view(), name='recommendation_history_list'),
    path('history/<int:pk>/', RecommendationHistoryDetailView.as_view(), name='recommendation_history_detail'),
]
