#!/bin/bash
set -e

# Reset langgraph database
env-cmd -f .env.test --use-shell 'echo '' > "../invest_agent/database/$AGENT_ENV/$AGENT_NAME.langgraph.db"' 

env-cmd -f .env.test poetry run python -m invest_agent.main &
API_PID=$!

../script/wait_agent_start.sh

env-cmd -f .env.test poetry run pytest -k "test_integration" "$@"
TEST_RESULT=$?

# Kill API
kill $API_PID
wait $API_PID 2>/dev/null

exit $TEST_RESULT