import psycopg2
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.db import get_conn, init_db
from backend.weather import CityNotFound, WeatherAPIError, fetch_weather, geocode

load_dotenv()

FRONTEND = Path(__file__).parent.parent / "frontend" / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class SearchRequest(BaseModel):
    city: str


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND)


@app.post("/api/search")
async def search(req: SearchRequest):
    if not req.city.strip():
        raise HTTPException(status_code=400, detail="city is required")

    try:
        location = await geocode(req.city)
    except CityNotFound:
        raise HTTPException(status_code=404, detail=f"City not found: {req.city}")
    except WeatherAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    try:
        weather = await fetch_weather(location["latitude"], location["longitude"])
    except WeatherAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cities (name, country, latitude, longitude)
                    VALUES (%(name)s, %(country)s, %(latitude)s, %(longitude)s)
                    ON CONFLICT (name, country) DO UPDATE
                        SET latitude  = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude
                    RETURNING id
                    """,
                    location,
                )
                city_id = cur.fetchone()["id"]

                cur.execute(
                    """
                    INSERT INTO search_history
                        (city_id, temperature_c, feels_like_c,
                         humidity_pct, wind_speed_kmh, weather_desc)
                    VALUES
                        (%(city_id)s, %(temperature_c)s, %(feels_like_c)s,
                         %(humidity_pct)s, %(wind_speed_kmh)s, %(weather_desc)s)
                    RETURNING searched_at
                    """,
                    {"city_id": city_id, **weather},
                )
                searched_at = cur.fetchone()["searched_at"]
    except psycopg2.Error as exc:
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()

    return {
        "city": location["name"],
        "country": location["country"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "searched_at": searched_at,
        **weather,
    }
