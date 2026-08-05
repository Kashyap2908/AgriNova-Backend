from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Notification
from .serializers import NotificationSerializer
from .services.generator import generate_smart_notifications

class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationMarkReadView(views.APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
            notif.is_read = True
            notif.save()
            return Response({'status': 'marked read'})
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class NotificationDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationMarkAllReadView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked read'})

class NotificationClearAllView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        Notification.objects.filter(user=request.user).delete()
        return Response({'status': 'all cleared'})

class NotificationGenerateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Trigger generation logic
        count = generate_smart_notifications(request.user)
        return Response({'status': 'generated', 'new_count': count})

class NotificationTestGenerateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .services.generator import generate_test_notification
        count = generate_test_notification(request.user)
        return Response({'status': 'test generated', 'new_count': count})
