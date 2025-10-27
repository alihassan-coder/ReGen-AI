import requests
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from config.env_config import EnvironmentConfig

class WeatherData(BaseModel):
    """Weather data model"""
    temperature: float = Field(description="Temperature in Celsius")
    humidity: int = Field(description="Humidity percentage")
    description: str = Field(description="Weather description")
    wind_speed: float = Field(description="Wind speed in m/s")
    pressure: float = Field(description="Atmospheric pressure in hPa")

class AirQualityData(BaseModel):
    """Air quality data model"""
    aqi: int = Field(description="Air Quality Index")
    pm25: float = Field(description="PM2.5 concentration")
    pm10: float = Field(description="PM10 concentration")
    o3: float = Field(description="Ozone concentration")
    no2: float = Field(description="Nitrogen dioxide concentration")
    so2: float = Field(description="Sulfur dioxide concentration")
    co: float = Field(description="Carbon monoxide concentration")

class ClimateAction(BaseModel):
    """Climate action recommendation model"""
    action: str = Field(description="Recommended climate action")
    impact: str = Field(description="Expected environmental impact")
    difficulty: str = Field(description="Implementation difficulty (Easy/Medium/Hard)")
    cost: str = Field(description="Cost level (Free/Low/Medium/High)")
    timeframe: str = Field(description="Time to implement")

