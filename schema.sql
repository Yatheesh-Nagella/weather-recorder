CREATE TABLE IF NOT EXISTS cities (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(120) NOT NULL,
    country    VARCHAR(4),
    latitude   DOUBLE PRECISION NOT NULL,
    longitude  DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (name, country)
);

CREATE TABLE IF NOT EXISTS search_history (
    id             SERIAL PRIMARY KEY,
    city_id        INTEGER NOT NULL REFERENCES cities(id),
    searched_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    temperature_c  NUMERIC(5,2),
    feels_like_c   NUMERIC(5,2),
    humidity_pct   SMALLINT,
    wind_speed_kmh NUMERIC(6,2),
    weather_desc   VARCHAR(120)
);
