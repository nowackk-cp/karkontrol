"""Opt-in Haiku benchmark adapter; only the synthetic evaluator calls this module."""

import json
import os
import urllib.error
import urllib.request

from .llm import ModelUnavailable

MODEL = "claude-haiku-4-5-20251001"


def haiku_completion(*, messages, schema, max_tokens=128):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ModelUnavailable("Haiku Environment secret eksik; çağrı yapılmadı.")
    if type(max_tokens) is not int or max_tokens <= 0:
        raise ModelUnavailable("Haiku token bütçesi pozitif tamsayı olmalı.")
    body = {
        "model": MODEL,
        "max_tokens": min(max_tokens, 256),
        "temperature": 0,
        "system": messages[0]["content"],
        "messages": messages[1:],
        "tools": [{"name": "route", "description": "Choose a report tool", "input_schema": schema}],
        "tool_choice": {"type": "tool", "name": "route"},
    }
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("Oversized response")
        result = json.loads(raw)
        blocks = [block for block in result["content"] if block["type"] == "tool_use"]
        if result["stop_reason"] != "tool_use" or len(blocks) != 1 or blocks[0]["name"] != "route":
            raise ValueError("Missing route")
        if not isinstance(blocks[0]["input"], dict):
            raise ValueError("Invalid tool input")
        return blocks[0]["input"], result.get("usage", {})
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ModelUnavailable("Haiku yanıtı doğrulanamadı.") from error
