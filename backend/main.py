import psycopg2
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.db import get_conn, init_db
from backend.weather import CityNotFound, WeatherAPIError, fetch_weather, geocode, suggest

load_dotenv()

FRONTEND = Path(__file__).parent.parent / "frontend" / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class SearchRequest(BaseModel):
    city: str
    latitude: float | None = None
    longitude: float | None = None
    country: str | None = None
    admin1: str | None = None


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND)


@app.get("/api/suggest")
async def suggest_cities(q: str = ""):
    if len(q.strip()) < 2:
        return []
    try:
        return await suggest(q.strip())
    except WeatherAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/api/history")
def history():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.name          AS city,
                    c.admin1,
                    c.country,
                    sh.temperature_c,
                    sh.feels_like_c,
                    sh.humidity_pct,
                    sh.wind_speed_kmh,
                    sh.weather_desc,
                    sh.searched_at
                FROM search_history sh
                JOIN cities c ON c.id = sh.city_id
                ORDER BY sh.searched_at DESC
                LIMIT 50
                """
            )
            rows = cur.fetchall()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()

    return [dict(row) for row in rows]


@app.post("/api/search")
async def search(req: SearchRequest):
    if not req.city.strip():
        raise HTTPException(status_code=400, detail="city is required")

    if req.latitude is not None and req.longitude is not None:
        location = {
            "name": req.city,
            "admin1": req.admin1,
            "country": req.country,
            "latitude": req.latitude,
            "longitude": req.longitude,
        }
    else:
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
                    INSERT INTO cities (name, admin1, country, latitude, longitude)
                    VALUES (%(name)s, %(admin1)s, %(country)s, %(latitude)s, %(longitude)s)
                    ON CONFLICT (name, country) DO UPDATE
                        SET admin1    = EXCLUDED.admin1,
                            latitude  = EXCLUDED.latitude,
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
        "admin1": location.get("admin1"),
        "country": location["country"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "searched_at": searched_at,
        **weather,
    }
