from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.services.weather_service import WeatherService
import asyncio
import json
from langchain_core.messages import HumanMessage, AIMessage
from app.db.supabase_client import supabase_db
import logging
from . import llm_prompts # Import the new prompts module
# NEW IMPORTS for helper modules
from . import query_helper
from . import response_helper

logger = logging.getLogger(__name__)

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
        self.db = supabase_db # Use the imported instance
        self.last_known_cities: List[str] = []
        logger.info("WeatherAIService initialized.")
    
    async def _check_weather_related(self, query: str) -> bool:
        """
        Checks if the query is weather-related using the safeguard prompt.
        Returns True if weather-related, False otherwise.
        """
        logger.debug(f"Checking if query is weather-related: {query}")
        prompt = llm_prompts.WEATHER_QUERY_SAFEGUARD_PROMPT_TEMPLATE.format(query=query)
        response = await self.llm.ainvoke(prompt)
        result = response.content.strip()
        logger.debug(f"Weather check response: {result}")
        return "WEATHER_RELATED" in result
    
    def _build_non_weather_response(self, query: str) -> Dict[str, Any]:
        """Constructs the response when the query is not weather-related."""
        logger.warning(f"Non-weather query received: {query}")
        return {
            "query": query,
            "processed_query": "Non-weather query received.",
            "weather_data": {},
            "ai_explanation": "I'm a weather-focused assistant and can only help with weather-related questions. Please ask me about current weather, forecasts, or any other weather-related topics!"
        }
    
    # Removed _extract_query_details method
    
    def _handle_empty_query(self, query: str) -> Optional[Dict[str, Any]]:
        # MODIFIED: Use helper function
        return response_helper.handle_empty_query(query, logger)

    async def _infer_city_from_history_if_needed(self, query_details: Dict[str, Any], query: str, session_id: Optional[str]) -> None:
        """
        If the query is a follow-up and no city is specified,
        tries to infer the city from chat history.
        Modifies query_details in-place.
        """
        if not query_details.get("cities") and query_details.get("is_follow_up", False):
            # MODIFIED: Use helper function and update query_details
            inferred_city = await query_helper.infer_city_from_history(
                llm=self.llm,
                db=self.db,
                query=query,
                session_id=session_id,
                logger=logger
            )
            if inferred_city:
                query_details["cities"] = [inferred_city]
                logger.info(f"Updated query_details with inferred city: {inferred_city}")

    def _build_no_city_response(self, query: str) -> Dict[str, Any]:
        # MODIFIED: Use helper function
        return response_helper.build_no_city_response(query, logger)

    def _build_final_response(self, query: str, query_details: Dict[str, Any], weather_data: Dict[str, Any], explanation: str) -> Dict[str, Any]:
        # MODIFIED: Use helper function
        return response_helper.build_final_response(query, query_details, weather_data, explanation)

    async def process_query(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"Processing query: '{query}' for session_id: '{session_id}'")
        try:
            empty_query_response = self._handle_empty_query(query)
            
            if empty_query_response:
                return empty_query_response
            
            # Check if query is weather-related
            is_weather_related = await self._check_weather_related(query)
            if not is_weather_related:
                # If query is not weather-related, don't bother with city validation
                # or other weather-specific processing
                non_weather_response = self._build_non_weather_response(query)
                # Still save the interaction in chat history
                await self.db.save_chat_message(session_id=session_id, user_message=query, ai_response=non_weather_response["ai_explanation"])
                return non_weather_response
            
            # MODIFIED: Call the helper function directly
            query_details = await query_helper.extract_query_details_from_llm(
                llm=self.llm,
                query=query,
                query_types_list=list(self.QUERY_TYPES.keys()),
                logger=logger
            )
            
            logger.info(f"Initial query_details: {query_details}")
            
            await self._infer_city_from_history_if_needed(query_details, query, session_id)
            city_present, self.last_known_cities = query_helper.manage_city_context(query_details, self.last_known_cities, logger)
            if not city_present:
                no_city_response = self._build_no_city_response(query)
                await self.db.save_chat_message(session_id=session_id, user_message=query, ai_response=no_city_response["ai_explanation"])
                return no_city_response
            
            weather_data = await query_helper.get_weather_data(self.weather_service, query_details, logger)
            explanation = await query_helper.generate_weather_explanation(self.llm, self.db, llm_prompts, query, query_details, weather_data, session_id, logger)
            logger.debug(f"Attempting to save to DB: session_id='{session_id}', user_message='{query}'")
            await self.db.save_chat_message(session_id=session_id, user_message=query, ai_response=explanation)
            logger.info("Successfully called save_chat_message.")
            return self._build_final_response(query, query_details, weather_data, explanation)
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}", exc_info=True)
            raise