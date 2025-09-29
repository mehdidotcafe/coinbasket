#!/bin/bash
set -e

PROJECT=$NX_TASK_TARGET_PROJECT

(cd .. && ./nx infra:test $PROJECT)
# Wait for test integration DB to be started
echo "Waiting Database..."
sleep 5


if [ "$PROJECT" = "invest_agent" ]; then
	(cd .. && ./nx migration:test:run $PROJECT)
fi

env-cmd -f .env.test poetry run python -m $PROJECT.main &
API_PID=$!

../script/wait_agent_start.sh

env-cmd -f .env.test poetry run pytest -k "test_integration" "$@"
TEST_RESULT=$?


(cd .. && ./nx infra:test:down $PROJECT)

# Kill API
kill $API_PID

exit $TEST_RESULT