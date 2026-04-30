#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
CRON_ENTRY="0 8 * * * cd \"$SCRIPT_DIR\" && \"$PYTHON_BIN\" \"$SCRIPT_DIR/run_scheduled_job.py\" >> \"$SCRIPT_DIR/logs/cron.log\" 2>&1"

tmp_file="$(mktemp)"
crontab -l 2>/dev/null | grep -v "run_scheduled_job.py" > "$tmp_file" || true
printf '%s\n' "$CRON_ENTRY" >> "$tmp_file"
crontab "$tmp_file"
rm -f "$tmp_file"

printf 'Installed cron entry:\n%s\n' "$CRON_ENTRY"
