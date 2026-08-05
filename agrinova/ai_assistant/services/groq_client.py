import os
import json
import time
import logging
from groq import Groq

# Configure logging for the LLM Client
logger = logging.getLogger(__name__)
# If we don't have a handler, set up a basic one for console
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

# Primary and Fallback models
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY is not set in environment variables.")
        raise ValueError("GROQ_API_KEY not found.")
    return Groq(api_key=api_key)

def query_groq_llm(messages, use_fallback=False):
    """
    Executes the LLM request to Groq with timing, logging, and automatic fallback.
    Returns the JSON parsed response.
    """
    client = get_groq_client()
    model_to_use = FALLBACK_MODEL if use_fallback else PRIMARY_MODEL
    
    start_time = time.time()
    logger.info(f"Initiating Groq LLM request using model: {model_to_use}")
    
    try:
        completion = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
        )
        
        end_time = time.time()
        response_time = round(end_time - start_time, 3)
        
        # Log successful request
        token_usage = completion.usage.total_tokens if completion.usage else "Unknown"
        logger.info(f"Groq LLM success | Model: {model_to_use} | Time: {response_time}s | Tokens: {token_usage}")
        
        response_content = completion.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        end_time = time.time()
        response_time = round(end_time - start_time, 3)
        logger.error(f"Groq LLM error | Model: {model_to_use} | Time: {response_time}s | Error: {str(e)}")
        
        # Trigger fallback if primary failed
        if not use_fallback:
            logger.warning(f"Falling back to {FALLBACK_MODEL}...")
            return query_groq_llm(messages, use_fallback=True)
        else:
            # If fallback also fails, return a safe error response
            logger.error("Fallback model also failed.")
            return {
                "reply": "I'm sorry, I am currently experiencing technical difficulties and cannot process your request. Please try again later.",
                "sources": [],
                "suggestions": [],
                "warnings": ["AI Service Unavailable"],
                "confidence": "low",
                "context_used": []
            }
