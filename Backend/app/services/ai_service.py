from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.services.weather_service import WeatherService
import asyncio
import json
from datetime import datetime, timedelta

class WeatherAIService:
    """Service for processing weather queries using LangChain and Gemini"""
    
    QUERY_TYPES = {
        "current": "Get current weather conditions",
        "forecast": "Get weather forecast",
        "temperature": "Get specific temperature information",
        "precipitation": "Get rainfall/snow information",
        "wind": "Get wind conditions",
        "humidity": "Get humidity levels",
        "comparison": "Compare weather between times/places",
        "conditions": "Get specific weather conditions (sunny, cloudy, etc.)",
        "alerts": "Get weather alerts or warnings"
    }
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2
        )
    
    async def _extract_query_details(self, query: str) -> Dict[str, Any]:
        """Extract detailed information from the weather query"""
        prompt = f"""
        Analyze the following weather query and extract key information:
        
        Query: {query}
        
        Provide a JSON response with the following fields:
        - cities: List of city names mentioned (empty if none)
        - query_types: List of query types from {list(self.QUERY_TYPES.keys())} (can be multiple)
        - time_context: "current", "future", "past", or specific time period
        - specific_conditions: List of specific weather conditions asked about (temperature, rain, wind, etc.)
        - comparison_type: "time" if comparing different times, "location" if comparing places, null if no comparison
        
        Response should be ONLY valid JSON.
        """
        
        response = await self.llm.ainvoke(prompt)
        try:
            # Clean the response to ensure it's valid JSON
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]  # Remove ```json and ``` markers
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback to basic extraction if JSON parsing fails
            return {
                "cities": [],
                "query_types": ["current"],
                "time_context": "current",
                "specific_conditions": [],
                "comparison_type": None
            }
    
    async def _get_weather_data(self, query_details: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch appropriate weather data based on query details"""
        weather_data = {}
        
        for city in query_details["cities"]:
            city_data = {}
            
            # Handle different time contexts
            if query_details["time_context"] == "current":
                city_data["current"] = await self.weather_service.get_weather_by_city(city)
            elif query_details["time_context"] == "future":
                city_data["forecast"] = await self.weather_service.get_forecast(city)
            
            # If comparison is needed, get both current and forecast
            if query_details["comparison_type"]:
                city_data["current"] = await self.weather_service.get_weather_by_city(city)
                city_data["forecast"] = await self.weather_service.get_forecast(city)
            
            weather_data[city] = city_data
        
        return weather_data
    
    async def _generate_weather_explanation(self, query: str, query_details: Dict[str, Any], weather_data: Dict[str, Any]) -> str:
        """Generate a natural language explanation of weather data"""
        prompt = f"""
        Generate a helpful explanation for the following weather query and data:
        
        Query: {query}
        
        Query Analysis: {json.dumps(query_details, indent=2)}
        
        Weather Data: {json.dumps(weather_data, indent=2)}
        
        Consider the following in your response:
        1. If it's a comparison query, compare the relevant aspects
        2. Focus on the specific conditions asked about
        3. Provide relevant context based on the time period
        4. If multiple cities are involved, address each one
        5. If specific weather conditions were asked about, prioritize those in the response
        
        Provide a concise, natural-sounding explanation focusing on exactly what was asked.
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user's weather query"""
        try:
            if not query or query.strip() == "":
                return {
                    "query": "",
                    "processed_query": "",
                    "weather_data": {},
                    "ai_explanation": "Please provide a valid weather query."
                }
            
            # Extract detailed query information
            query_details = await self._extract_query_details(query)
            
            # Handle queries with no city specified
            if not query_details["cities"]:
                return {
                    "query": query,
                    "processed_query": "No city specified in query",
                    "weather_data": {},
                    "ai_explanation": "I couldn't determine which city you're asking about. Please specify a city name in your query."
                }
            
            # Get weather data based on query details
            weather_data = await self._get_weather_data(query_details)
            
            # Generate explanation
            explanation = await self._generate_weather_explanation(query, query_details, weather_data)
            
            # Return structured response
            return {
                "query": query,
                "processed_query": f"Analyzed query for cities: {', '.join(query_details['cities'])}; "
                f"Types: {', '.join(query_details['query_types'])}; " 
                f"Time: {query_details['time_context']}",
                "weather_data": weather_data,
                "ai_explanation": explanation
            }
        except Exception as e:
            # Log the error for debugging
            print(f"Error processing query: {str(e)}")
            raise