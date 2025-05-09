import httpx
from typing import Dict, Any
from app.core.config import settings

class WeatherService:
    """Service for interacting with OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = settings.OPENWEATHERMAP_API_KEY
        self.base_url = settings.OPENWEATHERMAP_BASE_URL
    
    async def get_weather_by_city(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """Get weather data for a specific city"""
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_weather_by_coordinates(self, lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
        """Get weather data for specific coordinates"""
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": units
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_forecast(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """Get 5-day forecast for a specific city"""
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()