from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.services.weather_service import WeatherService
import asyncio
import json
from datetime import datetime, timedelta
from langchain.memory import ConversationBufferMemory # Add this import
from langchain_core.messages import HumanMessage, AIMessage # Modified this import
from app.db.supabase_client import supabase_db # Add this import

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
        # self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True) # Remove or comment out
        self.db = supabase_db # Use the Supabase client instance
        self.last_known_cities: List[str] = []
    
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
        
        response = await self.llm.ainvoke(prompt) # This line was previously commented out
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
    
    async def _generate_weather_explanation(self, query: str, query_details: Dict[str, Any], weather_data: Dict[str, Any], session_id: Optional[str] = None) -> str:
        """Generate a natural language explanation of weather data, considering chat history from Supabase"""
        prompt_text = f"""
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
        
        # Load chat history from Supabase
        history_from_db = await self.db.get_chat_history(session_id=session_id, limit=5) # Get last 5 interactions
        
        chat_history_messages = []
        for record in history_from_db:
            chat_history_messages.append(HumanMessage(content=record["user_message"]))
            chat_history_messages.append(AIMessage(content=record["ai_response"]))
            
        # Create the current prompt message
        current_prompt_message = HumanMessage(content=prompt_text)
        
        # Combine history with the current prompt
        llm_input_messages = chat_history_messages + [current_prompt_message]
        
        response = await self.llm.ainvoke(llm_input_messages)
        return response.content.strip()
    
    async def process_query(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]: # Add session_id
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
            
            # If current query doesn't specify cities, try to use last known cities
            # This logic might need refinement with persistent chat history.
            # For now, we keep it, but session_id based context might be more robust.
            if not query_details.get("cities") and self.last_known_cities:
                query_details["cities"] = self.last_known_cities
            elif query_details.get("cities"):
                self.last_known_cities = query_details["cities"]
            
            if not query_details.get("cities"):
                # Try to infer city from chat history if not in current query or memory
                history = await self.db.get_chat_history(session_id=session_id, limit=1)
                if history:
                    # A simple heuristic: check the last user message for city names
                    # This could be improved with more sophisticated context extraction
                    last_user_message = history[0]["user_message"]
                    # Re-run extraction on last message if it might contain a city
                    # For simplicity, we'll just note this as an area for improvement.
                    # For now, if no city, we ask.
                    pass # Placeholder for more advanced city inference from history

            if not query_details.get("cities"):
                 return {
                    "query": query,
                    "processed_query": "No city specified in query or recent context.",
                    "weather_data": {},
                    "ai_explanation": "I couldn't determine which city you're asking about. Please specify a city name in your query or ensure it was mentioned recently."
                }
            
            # Get weather data based on query details
            weather_data = await self._get_weather_data(query_details)
            
            # Generate explanation, passing session_id
            explanation = await self._generate_weather_explanation(query, query_details, weather_data, session_id)
            
            # Save the current interaction to Supabase
            await self.db.save_chat_message(session_id=session_id, user_message=query, ai_response=explanation)
            
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