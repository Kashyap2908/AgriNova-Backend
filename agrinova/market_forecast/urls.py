from django.urls import path
from .views import (
    MarketIntelligenceView, 
    MarketIntelligenceReportView,
    CropMarketPriceView, 
    MarketForecastHistoryListView, 
    MarketForecastHistoryDetailView, 
    HistoricalExplorerView
)

app_name = 'market_forecast'

urlpatterns = [
    path('intelligence/', MarketIntelligenceView.as_view(), name='market-intelligence'),
    path('report/', MarketIntelligenceReportView.as_view(), name='market-intelligence-report'),
    path('crop-price/', CropMarketPriceView.as_view(), name='crop-market-price'),
    path('explorer/', HistoricalExplorerView.as_view(), name='historical-explorer'),
    path('history/', MarketForecastHistoryListView.as_view(), name='history-list'),
    path('history/<int:pk>/', MarketForecastHistoryDetailView.as_view(), name='market-forecast-history-detail'),
]
