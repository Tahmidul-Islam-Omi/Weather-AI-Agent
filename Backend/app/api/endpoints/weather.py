from fastapi import APIRouter, HTTPException, Depends, Header # Add Header
from app.models.weather import WeatherQuery, WeatherResponse
from app.services.ai_service import WeatherAIService
from typing import Optional # Add Optional

router = APIRouter()

@router.post("/query", response_model=WeatherResponse)
async def process_weather_query(query: WeatherQuery, x_session_id: Optional[str] = Header(None)): # Add X-Session-ID header
    """
    Process a natural language weather query
    
    The query will be processed by the AI to extract relevant information,
    then the appropriate weather data will be fetched and explained.
    A `X-Session-ID` header can be provided to maintain conversation context.
    """
    try:
        ai_service = WeatherAIService()
        # Use x_session_id if provided, otherwise, you might generate one or handle None
        # For simplicity, we pass it directly. The service/db layer handles None.
        result = await ai_service.process_query(query.query, session_id=x_session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")