"""
Weather tool implementation with real API integration
Supports multiple weather APIs: OpenWeatherMap, WeatherAPI, and Visual Crossing
"""

from typing import Any, Dict, Optional
from .base import BaseTool
import os
import httpx
import asyncio

class WeatherTool(BaseTool):
    """Weather information tool using real weather APIs"""

    def __init__(self, api_key: Optional[str] = None, provider: str = "openweathermap"):
        """
        Initialize Weather Tool with API credentials
        
        Args:
            api_key: API key for weather service (or set WEATHER_API_KEY env var)
            provider: Weather API provider ('openweathermap', 'weatherapi', 'visualcrossing')
        
        To get free API keys:
        - OpenWeatherMap: https://openweathermap.org/api (Free tier: 1000 calls/day)
        - WeatherAPI: https://www.weatherapi.com/signup.aspx (Free tier: 1M calls/month)
        - Visual Crossing: https://www.visualcrossing.com/weather-api (Free tier: 1000 calls/day)
        """
        super().__init__(
            name="get_weather",
            description="""CRITICAL: Use this tool for ALL weather queries. 
                          Gets REAL-TIME current weather information for any city in the world.
                          This tool provides actual weather data including temperature, conditions, humidity, wind, and more.
                          YOU MUST USE THIS TOOL when users ask about weather, temperature, or current conditions.
                          DO NOT say you cannot access real-time weather - this tool gives you that capability.""",
            input_schema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (can include country code, e.g., 'London,UK' or 'New York,US')"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature units",
                        "default": "celsius"
                    }
                },
                "required": ["city"]
            }
        )
        
        self.api_key = api_key or os.getenv("WEATHER_API_KEY")
        self.provider = provider.lower()
        
        if not self.api_key:
            print("⚠️  Warning: No WEATHER_API_KEY found. Weather tool will return mock data.")
            print("   Set WEATHER_API_KEY environment variable or pass api_key parameter.")
            print(f"   Get a free API key from: {self._get_signup_url()}")
        
        # HTTP client with timeout
        self.client = httpx.AsyncClient(timeout=10.0)

    def _get_signup_url(self) -> str:
        """Get signup URL for the selected provider"""
        urls = {
            "openweathermap": "https://openweathermap.org/api",
            "weatherapi": "https://www.weatherapi.com/signup.aspx",
            "visualcrossing": "https://www.visualcrossing.com/weather-api"
        }
        return urls.get(self.provider, "https://openweathermap.org/api")

    async def _fetch_openweathermap(self, city: str, units: str) -> Dict[str, Any]:
        """Fetch weather from OpenWeatherMap API"""
        # Convert units
        api_units = "metric" if units == "celsius" else "imperial"
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": api_units
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "units": units,
            "condition": data["weather"][0]["description"].title(),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": round(data["wind"]["speed"], 1),
            "clouds": data["clouds"]["all"],
            "visibility": data.get("visibility", "N/A"),
            "sunrise": data["sys"]["sunrise"],
            "sunset": data["sys"]["sunset"],
            "provider": "OpenWeatherMap"
        }

    async def _fetch_weatherapi(self, city: str, units: str) -> Dict[str, Any]:
        """Fetch weather from WeatherAPI.com"""
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": self.api_key,
            "q": city,
            "aqi": "no"
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Get temperature in requested units
        temp = data["current"]["temp_c"] if units == "celsius" else data["current"]["temp_f"]
        feels_like = data["current"]["feelslike_c"] if units == "celsius" else data["current"]["feelslike_f"]
        
        return {
            "success": True,
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "temperature": round(temp, 1),
            "feels_like": round(feels_like, 1),
            "units": units,
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "pressure": data["current"]["pressure_mb"],
            "wind_speed": round(data["current"]["wind_kph"] if units == "celsius" else data["current"]["wind_mph"], 1),
            "wind_direction": data["current"]["wind_dir"],
            "clouds": data["current"]["cloud"],
            "visibility": data["current"]["vis_km"] if units == "celsius" else data["current"]["vis_miles"],
            "uv_index": data["current"]["uv"],
            "last_updated": data["current"]["last_updated"],
            "provider": "WeatherAPI"
        }

    async def _fetch_visualcrossing(self, city: str, units: str) -> Dict[str, Any]:
        """Fetch weather from Visual Crossing Weather API"""
        # Visual Crossing uses 'us' for Fahrenheit, 'metric' for Celsius
        unit_group = "us" if units == "fahrenheit" else "metric"
        
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}"
        params = {
            "key": self.api_key,
            "unitGroup": unit_group,
            "include": "current",
            "contentType": "json"
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        current = data["currentConditions"]
        
        return {
            "success": True,
            "city": data["resolvedAddress"],
            "temperature": round(current["temp"], 1),
            "feels_like": round(current["feelslike"], 1),
            "units": units,
            "condition": current["conditions"],
            "humidity": current["humidity"],
            "pressure": current["pressure"],
            "wind_speed": round(current["windspeed"], 1),
            "wind_direction": current.get("winddir", "N/A"),
            "clouds": current["cloudcover"],
            "visibility": current["visibility"],
            "uv_index": current.get("uvindex", "N/A"),
            "sunrise": current.get("sunrise", "N/A"),
            "sunset": current.get("sunset", "N/A"),
            "provider": "Visual Crossing"
        }

    async def _fetch_mock_data(self, city: str, units: str) -> Dict[str, Any]:
        """Fallback mock data when no API key is available"""
        mock_data = {
            "london": {"temp": 15, "condition": "Cloudy", "humidity": 65},
            "paris": {"temp": 18, "condition": "Sunny", "humidity": 50},
            "new york": {"temp": 22, "condition": "Partly cloudy", "humidity": 55},
            "tokyo": {"temp": 25, "condition": "Clear", "humidity": 45},
            "sydney": {"temp": 28, "condition": "Sunny", "humidity": 60},
            "berlin": {"temp": 12, "condition": "Rainy", "humidity": 80},
            "dubai": {"temp": 35, "condition": "Sunny", "humidity": 40},
            "mumbai": {"temp": 30, "condition": "Humid", "humidity": 75},
            "cairo": {"temp": 32, "condition": "Clear", "humidity": 30},
            "moscow": {"temp": 5, "condition": "Snow", "humidity": 70}
        }
        
        city_lower = city.split(",")[0].lower().strip()
        
        if city_lower not in mock_data:
            return {
                "success": False,
                "error": f"Mock weather data not available for '{city}'. Please set WEATHER_API_KEY for real data."
            }
        
        data = mock_data[city_lower]
        temp = data["temp"]
        
        if units == "fahrenheit":
            temp = (temp * 9/5) + 32
        
        return {
            "success": True,
            "city": city.title(),
            "temperature": round(temp, 1),
            "units": units,
            "condition": data["condition"],
            "humidity": data["humidity"],
            "provider": "Mock Data (Set WEATHER_API_KEY for real data)",
            "note": "This is mock data. Get real weather by setting WEATHER_API_KEY environment variable."
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather for a city using real API"""
        try:
            city = arguments["city"]
            units = arguments.get("units", "celsius")
            
            # If no API key, use mock data
            if not self.api_key:
                return await self._fetch_mock_data(city, units)
            
            # Try to fetch from selected provider
            try:
                if self.provider == "openweathermap":
                    return await self._fetch_openweathermap(city, units)
                elif self.provider == "weatherapi":
                    return await self._fetch_weatherapi(city, units)
                elif self.provider == "visualcrossing":
                    return await self._fetch_visualcrossing(city, units)
                else:
                    return {
                        "success": False,
                        "error": f"Unknown provider: {self.provider}. Use 'openweathermap', 'weatherapi', or 'visualcrossing'"
                    }
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    return {
                        "success": False,
                        "error": f"Invalid API key for {self.provider}. Please check your WEATHER_API_KEY."
                    }
                elif e.response.status_code == 404:
                    return {
                        "success": False,
                        "error": f"City '{city}' not found. Try adding country code (e.g., 'London,UK')"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error ({e.response.status_code}): {e.response.text}"
                    }
            
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "error": "Weather API request timed out. Please try again."
                }
            
            except Exception as api_error:
                # Fallback to mock data on any API error
                print(f"API error, falling back to mock data: {api_error}")
                return await self._fetch_mock_data(city, units)
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting weather: {str(e)}"
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def __del__(self):
        """Cleanup on deletion"""
        try:
            asyncio.create_task(self.close())
        except:
            pass


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
SETUP INSTRUCTIONS:

1. Get a free API key from one of these providers:
   - OpenWeatherMap: https://openweathermap.org/api (Recommended)
   - WeatherAPI: https://www.weatherapi.com/signup.aspx
   - Visual Crossing: https://www.visualcrossing.com/weather-api

2. Add to your .env file:
   WEATHER_API_KEY=your_api_key_here
   WEATHER_PROVIDER=openweathermap  # or weatherapi, visualcrossing

3. Update config.py:
   WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
   WEATHER_PROVIDER = os.getenv("WEATHER_PROVIDER", "openweathermap")

4. Update backend/mcp/server.py to pass API key:
   
   from config import config
   
   def _initialize_tools(self):
       default_tools = [
           CalculatorTool(),
           WeatherTool(
               api_key=config.WEATHER_API_KEY,
               provider=config.WEATHER_PROVIDER
           ),
           FileOpsTool()
       ]
       
       for tool in default_tools:
           self.register_tool(tool)

EXAMPLE QUERIES:
- "What's the weather in London?"
- "Tell me the temperature in Tokyo in Fahrenheit"
- "What's the weather like in New York,US?"
- "Compare weather in Paris and Berlin"

WITHOUT API KEY:
- Tool will automatically fall back to mock data
- You'll see a warning message with instructions

FREE TIER LIMITS:
- OpenWeatherMap: 1,000 calls/day, 60 calls/minute
- WeatherAPI: 1,000,000 calls/month
- Visual Crossing: 1,000 calls/day

RECOMMENDED: OpenWeatherMap (good free tier, reliable, comprehensive data)
"""