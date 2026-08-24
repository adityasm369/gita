#!/bin/sh
d="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$d/data/pid" ]; then
  kill "$(cat "$d/data/pid")" 2>/dev/null && echo "stopped $(cat "$d/data/pid")"
  rm -f "$d/data/pid"
else
  echo "no pidfile"
fi
