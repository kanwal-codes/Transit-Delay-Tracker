"""
Weather Integration Module
Integrates weather data to improve delay predictions
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class WeatherIntegration:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo_key"  # Use demo data if no API key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.toronto_coords = {"lat": 43.6532, "lon": -79.3832}
        
    def get_current_weather(self) -> Dict:
        """
        Get current weather data for Toronto
        """
        if self.api_key == "demo_key":
            return self._generate_mock_weather()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": self.toronto_coords["lat"],
                "lon": self.toronto_coords["lon"],
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._process_weather_data(data)
            
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return self._generate_mock_weather()
    
    def get_weather_forecast(self, days: int = 5) -> pd.DataFrame:
        """
        Get weather forecast for the next few days
        """
        if self.api_key == "demo_key":
            return self._generate_mock_forecast(days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": self.toronto_coords["lat"],
                "lon": self.toronto_coords["lon"],
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._process_forecast_data(data)
            
        except Exception as e:
            logger.error(f"Weather forecast API error: {e}")
            return self._generate_mock_forecast(days)
    
    def _process_weather_data(self, data: Dict) -> Dict:
        """Process raw weather API data"""
        return {
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "visibility": data.get("visibility", 10000),
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"].get("deg", 0),
            "weather_main": data["weather"][0]["main"],
            "weather_description": data["weather"][0]["description"],
            "clouds": data["clouds"]["all"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_forecast_data(self, data: Dict) -> pd.DataFrame:
        """Process weather forecast data"""
        forecasts = []
        
        for item in data["list"]:
            forecast = {
                "timestamp": datetime.fromtimestamp(item["dt"]).isoformat(),
                "temperature": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "wind_speed": item["wind"]["speed"],
                "weather_main": item["weather"][0]["main"],
                "weather_description": item["weather"][0]["description"],
                "clouds": item["clouds"]["all"],
                "precipitation_probability": item.get("pop", 0) * 100
            }
            forecasts.append(forecast)
        
        return pd.DataFrame(forecasts)
    
    def _generate_mock_weather(self) -> Dict:
        """Generate realistic mock weather data"""
        np.random.seed(42)
        
        # Seasonal temperature variation
        month = datetime.now().month
        base_temp = 20 - 15 * np.cos(2 * np.pi * month / 12)  # Seasonal variation
        
        weather_conditions = [
            "Clear", "Clouds", "Rain", "Snow", "Mist", "Fog"
        ]
        
        condition = np.random.choice(weather_conditions)
        
        return {
            "temperature": round(base_temp + np.random.normal(0, 3), 1),
            "feels_like": round(base_temp + np.random.normal(0, 2), 1),
            "humidity": np.random.randint(30, 90),
            "pressure": np.random.randint(1000, 1030),
            "visibility": np.random.randint(5000, 15000),
            "wind_speed": round(np.random.exponential(2), 1),
            "wind_direction": np.random.randint(0, 360),
            "weather_main": condition,
            "weather_description": f"{condition.lower()} conditions",
            "clouds": np.random.randint(0, 100),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_mock_forecast(self, days: int) -> pd.DataFrame:
        """Generate mock weather forecast"""
        forecasts = []
        current_time = datetime.now()
        
        for i in range(days * 8):  # 8 forecasts per day (3-hour intervals)
            timestamp = current_time + timedelta(hours=i * 3)
            
            # Add some variation to the forecast
            temp_variation = np.random.normal(0, 2)
            base_temp = 20 - 15 * np.cos(2 * np.pi * timestamp.month / 12)
            
            forecast = {
                "timestamp": timestamp.isoformat(),
                "temperature": round(base_temp + temp_variation, 1),
                "humidity": np.random.randint(40, 80),
                "pressure": np.random.randint(1005, 1025),
                "wind_speed": round(np.random.exponential(1.5), 1),
                "weather_main": np.random.choice(["Clear", "Clouds", "Rain"]),
                "weather_description": "Variable conditions",
                "clouds": np.random.randint(20, 80),
                "precipitation_probability": np.random.randint(0, 60)
            }
            forecasts.append(forecast)
        
        return pd.DataFrame(forecasts)
    
    def calculate_weather_impact(self, weather_data: Dict) -> float:
        """
        Calculate weather impact factor on transit delays
        Returns multiplier (1.0 = no impact, >1.0 = increased delays)
        """
        impact = 1.0
        
        # Temperature impact
        temp = weather_data["temperature"]
        if temp < -10:  # Very cold
            impact += 0.3
        elif temp < 0:  # Cold
            impact += 0.2
        elif temp > 30:  # Very hot
            impact += 0.1
        
        # Precipitation impact
        weather_main = weather_data["weather_main"].lower()
        if "rain" in weather_main or "drizzle" in weather_main:
            impact += 0.4
        elif "snow" in weather_main:
            impact += 0.6
        elif "storm" in weather_main:
            impact += 0.8
        
        # Wind impact
        wind_speed = weather_data["wind_speed"]
        if wind_speed > 20:  # Strong wind
            impact += 0.2
        elif wind_speed > 15:  # Moderate wind
            impact += 0.1
        
        # Visibility impact
        visibility = weather_data.get("visibility", 10000)
        if visibility < 1000:  # Poor visibility
            impact += 0.3
        elif visibility < 5000:  # Reduced visibility
            impact += 0.1
        
        # Humidity impact (extreme humidity can affect equipment)
        humidity = weather_data["humidity"]
        if humidity > 90:  # Very high humidity
            impact += 0.1
        
        return min(impact, 3.0)  # Cap at 3x impact
    
    def get_weather_features(self, weather_data: Dict) -> Dict:
        """
        Extract weather features for ML models
        """
        return {
            "temperature": weather_data["temperature"],
            "humidity": weather_data["humidity"],
            "pressure": weather_data["pressure"],
            "wind_speed": weather_data["wind_speed"],
            "visibility": weather_data.get("visibility", 10000),
            "is_rainy": 1 if "rain" in weather_data["weather_main"].lower() else 0,
            "is_snowy": 1 if "snow" in weather_data["weather_main"].lower() else 0,
            "is_stormy": 1 if "storm" in weather_data["weather_main"].lower() else 0,
            "is_clear": 1 if weather_data["weather_main"].lower() == "clear" else 0,
            "weather_impact": self.calculate_weather_impact(weather_data)
        }
    
    def update_delay_data_with_weather(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add weather data to delay dataset
        """
        df_with_weather = df.copy()
        
        # Get current weather
        current_weather = self.get_current_weather()
        weather_features = self.get_weather_features(current_weather)
        
        # Add weather features to all rows
        for feature, value in weather_features.items():
            df_with_weather[feature] = value
        
        # Add weather timestamp
        df_with_weather['weather_timestamp'] = current_weather['timestamp']
        
        logger.info(f"Added weather data to {len(df_with_weather)} records")
        return df_with_weather

def main():
    """Test weather integration"""
    weather = WeatherIntegration()
    
    # Test current weather
    current = weather.get_current_weather()
    print("🌤️ Current Weather:")
    for key, value in current.items():
        print(f"   {key}: {value}")
    
    # Test weather impact
    impact = weather.calculate_weather_impact(current)
    print(f"\n🚌 Weather Impact on Delays: {impact:.2f}x")
    
    # Test forecast
    forecast = weather.get_weather_forecast(3)
    print(f"\n📅 Weather Forecast ({len(forecast)} records):")
    print(forecast.head())

if __name__ == "__main__":
    main()

