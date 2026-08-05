from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'farm', 'title', 'language_code', 'is_weekly_report', 'created_at', 'updated_at')
    list_filter = ('is_weekly_report', 'language_code', 'created_at')
    search_fields = ('title', 'user__username', 'user__email')
    inlines = [MessageInline]
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'conversation__id')
    readonly_fields = ('created_at',)
