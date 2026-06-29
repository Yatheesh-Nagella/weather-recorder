# Deployment Guide — DigitalOcean Droplet

## Server Details

| Field        | Value                          |
|--------------|-------------------------------|
| IP Address   | 137.184.108.210               |
| SSH Port     | 29127                         |
| Username     | root                          |
| Password     | (see secure channel)          |
| OS           | Ubuntu 24 LTS                 |
| App installs to | /opt/weather-recorder      |
| App port     | 8000                          |
| DB name      | weatherdb                     |
| DB user      | weather                       |
| DB password  | (set in .env on server)       |

---

## What Claude Code Must Produce

Before deployment can run, these files must exist in the project:

- `weather-recorder.service` — systemd unit file
- `scripts/deploy.sh` — server setup script

Claude Code should create both files, then follow the manual deployment
steps below to get the app live.

---

## systemd Unit File

Create `weather-recorder.service` in the project root:

```ini
[Unit]
Description=Weather Recorder (FastAPI)
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/weather-recorder/backend
EnvironmentFile=/opt/weather-recorder/.env
ExecStart=/opt/weather-recorder/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## Server Setup Script

Create `scripts/deploy.sh`:

```bash
#!/usr/bin/env bash
# Run this ON THE DROPLET after copying the project there
set -euo pipefail

APP_DIR="/opt/weather-recorder"
DB_NAME="weatherdb"
DB_USER="weather"
DB_PASS="<YOUR_DB_PASSWORD>"  # set this before running

echo "--- [1/6] Installing system packages ---"
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv postgresql postgresql-contrib

echo "--- [2/6] Starting PostgreSQL ---"
systemctl enable --now postgresql

echo "--- [3/6] Creating DB user and database ---"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" \
  | grep -q 1 || sudo -u postgres psql -c \
  "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" \
  | grep -q 1 || sudo -u postgres psql -c \
  "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

echo "--- [4/6] Copying app files ---"
mkdir -p "${APP_DIR}"
cp -r backend frontend "${APP_DIR}/"

echo "--- [5/6] Setting up Python venv ---"
python3 -m venv "${APP_DIR}/venv"
"${APP_DIR}/venv/bin/pip" install --quiet --upgrade pip
"${APP_DIR}/venv/bin/pip" install --quiet -r "${APP_DIR}/backend/requirements.txt"

echo "--- [6/6] Writing .env ---"
cat > "${APP_DIR}/.env" <<EOF
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}
EOF

echo "Done. Now run: bash scripts/install_service.sh"
```

---

## Service Installation Script

Create `scripts/install_service.sh`:

```bash
#!/usr/bin/env bash
# Run this ON THE DROPLET after deploy.sh
set -euo pipefail

cp weather-recorder.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable weather-recorder
systemctl restart weather-recorder
systemctl status weather-recorder --no-pager
```

---

## Step-by-Step Deployment

### Step 1 — Push code to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/weather-recorder.git
git push -u origin main
```

### Step 2 — SSH into the droplet

```bash
ssh -p 29127 root@137.184.108.210
# Password: (see secure channel)
```

### Step 3 — Clone the repo on the server

```bash
apt-get install -y git
git clone https://github.com/YOUR_USERNAME/weather-recorder.git /tmp/weather-recorder
cd /tmp/weather-recorder
```

### Step 4 — Run the deploy script

```bash
bash scripts/deploy.sh
```

### Step 5 — Install the systemd service

```bash
bash scripts/install_service.sh
```

### Step 6 — Verify it is running

```bash
systemctl status weather-recorder
curl http://localhost:8000/api/history
```

### Step 7 — Verify it survives reboot

```bash
sudo reboot
# Wait 60 seconds, then SSH back in
ssh -p 29127 root@137.184.108.210
systemctl status weather-recorder
curl http://localhost:8000/api/history
```

### Step 8 — Verify from outside the server

From your local machine:

```bash
curl http://137.184.108.210:8000/api/history
```

---

## Useful Commands on the Server

```bash
# View live logs
journalctl -u weather-recorder -f

# Restart after a code change
cd /tmp/weather-recorder
git pull
cp -r backend frontend /opt/weather-recorder/
systemctl restart weather-recorder

# Check PostgreSQL
sudo -u postgres psql -d weatherdb -c "SELECT * FROM search_history LIMIT 5;"
```
