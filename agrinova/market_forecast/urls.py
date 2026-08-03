from django.urls import path
from .views import MarketIntelligenceView, MarketForecastHistoryListView, MarketForecastHistoryDetailView, HistoricalExplorerView

app_name = 'market_forecast'

urlpatterns = [
    path('intelligence/', MarketIntelligenceView.as_view(), name='market-intelligence'),
    path('explorer/', HistoricalExplorerView.as_view(), name='historical-explorer'),
    path('history/', MarketForecastHistoryListView.as_view(), name='history-list'),
    path('history/<int:pk>/', MarketForecastHistoryDetailView.as_view(), name='market-forecast-history-detail'),
]
