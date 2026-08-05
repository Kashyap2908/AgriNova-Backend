from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .models import Conversation
from .serializers import ConversationSerializer, ConversationDetailSerializer, ChatRequestSerializer
from .services.assistant_service import process_message

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if serializer.is_valid():
            farm_id = serializer.validated_data.get('farm_id')
            conversation_id = serializer.validated_data.get('conversation_id')
            message = serializer.validated_data.get('message')
            
            response_payload = process_message(
                user=request.user,
                farm_id=farm_id,
                message_text=message,
                conversation_id=conversation_id
            )
            
            return Response(response_payload, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class ConversationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            from .serializers import ConversationRenameSerializer
            return ConversationRenameSerializer
        return ConversationDetailSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

