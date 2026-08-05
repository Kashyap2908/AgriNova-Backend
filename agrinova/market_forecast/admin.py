from django.contrib import admin
from .models import MarketForecastHistory,MarketCache
# Register your models here.
admin.site.register(MarketForecastHistory)
admin.site.register(MarketCache)