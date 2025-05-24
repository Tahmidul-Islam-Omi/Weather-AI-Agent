from fastapi import APIRouter, HTTPException, Header
from app.models.weather import WeatherQuery, WeatherResponse
from app.services.ai_service import WeatherAIService
from app.db.supabase_client import supabase_db
from typing import Optional
import uuid

router = APIRouter()

@router.post("/query", response_model=WeatherResponse)
async def process_weather_query(query: WeatherQuery, x_session_id: Optional[str] = Header(None)):
    """
    Process a natural language weather query
    
    The query will be processed by the AI to extract relevant information,
    then the appropriate weather data will be fetched and explained.
    A `X-Session-ID` header can be provided to maintain conversation context.
    If not provided, a new session ID will be generated.
    """
    try:
        # Generate session ID if not provided
        if not x_session_id:
            x_session_id = f"session_{uuid.uuid4().hex[:16]}"
        
        ai_service = WeatherAIService()
        result = await ai_service.process_query(query.query, session_id=x_session_id)
        
        # Add session_id to response so frontend can track it
        result["session_id"] = x_session_id
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.delete("/clear-chat")
async def clear_chat_history(x_session_id: Optional[str] = Header(None)):
    """
    Clear chat history for a specific session
    
    Requires X-Session-ID header to identify which session's history to clear.
    """
    if not x_session_id:
        raise HTTPException(status_code=400, detail="X-Session-ID header is required")
    
    try:
        success = await supabase_db.clear_chat_history(x_session_id)
        if success:
            return {"message": "Chat history cleared successfully", "session_id": x_session_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear chat history")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing chat history: {str(e)}")