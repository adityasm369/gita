#!/bin/sh
# gita launcher.
#   ./start.sh            -> loopback only (default, safe)
#   ./start.sh --expose   -> bind 0.0.0.0 so Traefik can reach it over the bridge
d="$(cd "$(dirname "$0")" && pwd)"
"$d/stop.sh" >/dev/null 2>&1
cd "$d" || exit 1

HOST=127.0.0.1
for a in "$@"; do
  case "$a" in
    --expose) HOST=0.0.0.0 ;;
    --host=*) HOST="${a#--host=}" ;;
  esac
done

mkdir -p "$d/data"
SS_ROOT="$d" SS_INDEX="dashboard.html" SS_SLUG="gita" SS_HOST="$HOST" SS_PORT="${SS_PORT:-8771}" \
  nohup python3 /data/projects/_shared/serve_static.py > "$d/data/server.log" 2>&1 &
echo $! > "$d/data/pid"
curl -s --retry 30 --retry-connrefused --retry-delay 1 --max-time 30 \
  "http://127.0.0.1:${SS_PORT:-8771}/healthz" >/dev/null 2>&1

if ! grep -q " on http" "$d/data/server.log" 2>/dev/null; then
  echo "failed to start:"; cat "$d/data/server.log"; exit 1
fi
echo "gita -> http://$HOST:${SS_PORT:-8771}"
exit 0
