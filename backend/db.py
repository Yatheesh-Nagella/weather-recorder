import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cities (
                    id         SERIAL PRIMARY KEY,
                    name       VARCHAR(120) NOT NULL,
                    country    VARCHAR(4),
                    latitude   DOUBLE PRECISION NOT NULL,
                    longitude  DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (name, country)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id             SERIAL PRIMARY KEY,
                    city_id        INTEGER NOT NULL REFERENCES cities(id),
                    searched_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    temperature_c  NUMERIC(5,2),
                    feels_like_c   NUMERIC(5,2),
                    humidity_pct   SMALLINT,
                    wind_speed_kmh NUMERIC(6,2),
                    weather_desc   VARCHAR(120)
                )
            """)
        conn.commit()
