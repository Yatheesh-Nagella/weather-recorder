#!/usr/bin/env bash
# Run this ON THE DROPLET after deploy.sh completes.
# Must be run from /tmp/weather-recorder (project root).
set -euo pipefail

cp weather-recorder.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable weather-recorder
systemctl restart weather-recorder
systemctl status weather-recorder --no-pager
