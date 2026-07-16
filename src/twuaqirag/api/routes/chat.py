"""
Chat endpoint - handles text-based chat messages
"""
from fastapi import APIRouter, HTTPException
from twuaqirag.api.schemas import ChatMessage, ChatResponse, ClearHistoryRequest
from twuaqirag.rag.orchestrator import generate_response
from twuaqirag.rag.memory import store
from langchain_community.chat_message_histories import ChatMessageHistory

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Handle text chat messages"""
    if not chat_message.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    response = await generate_response(chat_message.message, chat_message.session_id)
    
    # Generate TTS audio
    audio_base64 = None
    try:
        from twuaqirag.services.text_to_speech import get_tts_service
        import base64
        
        tts_service = get_tts_service()
        if tts_service.config.enabled:
            # Generate audio in memory
            tts_result = tts_service.synthesize_text(response)
            # Encode audio to base64
            audio_base64 = base64.b64encode(tts_result.audio_data).decode('utf-8')
    except Exception as e:
        print(f"Error generating TTS for chat: {e}")
        # Continue without audio on error
    
    return ChatResponse(
        response=response,
        session_id=chat_message.session_id,
        audio_base64=audio_base64
    )


@router.post("/clear-history")
async def clear_history(request: ClearHistoryRequest):
    """Clear conversation history for a session"""
    session_id = request.session_id
    if session_id in store:
        store[session_id] = ChatMessageHistory()
    
    return {"message": "History cleared", "session_id": session_id}
