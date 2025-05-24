import json
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from app.db.supabase_client import SupabaseDB
from . import llm_prompts # Assuming llm_prompts.py is in the same directory
import logging

# If you have a shared QUERY_TYPES, define or import it here
# For now, assuming it's passed or handled within ai_service
# QUERY_TYPES = { ... }

async def extract_query_details_from_llm(
    llm: ChatGoogleGenerativeAI,
    query: str,
    query_types_list: List[str],
    logger: logging.Logger
) -> Dict[str, Any]:
    """
    Extracts detailed information from the user's query using the LLM.
    """
    logger.debug(f"Extracting query details for: {query}")
    
    prompt = llm_prompts.EXTRACT_QUERY_DETAILS_PROMPT_TEMPLATE.format(
        query=query,
        query_types_list=query_types_list
    )
    
    response = await llm.ainvoke(prompt)
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```") and content.endswith("```"):
            content = content[3:-3]
        
        extracted_details = json.loads(content)
        logger.debug(f"Extracted details: {extracted_details}")
        
        # Simplified follow-up logic, can be expanded as in original
        if extracted_details.get("is_follow_up", False) and not extracted_details.get("cities"):
            if "tomorrow" in query.lower():
                extracted_details["time_context"] = "future"
                extracted_details["specific_time"] = "tomorrow"
            elif "week" in query.lower():
                extracted_details["time_context"] = "future"
                extracted_details["specific_time"] = "week"
            elif "month" in query.lower():
                extracted_details["time_context"] = "future"
                extracted_details["specific_time"] = "month"
                
        return extracted_details
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError in extract_query_details_from_llm: {e}. Content was: {response.content}")
        # Fallback, similar to original
        return {
            "cities": [],
            "query_types": ["current"],
            "time_context": "current",
            "specific_conditions": [],
            "comparison_type": None,
            "is_follow_up": "tomorrow" in query.lower() or "next" in query.lower() or "and" in query.lower()
        }

async def infer_city_from_history(
    llm: ChatGoogleGenerativeAI,
    db: SupabaseDB,
    query: str,
    session_id: Optional[str],
    logger: logging.Logger
) -> Optional[str]:
    """
    If no city is specified in a follow-up query, tries to infer it from chat history.
    Returns the inferred city name or None.
    """
    logger.debug("Attempting to infer city from history.")
    history = await db.get_chat_history(session_id=session_id, limit=5)
    
    if history:
        history_context_for_city_extraction_str = "Consider the following recent conversation:\n"
        for record in reversed(history): # Ensure reversed to get recent context first
            history_context_for_city_extraction_str += f"User: {record['user_message']}\n"
        
        city_extraction_prompt_text = llm_prompts.CITY_EXTRACTION_FROM_HISTORY_PROMPT_TEMPLATE.format(
            history_context_for_city_extraction=history_context_for_city_extraction_str,
            query=query
        )
        
        city_response = await llm.ainvoke(city_extraction_prompt_text)
        extracted_city_from_history = city_response.content.strip().strip('.')
        logger.debug(f"LLM response for city extraction: '{extracted_city_from_history}'")

        if extracted_city_from_history and extracted_city_from_history.lower() != 'none':
            potential_city = extracted_city_from_history
            if potential_city.lower().startswith("the city is "):
                potential_city = potential_city[len("the city is "):].strip()
            if potential_city.lower().startswith("city: "):
                potential_city = potential_city[len("city: "):].strip()
            
            is_disclaimer = any(kw in potential_city.lower() for kw in 
                                ["sorry", "unable", "don't know", "cannot determine", 
                                 "no city", "context does not", "not specified", "no specific city"])

            if not is_disclaimer and 1 < len(potential_city) < 50:
                logger.info(f"Inferred city from history: {potential_city}")
                return potential_city
    return None

async def get_weather_data(weather_service, query_details, logger=None):
    """Fetch appropriate weather data based on query details """
    weather_data = {}
    for city in query_details["cities"]:
        city_data = {}
        if query_details["time_context"] == "current":
            city_data["current"] = await weather_service.get_weather_by_city(city)
        if query_details["time_context"] == "future" or query_details.get("is_follow_up", False):
            forecast_data = await weather_service.get_forecast(city)
            city_data["forecast"] = forecast_data
            if "specific_time" in query_details:
                city_data["specific_time_request"] = query_details["specific_time"]
        if query_details.get("comparison_type"):
            if "current" not in city_data:
                city_data["current"] = await weather_service.get_weather_by_city(city)
            if "forecast" not in city_data:
                city_data["forecast"] = await weather_service.get_forecast(city)
        weather_data[city] = city_data
    return weather_data

async def generate_weather_explanation(llm, db, llm_prompts, query, query_details, weather_data, session_id, logger):
    logger.debug(f"Generating weather explanation for query: {query}, session_id: {session_id}")
    history_from_db = await db.get_chat_history(session_id=session_id, limit=5)
    chat_context_str = ""
    if history_from_db:
        chat_context_str = "Previous conversation:\n"
        for record in history_from_db:
            chat_context_str += f"User: {record['user_message']}\n"
            chat_context_str += f"AI: {record['ai_response']}\n"
    is_follow_up = query_details.get("is_follow_up", False)
    follow_up_context_str = ""
    if is_follow_up:
        follow_up_context_str = """
        Note: This appears to be a follow-up question to a previous weather query.
        Make sure your response acknowledges the continued conversation and references 
        the previous information appropriately.
        """
        if query_details.get("specific_time"):
            specific_time = query_details["specific_time"]
            follow_up_context_str += f"""
            The user is specifically asking about the weather for {specific_time}.
            Focus your response on the forecast for {specific_time}.
            """
    prompt_text = llm_prompts.GENERATE_WEATHER_EXPLANATION_PROMPT_TEMPLATE.format(
        query=query,
        chat_context=chat_context_str,
        query_details_json=json.dumps(query_details, indent=2),
        weather_data_json=json.dumps(weather_data, indent=2),
        follow_up_context=follow_up_context_str
    )
    chat_history_messages = []
    for record in history_from_db:
        from langchain_core.messages import HumanMessage, AIMessage
        chat_history_messages.append(HumanMessage(content=record["user_message"]))
        chat_history_messages.append(AIMessage(content=record["ai_response"]))
    from langchain_core.messages import HumanMessage
    current_prompt_message = HumanMessage(content=prompt_text)
    llm_input_messages = chat_history_messages + [current_prompt_message]
    response = await llm.ainvoke(llm_input_messages)
    logger.debug(f"Generated explanation: {response.content.strip()}")
    return response.content.strip()

def manage_city_context(query_details, last_known_cities, logger):
    """
    Manages last_known_cities and updates query_details.
    Returns (city_present: bool, updated_last_known_cities: List[str]).
    """
    if query_details.get("cities"):
        last_known_cities = query_details["cities"]
        logger.debug(f"Updated last_known_cities: {last_known_cities}")
        return True, last_known_cities
    elif last_known_cities:
        query_details["cities"] = last_known_cities
        logger.info(f"Used city from instance memory (last_known_cities): {last_known_cities}")
        return True, last_known_cities
    return False, last_known_cities