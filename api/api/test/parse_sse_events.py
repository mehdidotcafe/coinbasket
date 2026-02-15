import json
from typing import Any

import requests


def parse_sse_events(response: requests.Response) -> list[Any]:
    events: list[Any] = []
    for line in response.text.strip().split("\n"):
        line = line.strip()
        if line.startswith("data: "):
            payload = line[len("data: ") :]
            try:
                events.append(json.loads(payload))
            except json.JSONDecodeError:
                events.append(payload)
    return events
