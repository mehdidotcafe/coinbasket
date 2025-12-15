#!/bin/bash
export $(grep -v '^#' .env.test | xargs)

echo "Waiting for API to be ready ..."
ready=0
for i in {1..120}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://localhost:$APP_PORT/health || true)
  if [ "$status" = "200" ]; then
    echo "API is up."
    ready=1
    break
  fi
  echo "($i) Waiting API..."
  sleep 1
done

if [ "$ready" -ne 1 ]; then
  echo "API is not up." >&2
  exit 1
fi
