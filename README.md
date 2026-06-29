# Weather Recorder

A full-stack web app that searches for current weather by city name, saves results to PostgreSQL, and displays a history of past lookups.

**Live:** http://137.184.108.210:8000

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, uvicorn |
| Database | PostgreSQL 16, psycopg2 (raw SQL, no ORM) |
| Weather API | [Open-Meteo](https://open-meteo.com) — free, no API key required |
| Frontend | Vanilla HTML, CSS, JavaScript — single file, no build step |
| Deployment | DigitalOcean Ubuntu 24 LTS, systemd |

---

## Local Setup

### Prerequisites

- Python 3.11+
- Docker (for local PostgreSQL) or a running PostgreSQL instance
- Git

### 1. Clone the repo

```bash
git clone https://github.com/Yatheesh-Nagella/weather-recorder.git
cd weather-recorder
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Start PostgreSQL via Docker

```bash
docker run --name weather-pg \
  -e POSTGRES_USER=weather \
  -e POSTGRES_PASSWORD=weather_local \
  -e POSTGRES_DB=weatherdb \
  -p 5432:5432 -d postgres:16
```

### 5. Configure environment

```bash
cp .env.example .env
# Edit .env and set DATABASE_URL to match your PostgreSQL credentials
```

`.env` for the Docker setup above:
```
DATABASE_URL=postgresql://weather:weather_local@localhost:5432/weatherdb
```

### 6. Run the app

```bash
uvicorn backend.main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend |
| `POST` | `/api/search` | Geocodes city, fetches weather, saves to DB |
| `GET` | `/api/history` | Returns last 50 searches (JOIN query) |

### POST /api/search

**Request:**
```json
{ "city": "London" }
```

**Response:**
```json
{
  "city": "London",
  "country": "GB",
  "latitude": 51.50853,
  "longitude": -0.12574,
  "temperature_c": 18.2,
  "feels_like_c": 17.5,
  "humidity_pct": 68,
  "wind_speed_kmh": 14.4,
  "weather_desc": "Partly cloudy",
  "searched_at": "2026-06-29T19:07:45.134037+00:00"
}
```

**Error codes:** `400` empty city · `404` city not found · `502` weather API failure · `500` database error

---

## Database Schema

Two tables with a foreign key relationship:

```sql
cities (id, name, country, latitude, longitude, created_at)
search_history (id, city_id → cities.id, searched_at, temperature_c,
                feels_like_c, humidity_pct, wind_speed_kmh, weather_desc)
```

History queries use a JOIN between both tables. Full schema in `schema.sql`.

---

## Server Deployment

The app runs on a DigitalOcean Ubuntu 24 LTS droplet as a systemd service.

### Deploy from scratch

```bash
# SSH into the server
ssh -p 29127 root@137.184.108.210

# Clone the repo
apt-get install -y git
git clone https://github.com/Yatheesh-Nagella/weather-recorder.git /tmp/weather-recorder
cd /tmp/weather-recorder

# Run setup (installs packages, PostgreSQL, venv)
DB_PASS=your_db_password bash scripts/deploy.sh

# Install and start the systemd service
bash scripts/install_service.sh
```

### Useful server commands

```bash
# View live logs
journalctl -u weather-recorder -f

# Restart after a code update
cd /tmp/weather-recorder && git pull
cp -r backend frontend /opt/weather-recorder/
systemctl restart weather-recorder

# Check service status
systemctl status weather-recorder
```

---

## AI Tools Used

This project was built using **Claude Code** (Anthropic's CLI) as the primary development tool.

Claude Code was used to:
- Design and scaffold the project structure
- Implement all backend modules (`db.py`, `weather.py`, `main.py`) feature by feature
- Write the frontend (`index.html`) with no frameworks
- Write deployment scripts and the systemd unit file
- Identify and fix a security issue (XSS via `innerHTML`) and an error handling gap (non-JSON API responses crashing the server)
- Write and update progress documentation throughout

See `AI_WORKFLOW.md` for a detailed account of specific prompts and workflows used.

---

## Assumptions and Trade-offs

| Decision | Reasoning |
|---|---|
| Open-Meteo for weather | Free, no API key, no rate limits at this scale, global coverage |
| Per-request DB connections | Simple and correct for this traffic level; a pool adds complexity without benefit here |
| LIMIT 50 for history | No pagination requirement in the spec; 50 rows covers all practical use |
| City name search only | Open-Meteo geocoder is name-based; zip code support would require a different geocoder |
| Single-file frontend | No build step, no dependencies, trivial to serve from FastAPI |
| `ON CONFLICT DO UPDATE` on cities | Same city searched multiple times stays one row in `cities`, many rows in `search_history` |
| Shared search history | All users see the same history feed — no authentication or session isolation. Per-session isolation would require auth or an anonymous session token. |
| `psycopg2-binary` | Bundles PostgreSQL client libs — no system-level dev headers needed |

---

## What I Would Improve With More Time

- **Pagination** on the history endpoint with configurable page size
- **Country disambiguation** — allow `"Paris, FR"` vs `"Paris, TX"` style input
- **Connection pooling** with `psycopg2.pool` or switch to `asyncpg` for async DB access
- **HTTPS** via nginx reverse proxy with Let's Encrypt
- **Unit and integration tests** for the API endpoints
- **City autocomplete** in the frontend using the Open-Meteo geocoding API
- **Temperature unit toggle** (°C / °F) in the UI
- **Response caching** — skip the weather API call if the same city was searched in the last 10 minutes
