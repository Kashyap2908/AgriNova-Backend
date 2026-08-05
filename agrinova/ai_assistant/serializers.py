from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'metadata', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'farm', 'title', 'language_code', 'is_weekly_report', 'created_at', 'updated_at']

class ConversationDetailSerializer(ConversationSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']

class ChatRequestSerializer(serializers.Serializer):
    farm_id = serializers.IntegerField(required=False, allow_null=True)
    conversation_id = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(required=True, min_length=1)

class ConversationRenameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['title']
        extra_kwargs = {
            'title': {'required': True, 'allow_blank': False}
        }
