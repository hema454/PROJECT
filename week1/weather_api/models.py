from typing import Optional
from pydantic import BaseModel, Field


class GeocodingResult(BaseModel):
    """One matched location from the Open-Meteo geocoding API."""
    id: int
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    admin1: Optional[str] = None  # state/region, when available
    timezone: Optional[str] = None


class GeocodingResponse(BaseModel):
    results: Optional[list[GeocodingResult]] = None


class CurrentWeather(BaseModel):
    """The 'current' block from the Open-Meteo forecast API."""
    time: str
    temperature_2m: float = Field(..., description="Air temperature, deg C")
    apparent_temperature: float = Field(..., description="Feels-like temp, deg C")
    relative_humidity_2m: int
    wind_speed_10m: float
    weather_code: int


class ForecastResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    current: CurrentWeather