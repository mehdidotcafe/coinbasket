#!/bin/bash
set -e

PROJECT=$NX_TASK_TARGET_PROJECT

(cd .. && ./nx infra:test $PROJECT)
# Wait for test integration DB to be started
echo "Waiting Database..."
sleep 5


(cd .. && ./nx migration:test:run $PROJECT)
env-cmd -f .env.test poetry run python -m $PROJECT.worker &
WORKER_PID=$!

(cd .. && ./nx start:test api &)
API_PID=$!

../script/wait_api_start.sh

env-cmd -f .env.test poetry run pytest -k "test_integration" "$@"
TEST_RESULT=$?


(cd .. && ./nx infra:test:down $PROJECT)

# Kill Worker
kill $WORKER_PID

# Kill API
kill $API_PID

exit $TEST_RESULT