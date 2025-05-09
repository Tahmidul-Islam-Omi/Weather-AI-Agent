from fastapi import APIRouter, HTTPException, Depends
from app.models.weather import WeatherQuery, WeatherResponse
from app.services.ai_service import WeatherAIService

router = APIRouter()

@router.post("/query", response_model=WeatherResponse)
async def process_weather_query(query: WeatherQuery):
    """
    Process a natural language weather query
    
    The query will be processed by the AI to extract relevant information,
    then the appropriate weather data will be fetched and explained.
    """
    try:
        ai_service = WeatherAIService()
        result = await ai_service.process_query(query.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")