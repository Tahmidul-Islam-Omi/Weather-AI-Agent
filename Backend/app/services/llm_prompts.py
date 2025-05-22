EXTRACT_QUERY_DETAILS_PROMPT_TEMPLATE = """
Analyze the following weather query and extract key information:

Query: {query}

This query may be a follow-up to a previous conversation about weather. 
If the query seems incomplete (like "And tomorrow?" or "What about next week?"),
it's likely referring to the previously mentioned location or weather topic.

Provide a JSON response with the following fields:
- cities: List of city names mentioned (empty if none and no context available)
- query_types: List of query types from {query_types_list} (can be multiple)
- time_context: "current", "future", "past", or specific time period
  * For queries like "tomorrow", "next day", etc., use "future" and note the specific timeframe
  * For queries like "yesterday", "last week", etc., use "past" and note the timeframe
- specific_conditions: List of specific weather conditions asked about (temperature, rain, wind, etc.)
- comparison_type: "time" if comparing different times, "location" if comparing places, null if no comparison
- is_follow_up: true if this appears to be a follow-up query requiring previous context, false otherwise

Response should be ONLY valid JSON.
"""

GENERATE_WEATHER_EXPLANATION_PROMPT_TEMPLATE = """
Generate a helpful explanation for the following weather query and data:

Query: {query}

{chat_context}

Query Analysis: {query_details_json}

Weather Data: {weather_data_json}

{follow_up_context}

Consider the following in your response:
1. If it's a comparison query, compare the relevant aspects
2. Focus on the specific conditions asked about
3. Provide relevant context based on the time period
4. If multiple cities are involved, address each one
5. If specific weather conditions were asked about, prioritize those in the response
6. If this is a follow-up query, maintain context from the previous conversation

Provide a concise, natural-sounding explanation focusing on exactly what was asked.
"""

CITY_EXTRACTION_FROM_HISTORY_PROMPT_TEMPLATE = """
{history_context_for_city_extraction}
Current user query: "{query}"

Based on the conversation history, what is the primary city being discussed or previously mentioned that the current query most likely refers to? 
Respond with ONLY the city name (e.g., London, New York). If no city is clearly implied for the current query from the history, respond with the exact word 'None'.
"""