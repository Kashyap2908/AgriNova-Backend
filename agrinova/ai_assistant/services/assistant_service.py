from django.shortcuts import get_object_or_404
from ai_assistant.models import Conversation, Message
from ai_assistant.services.context_builder import build_farm_context
from ai_assistant.services.prompt_builder import get_system_prompt, wrap_user_message
from ai_assistant.services.groq_client import query_groq_llm
import logging

logger = logging.getLogger(__name__)

def process_message(user, farm_id, message_text, conversation_id=None):
    # 1. Fetch or create Conversation
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=user)
    else:
        title = message_text[:50] + "..." if len(message_text) > 50 else message_text
        conversation = Conversation.objects.create(user=user, farm_id=farm_id, title=title)
    
    # 2. Save user message
    Message.objects.create(
        conversation=conversation,
        role='user',
        content=message_text
    )
    
    # 3. Get recent history (last 10 messages)
    recent_messages = list(conversation.messages.order_by('-created_at')[:10])
    recent_messages.reverse()
    
    # 4. Get Context & System Prompt
    farm_context = build_farm_context(user, farm_id)
    system_prompt = get_system_prompt(farm_context)
    
    # 5. Build LLM message payload
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in recent_messages:
        # Wrap the user's latest message to prevent prompt injection
        if msg.role == 'user' and msg.id == recent_messages[-1].id:
            content = wrap_user_message(msg.content)
        else:
            content = msg.content
            
        messages.append({
            "role": msg.role,
            "content": content
        })
        
    # 6. Query LLM
    try:
        response_data = query_groq_llm(messages)
    except Exception as e:
        logger.error(f"Failed to query LLM: {str(e)}")
        response_data = {
            "reply": "I'm sorry, an error occurred while processing your request.",
            "sources": [],
            "suggestions": [],
            "warnings": ["LLM Query Failed"],
            "confidence": "low",
            "context_used": []
        }
        
    # 7. Save Assistant message
    assistant_msg = Message.objects.create(
        conversation=conversation,
        role='assistant',
        content=response_data.get('reply', ''),
        metadata={
            "sources": response_data.get('sources', []),
            "suggestions": response_data.get('suggestions', []),
            "warnings": response_data.get('warnings', []),
            "confidence": response_data.get('confidence', 'unknown'),
            "context_used": response_data.get('context_used', [])
        }
    )
    
    # 8. Return structured data
    return {
        "conversation_id": conversation.id,
        "reply": assistant_msg.content,
        "sources": assistant_msg.metadata.get("sources"),
        "suggestions": assistant_msg.metadata.get("suggestions"),
        "warnings": assistant_msg.metadata.get("warnings"),
        "confidence": assistant_msg.metadata.get("confidence"),
        "context_used": assistant_msg.metadata.get("context_used"),
        "created_at": assistant_msg.created_at
    }
