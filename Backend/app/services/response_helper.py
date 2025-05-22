from typing import Dict, Any, Optional
import logging

def handle_empty_query(query: str, logger: logging.Logger) -> Optional[Dict[str, Any]]:
    """Checks for an empty query and returns a standard response if it is."""
    if not query or query.strip() == "":
        logger.warning("Empty query received.")
        return {
            "query": "",
            "processed_query": "Empty query received.",
            "weather_data": {},
            "ai_explanation": "Please provide a valid weather query."
        }
    return None

def build_no_city_response(query: str, logger: logging.Logger) -> Dict[str, Any]:
    """Constructs the response when no city could be determined."""
    logger.warning("No city specified in query or recent context.")
    return {
        "query": query,
        "processed_query": "No city specified in query or recent context.",
        "weather_data": {},
        "ai_explanation": "I couldn't determine which city you're asking about. Please specify a city name in your query."
    }

def build_final_response(
    query: str,
    query_details: Dict[str, Any],
    weather_data: Dict[str, Any],
    explanation: str
) -> Dict[str, Any]:
    """Constructs the final successful response dictionary."""
    cities_str = ', '.join(query_details.get('cities', []))
    query_types_str = ', '.join(query_details.get('query_types', []))
    time_context_str = query_details.get('time_context', 'N/A')

    return {
        "query": query,
        "processed_query": f"Analyzed query for cities: {cities_str}; "
                           f"Types: {query_types_str}; "
                           f"Time: {time_context_str}",
        "weather_data": weather_data,
        "ai_explanation": explanation
    }