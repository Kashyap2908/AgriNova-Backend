from django.urls import path
from .views import ProfitAnalysisView

app_name = 'profit_analysis'

urlpatterns = [
    path('', ProfitAnalysisView.as_view(), name='profit-analysis'),
]
