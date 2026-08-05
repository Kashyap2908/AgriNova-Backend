from django.urls import path
from .views import ChatAPIView, ConversationListView, ConversationDetailView

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='assistant-chat'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
]
