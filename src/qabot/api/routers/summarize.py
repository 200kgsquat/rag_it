
from fastapi import APIRouter
from src.qabot.api.schemas.summarize import SummarizeRequest

summarize = APIRouter()

@summarize.post("/summarize")
async def summarize_conversation(request: SummarizeRequest):
    """
    Summarize the conversation history
    """
    try:
                                                                              
        user_messages = [msg["content"] for msg in request.chat_history if msg["role"] == "user"]
        
                                                 
        recent_questions = user_messages[-4:] if len(user_messages) > 4 else user_messages
        
        if recent_questions:
            summary = "Recent discussion about: " + ", ".join([q[:30] + "..." if len(q) > 30 else q for q in recent_questions])
        else:
            summary = "Conversation in progress"
            
        return {"summary": summary, "session_id": request.session_id}
        
    except Exception as e:
        return {"summary": "Conversation context available", "session_id": request.session_id}