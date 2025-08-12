#!/bin/bash
set -e

(cd .. && ./nx infra:test invest_agent)

# Wait for test integration DB to be started
echo "Waiting Database..."
sleep 5

(cd .. && ./nx migration:test:run invest_agent)

env-cmd -f .env.test poetry run python -m invest_agent.main &
API_PID=$!

../script/wait_agent_start.sh

env-cmd -f .env.test poetry run pytest -k "test_integration" "$@"
TEST_RESULT=$?

# Kill API
kill $API_PID
wait $API_PID 2>/dev/null

exit $TEST_RESULT