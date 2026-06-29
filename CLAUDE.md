# Weather Recorder — Claude Code Instructions

## Startup Routine

Every session must begin with these steps in order:

1. Read `docs/claude-progress.md` to understand where the project stands
2. Read `docs/feature_list.json` to find the highest priority `not_started` feature
3. Run `bash init.sh` to verify the environment is working
4. Begin work on exactly one feature

Do not skip the startup routine. Do not start writing code before reading progress.

---

## Project Goal

Build a weather recorder web app where a user can:
- Search for weather by city name
- See the current conditions returned
- View a history of past searches

---

## Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Vanilla HTML, CSS, JavaScript — single file preferred
- **Database:** PostgreSQL with raw psycopg2 — no ORM, no SQLAlchemy
- **Weather API:** Open-Meteo (free, no API key required)

---

## Project Structure to Build

```
weather-recorder/
├── CLAUDE.md
├── init.sh
├── .env.example
├── .gitignore
├── backend/
│   ├── main.py
│   ├── db.py
│   ├── weather.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── schema.sql
├── weather-recorder.service
├── README.md
└── docs/
    ├── claude-progress.md
    └── feature_list.json
```

---

## Database Schema

Two tables. Raw SQL only. Use this exactly.

```sql
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
```

---

## API Endpoints

```
POST /api/search    Geocode city, fetch weather, save to DB, return result
GET  /api/history   Return last 50 searches — must use a JOIN on cities
GET  /              Serve the frontend
```

---

## Error Handling

Every endpoint must return correct HTTP status codes:

- 400 — missing or empty city name
- 404 — city not found by geocoder
- 502 — Open-Meteo API failure or timeout
- 500 — database error

---

## Working Rules

- Work on one feature at a time
- After writing any Python file, verify syntax: python -m py_compile <file>
- After each feature is complete, update docs/feature_list.json status to passing
- After each feature is complete, write a session entry in docs/claude-progress.md
- Do not add features that are not in feature_list.json
- Do not mark a feature passing without actually running it

---

## Definition of Done

The project is complete when:

- bash init.sh runs without errors
- POST /api/search with a valid city returns weather data and saves to DB
- GET /api/history returns a list using a JOIN query
- The frontend loads at localhost:8000 and search works end to end
- All features in feature_list.json are marked passing
- docs/claude-progress.md is up to date
- README.md is complete

---

## End of Session Routine

Before ending every session:

1. Update docs/feature_list.json with current status of all features worked on
2. Write a new session entry in docs/claude-progress.md
3. Make sure no feature is left as in_progress unless it will continue next session

---

## Deployment

When all app features are passing locally, follow docs/deploy.md to deploy to the DigitalOcean droplet.

Claude Code must:
1. Create weather-recorder.service in the project root
2. Create scripts/deploy.sh and scripts/install_service.sh
3. Follow the step-by-step instructions in docs/deploy.md
4. Verify the app responds at http://137.184.108.210:8000/api/history
5. Verify the service survives a reboot
6. Update the deploy feature in docs/feature_list.json to passing with evidence

Do not mark the deploy feature passing until the live URL responds correctly.
