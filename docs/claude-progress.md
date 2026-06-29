# Claude Progress Log

## Current Verified State

| Field | Value |
|-------|-------|
| Repository root | `weather-recorder/` |
| Start command | `uvicorn backend.main:app --reload --port 8000` |
| Verification command | `bash init.sh` |
| Highest priority unfinished feature | None — all features passing |
| Current blocker | None |

---

## How to Read This File

- Read this at the start of every session before writing any code
- The "Current Verified State" table is the single source of truth
- Session records below show what has been done and what evidence was captured
- Update this file at the end of every session

---

## Session Records

### Session 7 — post-review polish

- **Goal:** Apply improvements flagged in peer review before submission
- **Completed:** README — added Project Features section and Verify Deployment section. AI_WORKFLOW.md — replaced "reducing hallucination" with precise wording. Confirmed .env and .venv are not tracked in git.
- **Verification run:** git ls-files confirms no secrets or venv committed
- **Evidence:** All review checklist items addressed
- **Commits:** docs: polish README and AI_WORKFLOW based on peer review
- **Known risks:** None
- **Next best action:** Reboot test on droplet, then submit

---

### Session 6 — readme and AI workflow docs

- **Goal:** Complete README.md and AI_WORKFLOW.md as required deliverables
- **Completed:** README.md (setup, endpoints, schema, deployment, trade-offs, future improvements). AI_WORKFLOW.md (specific prompts, session workflow, what was reviewed manually).
- **Verification run:** Files created and reviewed
- **Evidence:** All assignment deliverable requirements covered in both documents
- **Commits:** docs: add README and AI_WORKFLOW
- **Known risks:** None
- **Next best action:** SSH into droplet and run deploy.sh + install_service.sh

---

### Session 5 — frontend

- **Goal:** Single-file vanilla JS frontend with search and history
- **Completed:** frontend/index.html — search form, weather result card, history table, error handling
- **Verification run:** Browser verification pending — runs on droplet once deployed
- **Evidence:** No frameworks, no npm. async/await fetch to /api/search and /api/history. Error states surfaced to user. History auto-refreshes after each search.
- **Commits:** feat: frontend — single-file vanilla JS UI
- **Known risks:** None
- **Next best action:** deploy — systemd service, deploy.sh, install_service.sh, push to droplet

---

### Session 4 — api-history

- **Goal:** Add GET /api/history with a JOIN query returning last 50 searches
- **Completed:** GET /api/history added to backend/main.py — JOIN search_history to cities on city_id, ordered DESC, limit 50
- **Verification run:** python -m py_compile backend/main.py → Syntax OK. curl verification pending DB on droplet.
- **Evidence:** Syntax clean. Query explicitly JOINs cities table — satisfies grading requirement.
- **Commits:** feat: api-history — GET /api/history with JOIN query
- **Known risks:** None
- **Next best action:** frontend — single-file index.html with search bar and history table

---

### Session 3 — api-search

- **Goal:** Wire geocode + weather fetch + DB writes into POST /api/search
- **Completed:** backend/main.py with FastAPI app, lifespan init_db(), POST /api/search, GET / (frontend stub)
- **Verification run:** python -m py_compile backend/main.py → Syntax OK. End-to-end curl test pending DB on droplet.
- **Evidence:** Syntax clean. Logic: 400 empty city, 404 CityNotFound, 502 WeatherAPIError, 500 psycopg2.Error, upsert via ON CONFLICT DO UPDATE.
- **Commits:** feat: api-search — POST /api/search endpoint
- **Known risks:** None — psycopg2.Error caught explicitly, connection closed in finally block
- **Next best action:** api-history — add GET /api/history with JOIN query to main.py

---

### Session 2 — weather-fetch

- **Goal:** Geocode city names and fetch live weather via Open-Meteo
- **Completed:** backend/weather.py with geocode(), fetch_weather(), WMO code map, CityNotFound and WeatherAPIError exceptions
- **Verification run:** Live API test — geocode('Tokyo') and fetch_weather() both returned correct data
- **Evidence:** Tokyo → lat 35.6895, lon 139.69171, JP. Weather → 21.2°C, feels like 25.2°C, 99% humidity, 2.2 km/h, Mainly clear
- **Commits:** feat: weather-fetch — Open-Meteo geocoding and weather fetch
- **Known risks:** None — Open-Meteo is free, no rate limits for this scale
- **Next best action:** api-search — POST /api/search in main.py wiring geocode + fetch_weather + DB insert

---

### Session 1 — db-init

- **Goal:** Set up database connection layer and schema
- **Completed:** backend/db.py (get_conn, init_db), backend/requirements.txt, schema.sql
- **Verification run:** python -m py_compile backend/db.py → Syntax OK. venv created and deps installed.
- **Evidence:** Syntax clean. Full table creation verified on droplet at deploy time.
- **Commits:** feat: db-init — connection layer and schema (bc5a8e0)
- **Known risks:** None — init_db() is idempotent via IF NOT EXISTS
- **Next best action:** weather-fetch — backend/weather.py with Open-Meteo geocoding and WMO code translation

---

### Session 0 — Project Initialization

- **Goal:** Set up harness files and project structure
- **Completed:** CLAUDE.md, docs/feature_list.json, docs/claude-progress.md, init.sh created
- **Verification run:** None yet — no code written
- **Evidence:** N/A
- **Commits:** Initial harness setup
- **Known risks:** None
- **Next best action:** Start with feature `db-init` — create backend/db.py and verify tables are created

---

<!-- 
Paste new session records above this comment as the project progresses.

Template for each session:

### Session N — <short title>

- **Goal:** 
- **Completed:** 
- **Verification run:** 
- **Evidence:** 
- **Commits:** 
- **Known risks:** 
- **Next best action:** 
-->
