"""
Look up a city with Open-Meteo's geocoding API, then fetch current weather
for its coordinates. Raw httpx only, Pydantic models for validation,
exponential backoff on transient failures.
"""

import sys
import time
import httpx
from config import settings
from models import GeocodingResponse, ForecastResponse

# Weather codes -> plain-English description (WMO code table, abridged)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _request_with_retry(client: httpx.Client, url: str, params: dict) -> httpx.Response:
    """GET with exponential backoff on 429/5xx and network errors."""
    last_exc = None
    for attempt in range(settings.max_retries):
        try:
            response = client.get(url, params=params)
            if response.status_code == 429 or response.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"Retryable status {response.status_code}",
                    request=response.request,
                    response=response,
                )
            response.raise_for_status()
            return response
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            last_exc = exc
            wait = 2 ** attempt  # 1s, 2s, 4s...
            print(f"  Request failed ({exc}), retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Request failed after {settings.max_retries} attempts") from last_exc


def geocode_city(client: httpx.Client, city_name: str) -> GeocodingResponse:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    response = _request_with_retry(client, url, {"name": city_name, "count": 1})
    return GeocodingResponse.model_validate(response.json())


def get_current_weather(client: httpx.Client, latitude: float, longitude: float) -> ForecastResponse:
    url = f"{settings.open_meteo_base_url}/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
    }
    response = _request_with_retry(client, url, params)
    return ForecastResponse.model_validate(response.json())


def main(city_name: str):
    with httpx.Client(timeout=settings.request_timeout_seconds) as client:
        print(f"Looking up '{city_name}'...")
        geo = geocode_city(client, city_name)

        if not geo.results:
            print(f"No location found for '{city_name}'.")
            return

        place = geo.results[0]
        location_label = f"{place.name}" + (f", {place.admin1}" if place.admin1 else "") + (f", {place.country}" if place.country else "")
        print(f"Found: {location_label} ({place.latitude}, {place.longitude})\n")

        forecast = get_current_weather(client, place.latitude, place.longitude)
        c = forecast.current
        description = WEATHER_CODES.get(c.weather_code, "Unknown conditions")

        print(f"Current weather in {location_label}:")
        print(f"  Conditions:  {description}")
        print(f"  Temperature: {c.temperature_2m}°C (feels like {c.apparent_temperature}°C)")
        print(f"  Humidity:    {c.relative_humidity_2m}%")
        print(f"  Wind speed:  {c.wind_speed_10m} km/h")
        print(f"  As of:       {c.time} ({forecast.timezone})")


if __name__ == "__main__":
    city = sys.argv[1] if len(sys.argv) > 1 else "Chennai"
    main(city)