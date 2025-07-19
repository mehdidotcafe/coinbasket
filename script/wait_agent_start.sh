#!/bin/bash
export $(grep -v '^#' .env.test | xargs)

echo "Waiting for Agent to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:$AGENT_PORT/health >/dev/null; then
    echo "Agent is up."
    break
  fi
  echo "Waiting..."
  sleep 1
done
