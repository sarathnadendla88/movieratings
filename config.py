"""
Configuration settings for the Movie Rating Aggregator application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))  # seconds

# Application Settings
APP_TITLE = "🎬 Movie Rating Aggregator"
APP_ICON = "🍿"
DEFAULT_LAYOUT = "wide"

# Cache Settings
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour in seconds

# Movie Rating Platforms
MOVIE_PLATFORMS = [
    "BookMyShow",
    "Paytm",
    "PVR Cinemas",
    "INOX Movies",
    "Cinepolis"
]

# Feature Flags
ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "false").lower() == "true"
ENABLE_FEEDBACK = os.getenv("ENABLE_FEEDBACK", "true").lower() == "true"
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"

# Error Messages
ERROR_MESSAGES = {
    "api_connection": "Unable to connect to the rating service. Please try again later.",
    "invalid_response": "Received an invalid response from the rating service.",
    "timeout": "The request timed out. Please try again.",
    "no_results": "No ratings found for this movie. Please check the movie name and try again."
}

# UI Settings
THEME_PRIMARY_COLOR = "#E50914"  # Netflix red
THEME_SECONDARY_COLOR = "#221F1F"  # Dark gray/black
THEME_WARNING_COLOR = "#FFC107"  # Amber
THEME_ERROR_COLOR = "#F44336"  # Red
THEME_SUCCESS_COLOR = "#4CAF50"  # Green
