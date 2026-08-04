from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authenticate.urls')),
    path('api/', include('farms.urls')),
    path('api/recommendation/', include('recommendation.urls')),
    path('api/market-forecast/', include('market_forecast.urls')),
    path('api/disease/', include('disease_detection.urls')),
    path('api/assistant/', include('assistant.urls')),
    path('api/weather/', include('weather.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
