from django.urls import path
from .views import FertilizerRecommendView, FertilizerHistoryListView, FertilizerMasterListView

urlpatterns = [
    path('recommend/', FertilizerRecommendView.as_view(), name='fertilizer-recommend'),
    path('history/', FertilizerHistoryListView.as_view(), name='fertilizer-history'),
    path('master/', FertilizerMasterListView.as_view(), name='fertilizer-master'),
]
