from unittest import mock
from uagents.storage import KeyValueStore
from jsonpickle import encode

from pytest import fixture

from invest_agent.infrastructure.fetch_ai.storage.fetch_ai_storage import FetchAiStorage


@fixture
def fetch_ai_store():
    return mock.Mock(spec=KeyValueStore)


@fixture
def storage(fetch_ai_store: KeyValueStore):
    return FetchAiStorage[str](store=fetch_ai_store, key_prefix="kp")


def test_get_with_decode(storage: FetchAiStorage[str], fetch_ai_store: KeyValueStore):
    fetch_ai_store.get.return_value = encode(["value", 2])
    result = storage.get("key")

    assert result == ("value", 2)
    fetch_ai_store.get.assert_called_once_with("kp:key")


def test_has(storage: FetchAiStorage[str], fetch_ai_store: KeyValueStore):
    fetch_ai_store.has.return_value = True
    result = storage.has("key")

    assert result is True
    fetch_ai_store.has.assert_called_once_with("kp:key")


def test_set_with_encode(storage: FetchAiStorage[str], fetch_ai_store: KeyValueStore):
    storage.set("key", "value", 2)
    fetch_ai_store.set.assert_called_once_with("kp:key", encode(["value", 2]))


def test_remove(storage: FetchAiStorage[str], fetch_ai_store: KeyValueStore):
    storage.remove("key")
    fetch_ai_store.remove.assert_called_once_with("kp:key")


def test_clear(storage: FetchAiStorage[str], fetch_ai_store: KeyValueStore):
    storage.clear()
    fetch_ai_store.clear.assert_called_once()
