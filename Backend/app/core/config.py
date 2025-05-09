import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API Keys
    OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # OpenWeatherMap API Base URL
    OPENWEATHERMAP_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    
    # Project metadata
    PROJECT_NAME: str = "Weather AI Agent"
    PROJECT_DESCRIPTION: str = "An AI-powered weather agent using LangChain and Gemini"
    VERSION: str = "0.1.0"

settings = Settings()