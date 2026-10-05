"""HTTP adapter contracts with synthetic stubs; no paid API/model score."""

import json
import urllib.error
from io import BytesIO

import pytest

from apps.assistant import llm, remote

pytestmark = pytest.mark.unit
MESSAGES = [
    {"role": "system", "content": "Sentetik araç seçimi"},
    {"role": "user", "content": "Sentetik rapor özeti"},
]
SELECTED = {"action": "summary", "topic": "", "year": None, "month": None}


def response(**changes):
    return {
        "content": [
            {"type": "tool_use", "id": "synthetic-call", "name": "route", "input": SELECTED}
        ],
        "stop_reason": "tool_use",
        "usage": {"input_tokens": 10, "output_tokens": 8},
        **changes,
    }


@pytest.fixture(autouse=True)
def no_real_http(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "synthetic-test-key")
    monkeypatch.setattr(
        remote.urllib.request, "urlopen", lambda *args, **kwargs: pytest.fail("real HTTP forbidden")
    )


def test_haiku_secret_is_required_before_http(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    with pytest.raises(llm.ModelUnavailable, match="secret eksik; çağrı yapılmadı"):
        remote.haiku_completion(messages=MESSAGES, schema=llm.SCHEMA)


@pytest.mark.parametrize("requested,expected", [(1, 1), (128, 128), (256, 256), (4096, 256)])
def test_haiku_transport_tool_schema_timeout_and_upper_token_bound(
    monkeypatch, requested, expected
):
    calls = []

    def respond(request, **kwargs):
        calls.append(request)
        assert request.full_url == "https://api.anthropic.com/v1/messages"
        assert request.get_method() == "POST"
        assert kwargs == {"timeout": 45}
        headers = {name.casefold(): value for name, value in request.header_items()}
        assert headers["x-api-key"] == "synthetic-test-key"
        assert headers["anthropic-version"] == "2023-06-01"
        body = json.loads(request.data)
        assert body["model"] == "claude-haiku-4-5-20251001"
        assert body["max_tokens"] == expected
        assert body["temperature"] == 0
        assert body["system"] == MESSAGES[0]["content"]
        assert body["messages"] == MESSAGES[1:]
        assert body["tool_choice"] == {"type": "tool", "name": "route"}
        assert body["tools"][0]["input_schema"] == llm.SCHEMA
        return BytesIO(json.dumps(response()).encode())

    monkeypatch.setattr(remote.urllib.request, "urlopen", respond)
    assert remote.haiku_completion(messages=MESSAGES, schema=llm.SCHEMA, max_tokens=requested) == (
        SELECTED,
        {"input_tokens": 10, "output_tokens": 8},
    )
    assert len(calls) == 1


@pytest.mark.parametrize("invalid", [0, -1, True, 1.5, "128"])
def test_haiku_invalid_token_budget_fails_before_http(invalid):
    with pytest.raises(llm.ModelUnavailable, match="token"):
        remote.haiku_completion(messages=MESSAGES, schema=llm.SCHEMA, max_tokens=invalid)


@pytest.mark.parametrize(
    "reply",
    [
        b"not-json",
        b"{}",
        json.dumps(response(stop_reason="max_tokens")).encode(),
        json.dumps(response(content=[])).encode(),
        json.dumps(response(content=[{"type": "text", "text": "summary"}])).encode(),
        json.dumps(
            response(content=[{"type": "tool_use", "name": "wrong", "input": SELECTED}])
        ).encode(),
        json.dumps(response(content=[response()["content"][0]] * 2)).encode(),
        json.dumps(
            response(content=[{"type": "tool_use", "name": "route", "input": [{"x": 1}]}])
        ).encode(),
        b"x" * (1024 * 1024 + 1),
    ],
    ids=["json", "fields", "truncated", "empty", "text", "name", "multiple", "input-type", "size"],
)
def test_haiku_malformed_or_oversized_reply_is_safe(monkeypatch, reply):
    monkeypatch.setattr(remote.urllib.request, "urlopen", lambda *args, **kwargs: BytesIO(reply))
    with pytest.raises(llm.ModelUnavailable, match="yanıtı doğrulanamadı"):
        remote.haiku_completion(messages=MESSAGES, schema=llm.SCHEMA)


def test_haiku_http_failure_is_bounded_and_does_not_expose_private_error(monkeypatch):
    calls = []

    def fail(request, **kwargs):
        calls.append(request)
        raise urllib.error.URLError("synthetic-private-error-with-key")

    monkeypatch.setattr(remote.urllib.request, "urlopen", fail)
    with pytest.raises(llm.ModelUnavailable) as error:
        remote.haiku_completion(messages=MESSAGES, schema=llm.SCHEMA)
    assert str(error.value) == "Haiku yanıtı doğrulanamadı."
    assert len(calls) == 1


@pytest.mark.parametrize("selected", [None, "summary", [{"action": "summary"}]])
def test_selector_rejects_non_object_completion_safely(selected):
    with pytest.raises(llm.ModelUnavailable, match="parametreleri"):
        llm.select_tool("özet", completion=lambda **kwargs: (selected, {}))


@pytest.mark.parametrize("reply", [None, (), (SELECTED,)])
def test_selector_rejects_malformed_completion_tuple_safely(reply):
    with pytest.raises(llm.ModelUnavailable, match="parametreleri"):
        llm.select_tool("özet", completion=lambda **kwargs: reply)
