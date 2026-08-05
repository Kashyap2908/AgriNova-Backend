from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationDeleteView,
    NotificationMarkAllReadView,
    NotificationClearAllView,
    NotificationGenerateView,
    NotificationTestGenerateView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('<int:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('clear-all/', NotificationClearAllView.as_view(), name='notification-clear-all'),
    path('generate/', NotificationGenerateView.as_view(), name='notification-generate'),
    path('test-generate/', NotificationTestGenerateView.as_view(), name='notification-test-generate'),
]