def get_weather_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get current weather data for a specific location
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary containing weather information
    """
    api_key = EnvironmentConfig.OPENWEATHER_API_KEY
    if not api_key:
        return {"error": "OpenWeather API key not configured"}
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "city": data["name"],
            "country": data["sys"]["country"]
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}
    except KeyError as e:
        return {"error": f"Unexpected weather data format: {str(e)}"}

def get_air_quality_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get air quality data for a specific location
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary containing air quality information
    """
    api_key = EnvironmentConfig.AIRVISUAL_API_KEY
    if not api_key:
        return {"error": "AirVisual API key not configured"}
    
    try:
        url = f"http://api.airvisual.com/v2/nearest_city"
        params = {
            "lat": latitude,
            "lon": longitude,
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data["status"] == "success":
            pollution = data["data"]["current"]["pollution"]
            return {
                "aqi": pollution["aqius"],
                "pm25": pollution.get("pm25", 0),
                "pm10": pollution.get("pm10", 0),
                "o3": pollution.get("o3", 0),
                "no2": pollution.get("no2", 0),
                "so2": pollution.get("so2", 0),
                "co": pollution.get("co", 0),
                "city": data["data"]["city"],
                "country": data["data"]["country"]
            }
        else:
            return {"error": "Failed to fetch air quality data"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch air quality data: {str(e)}"}
    except KeyError as e:
        return {"error": f"Unexpected air quality data format: {str(e)}"}

def calculate_carbon_footprint(activity: str, value: float, unit: str = "kg") -> Dict[str, Any]:
    """
    Calculate carbon footprint for various activities
    
    Args:
        activity: Type of activity (driving, flying, electricity, etc.)
        value: Amount or distance
        unit: Unit of measurement
        
    Returns:
        Dictionary containing carbon footprint calculation
    """
    # Simplified carbon footprint calculations (in kg CO2)
    carbon_factors = {
        "driving": 0.192,  # kg CO2 per km
        "flying": 0.285,   # kg CO2 per km
        "electricity": 0.4,  # kg CO2 per kWh
        "natural_gas": 0.2,  # kg CO2 per kWh
        "meat": 27,        # kg CO2 per kg
        "vegetables": 2,   # kg CO2 per kg
        "plastic": 3.5,    # kg CO2 per kg
    }
    
    if activity.lower() not in carbon_factors:
        return {"error": f"Activity '{activity}' not supported"}
    
    factor = carbon_factors[activity.lower()]
    carbon_footprint = value * factor
    
    return {
        "activity": activity,
        "value": value,
        "unit": unit,
        "carbon_footprint_kg": round(carbon_footprint, 2),
        "equivalent_trees": round(carbon_footprint / 22, 2),  # 1 tree absorbs ~22kg CO2/year
        "equivalent_car_km": round(carbon_footprint / 0.192, 2)
    }

def get_climate_actions(weather_data: Dict[str, Any], air_quality: Dict[str, Any], 
                       user_preferences: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Generate personalized climate action recommendations based on local conditions
    
    Args:
        weather_data: Current weather information
        air_quality: Current air quality information
        user_preferences: Optional user preferences and constraints
        
    Returns:
        List of climate action recommendations
    """
    actions = []
    
    # Weather-based recommendations
    if "temperature" in weather_data:
        temp = weather_data["temperature"]
        if temp > 30:
            actions.append({
                "action": "Use energy-efficient cooling strategies",
                "impact": "Reduce electricity consumption by 20-30%",
                "difficulty": "Easy",
                "cost": "Low",
                "timeframe": "Immediate",
                "reason": f"High temperature ({temp}°C) increases cooling demand"
            })
        elif temp < 10:
            actions.append({
                "action": "Improve home insulation",
                "impact": "Reduce heating energy by 15-25%",
                "difficulty": "Medium",
                "cost": "Medium",
                "timeframe": "1-2 weeks",
                "reason": f"Low temperature ({temp}°C) increases heating demand"
            })
    
    # Air quality-based recommendations
    if "aqi" in air_quality:
        aqi = air_quality["aqi"]
        if aqi > 100:
            actions.append({
                "action": "Use air purifiers and limit outdoor activities",
                "impact": "Protect health and reduce exposure to pollutants",
                "difficulty": "Easy",
                "cost": "Medium",
                "timeframe": "Immediate",
                "reason": f"Poor air quality (AQI: {aqi}) detected"
            })
            actions.append({
                "action": "Use public transportation or electric vehicles",
                "impact": "Reduce local air pollution by 40-60%",
                "difficulty": "Medium",
                "cost": "Low",
                "timeframe": "1-3 days",
                "reason": f"Transportation contributes to air pollution (AQI: {aqi})"
            })
    
    # General climate actions
    actions.extend([
        {
            "action": "Switch to LED light bulbs",
            "impact": "Reduce electricity consumption by 80%",
            "difficulty": "Easy",
            "cost": "Low",
            "timeframe": "1 day",
            "reason": "Universal energy efficiency improvement"
        },
        {
            "action": "Install a programmable thermostat",
            "impact": "Reduce heating/cooling costs by 10-15%",
            "difficulty": "Medium",
            "cost": "Medium",
            "timeframe": "1 week",
            "reason": "Optimize temperature control"
        },
        {
            "action": "Start a small vegetable garden",
            "impact": "Reduce food miles and packaging waste",
            "difficulty": "Medium",
            "cost": "Low",
            "timeframe": "2-4 weeks",
            "reason": "Promote sustainable food production"
        }
    ])
    
    return actions[:5]  # Return top 5 recommendations

def get_eco_tips_by_season(month: int) -> List[str]:
    """
    Get seasonal eco-friendly tips
    
    Args:
        month: Month number (1-12)
        
    Returns:
        List of seasonal eco tips
    """
    seasonal_tips = {
        1: ["Use draft stoppers for doors", "Insulate water heater", "Use natural light during short days"],
        2: ["Check home insulation", "Use energy-efficient heating", "Plan spring garden"],
        3: ["Start composting", "Clean air filters", "Prepare for spring planting"],
        4: ["Plant native flowers", "Clean gutters", "Check for air leaks"],
        5: ["Start vegetable garden", "Use natural cleaning products", "Bike to work"],
        6: ["Use fans instead of AC", "Harvest rainwater", "Plant trees"],
        7: ["Use natural ventilation", "Eat seasonal produce", "Reduce water usage"],
        8: ["Use solar power", "Preserve summer produce", "Use public transport"],
        9: ["Harvest garden", "Prepare for winter", "Use natural light"],
        10: ["Insulate windows", "Clean heating systems", "Plant fall crops"],
        11: ["Use programmable thermostat", "Seal air leaks", "Prepare for winter"],
        12: ["Use LED holiday lights", "Recycle wrapping paper", "Conserve energy"]
    }
    
    return seasonal_tips.get(month, ["Check energy efficiency", "Reduce waste", "Use sustainable products"])