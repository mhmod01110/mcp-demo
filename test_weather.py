#!/usr/bin/env python3
"""
Weather API Testing Script
==========================

Standalone script to test weather API integration without running the full MCP server.
Tests all three providers: OpenWeatherMap, WeatherAPI, and Visual Crossing.

Usage:
    python test_weather_api.py
    python test_weather_api.py --city "London" --units fahrenheit
    python test_weather_api.py --provider weatherapi --city "Tokyo"
"""

import asyncio
import httpx
import os
import sys
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from datetime import datetime

load_dotenv()

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class WeatherAPITester:
    """Test weather API integration"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "openweathermap"):
        self.api_key = api_key or os.getenv("WEATHER_API_KEY")
        self.provider = provider.lower()
        self.client = httpx.AsyncClient(timeout=15.0)
    
    def print_header(self, text: str):
        """Print colored header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")
    
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")
    
    async def test_openweathermap(self, city: str, units: str) -> Dict[str, Any]:
        """Test OpenWeatherMap API"""
        self.print_info(f"Testing OpenWeatherMap API for {city}...")
        
        if not self.api_key:
            self.print_error("No API key provided!")
            return {"success": False, "error": "No API key"}
        
        api_units = "metric" if units == "celsius" else "imperial"
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": api_units
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            result = {
                "success": True,
                "provider": "OpenWeatherMap",
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
                "timestamp": datetime.fromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.print_success("OpenWeatherMap API call successful!")
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                self.print_error("Invalid API key!")
                return {"success": False, "error": "Invalid API key", "status_code": 401}
            elif e.response.status_code == 404:
                self.print_error(f"City '{city}' not found!")
                return {"success": False, "error": "City not found", "status_code": 404}
            else:
                self.print_error(f"HTTP error: {e.response.status_code}")
                return {"success": False, "error": str(e), "status_code": e.response.status_code}
        
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_weatherapi(self, city: str, units: str) -> Dict[str, Any]:
        """Test WeatherAPI.com"""
        self.print_info(f"Testing WeatherAPI.com for {city}...")
        
        if not self.api_key:
            self.print_error("No API key provided!")
            return {"success": False, "error": "No API key"}
        
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": self.api_key,
            "q": city,
            "aqi": "yes"
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            temp = data["current"]["temp_c"] if units == "celsius" else data["current"]["temp_f"]
            feels_like = data["current"]["feelslike_c"] if units == "celsius" else data["current"]["feelslike_f"]
            
            result = {
                "success": True,
                "provider": "WeatherAPI",
                "city": data["location"]["name"],
                "country": data["location"]["country"],
                "region": data["location"]["region"],
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
                "last_updated": data["current"]["last_updated"]
            }
            
            self.print_success("WeatherAPI.com call successful!")
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401 or e.response.status_code == 403:
                self.print_error("Invalid API key!")
                return {"success": False, "error": "Invalid API key", "status_code": e.response.status_code}
            elif e.response.status_code == 400:
                self.print_error(f"Bad request - City '{city}' might be invalid")
                return {"success": False, "error": "Bad request", "status_code": 400}
            else:
                self.print_error(f"HTTP error: {e.response.status_code}")
                return {"success": False, "error": str(e), "status_code": e.response.status_code}
        
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_visualcrossing(self, city: str, units: str) -> Dict[str, Any]:
        """Test Visual Crossing Weather API"""
        self.print_info(f"Testing Visual Crossing API for {city}...")
        
        if not self.api_key:
            self.print_error("No API key provided!")
            return {"success": False, "error": "No API key"}
        
        unit_group = "us" if units == "fahrenheit" else "metric"
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}"
        params = {
            "key": self.api_key,
            "unitGroup": unit_group,
            "include": "current",
            "contentType": "json"
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            current = data["currentConditions"]
            
            result = {
                "success": True,
                "provider": "Visual Crossing",
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
                "timestamp": current.get("datetime", "N/A")
            }
            
            self.print_success("Visual Crossing API call successful!")
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                self.print_error("Invalid API key!")
                return {"success": False, "error": "Invalid API key", "status_code": 401}
            elif e.response.status_code == 400:
                self.print_error(f"Bad request - City '{city}' might be invalid")
                return {"success": False, "error": "Bad request", "status_code": 400}
            else:
                self.print_error(f"HTTP error: {e.response.status_code}")
                return {"success": False, "error": str(e), "status_code": e.response.status_code}
        
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def display_weather_data(self, data: Dict[str, Any]):
        """Display weather data in a pretty format"""
        if not data.get("success"):
            self.print_error(f"Failed: {data.get('error', 'Unknown error')}")
            return
        
        print(f"\n{Colors.OKBLUE}{Colors.BOLD}Weather Information:{Colors.ENDC}")
        print(f"{Colors.BOLD}{'─'*80}{Colors.ENDC}")
        
        # Basic info
        print(f"📍 Location: {Colors.BOLD}{data.get('city')}{Colors.ENDC}", end="")
        if data.get('country'):
            print(f", {data.get('country')}")
        else:
            print()
        
        if data.get('region'):
            print(f"   Region: {data.get('region')}")
        
        print(f"🌡️  Temperature: {Colors.BOLD}{data.get('temperature')}°{Colors.ENDC}", end="")
        if data.get('units') == 'celsius':
            print(" C")
        else:
            print(" F")
        
        print(f"🤔 Feels Like: {data.get('feels_like')}°")
        print(f"☁️  Condition: {Colors.BOLD}{data.get('condition')}{Colors.ENDC}")
        print(f"💧 Humidity: {data.get('humidity')}%")
        print(f"🌬️  Wind Speed: {data.get('wind_speed')} {'km/h' if data.get('units') == 'celsius' else 'mph'}")
        
        if data.get('wind_direction'):
            print(f"🧭 Wind Direction: {data.get('wind_direction')}")
        
        print(f"📊 Pressure: {data.get('pressure')} mb")
        print(f"☁️  Cloud Cover: {data.get('clouds')}%")
        print(f"👁️  Visibility: {data.get('visibility')}")
        
        if data.get('uv_index'):
            print(f"☀️  UV Index: {data.get('uv_index')}")
        
        print(f"\n⏰ Last Updated: {data.get('timestamp', data.get('last_updated', 'N/A'))}")
        print(f"🔌 Provider: {Colors.OKCYAN}{data.get('provider')}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'─'*80}{Colors.ENDC}\n")
    
    async def run_comprehensive_test(self, city: str = "London", units: str = "celsius"):
        """Run comprehensive test of weather API"""
        self.print_header("Weather API Comprehensive Test")
        
        # Check environment
        self.print_info("Checking environment...")
        if self.api_key:
            self.print_success(f"API key found: {self.api_key[:8]}...")
        else:
            self.print_warning("No API key found in environment or parameter")
            self.print_info("Set WEATHER_API_KEY environment variable or pass --api-key")
            return
        
        print(f"\nProvider: {Colors.BOLD}{self.provider}{Colors.ENDC}")
        print(f"City: {Colors.BOLD}{city}{Colors.ENDC}")
        print(f"Units: {Colors.BOLD}{units}{Colors.ENDC}\n")
        
        # Test the selected provider
        if self.provider == "openweathermap":
            result = await self.test_openweathermap(city, units)
        elif self.provider == "weatherapi":
            result = await self.test_weatherapi(city, units)
        elif self.provider == "visualcrossing":
            result = await self.test_visualcrossing(city, units)
        else:
            self.print_error(f"Unknown provider: {self.provider}")
            self.print_info("Available providers: openweathermap, weatherapi, visualcrossing")
            return
        
        # Display results
        self.display_weather_data(result)
        
        # Save to file
        if result.get("success"):
            filename = f"weather_test_{city.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
            self.print_success(f"Results saved to: {filename}")
    
    async def test_all_providers(self, city: str = "London", units: str = "celsius"):
        """Test all weather API providers"""
        self.print_header("Testing All Weather API Providers")
        
        if not self.api_key:
            self.print_error("No API key provided!")
            return
        
        providers = ["openweathermap", "weatherapi", "visualcrossing"]
        results = {}
        
        for provider in providers:
            self.provider = provider
            print(f"\n{Colors.BOLD}Testing {provider.upper()}...{Colors.ENDC}")
            print(f"{Colors.BOLD}{'─'*80}{Colors.ENDC}")
            
            if provider == "openweathermap":
                result = await self.test_openweathermap(city, units)
            elif provider == "weatherapi":
                result = await self.test_weatherapi(city, units)
            elif provider == "visualcrossing":
                result = await self.test_visualcrossing(city, units)
            
            results[provider] = result
            self.display_weather_data(result)
            
            await asyncio.sleep(1)  # Rate limiting
        
        # Summary
        self.print_header("Test Summary")
        for provider, result in results.items():
            status = "✓ SUCCESS" if result.get("success") else "✗ FAILED"
            color = Colors.OKGREEN if result.get("success") else Colors.FAIL
            print(f"{color}{provider.upper()}: {status}{Colors.ENDC}")
            if not result.get("success"):
                print(f"  Error: {result.get('error')}")
        print()
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test weather API integration")
    parser.add_argument("--city", type=str, default="London", help="City name (default: London)")
    parser.add_argument("--units", type=str, choices=["celsius", "fahrenheit"], default="celsius", help="Temperature units")
    parser.add_argument("--provider", type=str, choices=["openweathermap", "weatherapi", "visualcrossing"], 
                       default="openweathermap", help="Weather API provider")
    parser.add_argument("--api-key", type=str, help="API key (or set WEATHER_API_KEY env var)")
    parser.add_argument("--test-all", action="store_true", help="Test all providers")
    
    args = parser.parse_args()
    
    tester = WeatherAPITester(api_key=os.getenv("WEATHER_API_KEY"), provider=args.provider)
    
    try:
        if args.test_all:
            await tester.test_all_providers(args.city, args.units)
        else:
            await tester.run_comprehensive_test(args.city, args.units)
    finally:
        await tester.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
        sys.exit(0)