from pydantic import BaseModel, Field
from typing import  Dict, Any

class WeatherQuery(BaseModel):
    """Model for user weather query"""
    query: str = Field(..., description="User's natural language query about weather")

class WeatherResponse(BaseModel):
    """Model for weather response"""
    query: str = Field(..., description="Original user query")
    processed_query: str = Field(..., description="Query processed by AI")
    weather_data: Dict[str, Any] = Field(..., description="Weather data from OpenWeatherMap")
    ai_explanation: str = Field(..., description="AI-generated explanation of the weather data")