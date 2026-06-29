#!/usr/bin/env bash
# Run this ON THE DROPLET from /tmp/weather-recorder after cloning the repo.
# Usage: DB_PASS=yourpassword bash scripts/deploy.sh
set -euo pipefail

if [ -z "${DB_PASS:-}" ]; then
  echo "ERROR: DB_PASS environment variable is required"
  echo "Usage: DB_PASS=yourpassword bash scripts/deploy.sh"
  exit 1
fi

APP_DIR="/opt/weather-recorder"
DB_NAME="weatherdb"
DB_USER="weather"

echo "--- [1/6] Installing system packages ---"
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv postgresql postgresql-contrib

echo "--- [2/6] Starting PostgreSQL ---"
systemctl enable --now postgresql

echo "--- [3/6] Creating DB user and database ---"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" \
  | grep -q 1 \
  || sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" \
  | grep -q 1 \
  || sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

echo "--- [4/6] Copying app files ---"
mkdir -p "${APP_DIR}"
cp -r backend frontend schema.sql "${APP_DIR}/"

echo "--- [5/6] Setting up Python venv ---"
python3 -m venv "${APP_DIR}/venv"
"${APP_DIR}/venv/bin/pip" install --quiet --upgrade pip
"${APP_DIR}/venv/bin/pip" install --quiet -r "${APP_DIR}/backend/requirements.txt"

echo "--- [6/6] Writing .env ---"
cat > "${APP_DIR}/.env" <<EOF
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}
EOF

echo ""
echo "=== Deploy complete. Run: bash scripts/install_service.sh ==="
