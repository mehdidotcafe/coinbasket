import json
from typing import Any, cast

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


def concat_text_deltas(events: list[Any]) -> str:
    return "".join(
        e["delta"]
        for e in events
        if isinstance(e, dict) and e.get("type") == "text-delta"
    )


def parse_sse_chunks(chunks: list[str]) -> list[Any]:
    events: list[Any] = []
    for chunk in chunks:
        line = chunk.strip()
        if line.startswith("data: "):
            payload = line[len("data: ") :]
            try:
                events.append(json.loads(payload))
            except json.JSONDecodeError:
                events.append(payload)
    return events


def find_event(events: list[Any], event_type: str) -> dict[str, Any] | None:
    for e in events:
        event = cast(dict[str, Any], e)
        if isinstance(e, dict) and event.get("type") == event_type:
            return event
    return None


def find_events(events: list[Any], event_type: str) -> list[dict[str, Any]]:
    return [
        cast(dict[str, Any], e)
        for e in events
        if isinstance(e, dict) and cast(dict[str, Any], e).get("type") == event_type
    ]


def find_data_interrupt(events: list[Any]) -> dict[str, Any] | None:
    return find_event(events, "data-interrupt")
