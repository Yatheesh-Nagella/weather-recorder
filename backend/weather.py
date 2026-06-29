import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers", 81: "Showers", 82: "Heavy showers",
    85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


class CityNotFound(Exception):
    pass


class WeatherAPIError(Exception):
    pass


async def geocode(city: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                GEOCODING_URL,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
            )
            r.raise_for_status()
    except httpx.HTTPError as exc:
        raise WeatherAPIError(str(exc))

    results = r.json().get("results")
    if not results:
        raise CityNotFound(city)

    hit = results[0]
    return {
        "name": hit["name"],
        "country": hit.get("country_code"),
        "latitude": hit["latitude"],
        "longitude": hit["longitude"],
    }


async def fetch_weather(latitude: float, longitude: float) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        "wind_speed_unit": "kmh",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(WEATHER_URL, params=params)
            r.raise_for_status()
    except httpx.HTTPError as exc:
        raise WeatherAPIError(str(exc))

    current = r.json().get("current", {})
    code = current.get("weather_code", 0)
    return {
        "temperature_c": current.get("temperature_2m"),
        "feels_like_c": current.get("apparent_temperature"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_desc": WMO_CODES.get(code, f"Unknown ({code})"),
    }
