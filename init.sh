#!/usr/bin/env bash
# init.sh — run this at the start of every session to verify the environment
set -e

INSTALL_CMD="pip install -r backend/requirements.txt"
VERIFY_CMD="python -m py_compile backend/db.py backend/weather.py backend/main.py"
START_CMD="uvicorn backend.main:app --reload --port 8000"

echo ""
echo "=== Weather Recorder — Environment Check ==="
echo "Working directory: $(pwd)"
echo ""

# 1. Check Python
echo "[1/4] Checking Python..."
python3 --version || { echo "ERROR: python3 not found"; exit 1; }

# 2. Check PostgreSQL connection
echo "[2/4] Checking DATABASE_URL..."
if [ -z "$DATABASE_URL" ]; then
  if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "      Loaded from .env"
  else
    echo "WARNING: DATABASE_URL not set and no .env found"
    echo "         Copy .env.example to .env and fill in your credentials"
  fi
fi

# 3. Install dependencies
echo "[3/4] Installing dependencies..."
$INSTALL_CMD

# 4. Verify syntax if backend files exist
echo "[4/4] Verifying syntax..."
if [ -f backend/main.py ]; then
  $VERIFY_CMD && echo "      Syntax OK"
else
  echo "      backend/main.py not written yet — skipping syntax check"
fi

echo ""
echo "=== Ready ==="
echo "Start server with: $START_CMD"
echo ""
