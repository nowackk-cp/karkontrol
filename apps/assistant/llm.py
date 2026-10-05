"""Real local LLM selects read-only tools; money is always rendered by server code."""

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from django.shortcuts import get_object_or_404

from apps.stores.models import Store

from .dates import normalize_question, resolve_period
from .service import _render, guardrail, unsafe_question, unsupported_amount_filter
from .tools import RULES, explain_rule, product_profit, profit_summary, return_statistics

PROMPTS = Path(__file__).with_name("prompts")
TOOLS = {
    "summary": profit_summary,
    "products": product_profit,
    "returns": return_statistics,
}
SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": [*TOOLS, "rule", "clarify", "refuse", "unsupported"]},
        "topic": {"type": "string", "enum": ["", *RULES]},
        "year": {"type": ["integer", "null"], "minimum": 1900, "maximum": 2199},
        "month": {"type": ["integer", "null"], "minimum": 1, "maximum": 12},
    },
    "required": ["action", "topic", "year", "month"],
    "additionalProperties": False,
}
MESSAGES = {
    "clarify": "Hangi yıl ve ay için, hangi raporu inceleyelim?",
    "refuse": "Bu isteği yerine getiremiyorum. Yalnız seçili mağazanızın raporlarına erişebilirim.",
    "unsupported": (
        "Bu konu kapsamım dışında. Mağazanızın finans raporları hakkında sorabilirsiniz."
    ),
}


class ModelUnavailable(Exception):
    """Safe public failure; raw server errors and configuration never reach the UI."""


def local_completion(*, messages, schema, max_tokens=128, base_url=None, model=None):
    base = base_url or os.getenv("KARKONTROL_LLM_URL", "http://127.0.0.1:8081")
    parsed = urllib.parse.urlsplit(base)
    # This adapter deliberately supports loopback only: no financial data leaves the computer.
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ModelUnavailable("Yerel model adresi geçersiz.")
    body = {
        "model": model or os.getenv("KARKONTROL_LLM_MODEL", "Qwen3-1.7B-Q8_0"),
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
        "response_format": {"type": "json_object", "schema": schema},
    }
    request = urllib.request.Request(
        base.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("Oversized response")
        result = json.loads(raw)
        choice = result["choices"][0]
        if choice.get("finish_reason") != "stop":
            raise ValueError("Incomplete output")
        content = json.loads(choice["message"]["content"])
        if not isinstance(content, dict):
            raise ValueError("Invalid output")
        return content, result.get("usage", {})
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        raise ModelUnavailable(
            "Yerel dil modeline ulaşılamadı veya yanıt doğrulanamadı."
        ) from error


def _explicit_rule_topic(question):
    words = set(re.findall(r"\w+", normalize_question(question)))
    topics = [topic for topic in RULES if normalize_question(topic) in words]
    return topics[0] if len(topics) == 1 else None


def select_tool(question, version="v3", *, completion=None):
    if version not in {"v1", "v2", "v3"}:
        raise ValueError("Unknown prompt version")
    prompt = (PROMPTS / f"{version}.txt").read_text(encoding="utf-8")
    period = resolve_period(question)
    if period.error:
        raise ModelUnavailable(period.error)
    year, month = period.year, period.month
    explicit_topic = _explicit_rule_topic(question) if version == "v3" else None
    if version == "v3":
        prompt += f"\nSunucunun çözdüğü dönem: year={year}, month={month}. Bu değerleri kullan."
        if explicit_topic:
            prompt += (
                f"\nSunucunun metindeki tek açık kural konusu: topic={explicit_topic}. "
                "action=rule ise bu topic değerini kullan; diğer eylemlerde topic boş kalır."
            )
    # Dates are exact user input, not model arithmetic. Constrain generation at its source.
    schema = {
        **SCHEMA,
        "properties": {
            **SCHEMA["properties"],
            "year": {"enum": [year]},
            "month": {"enum": [month]},
        },
    }
    if explicit_topic:
        schema["properties"]["topic"] = {
            **SCHEMA["properties"]["topic"],
            "enum": ["", explicit_topic],
        }
    try:
        selected, usage = (completion or local_completion)(
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": question}],
            schema=schema,
        )
    except (TypeError, ValueError) as error:
        raise ModelUnavailable("Araç parametreleri doğrulanamadı.") from error
    if not isinstance(selected, dict) or set(selected) != set(SCHEMA["required"]):
        raise ModelUnavailable("Araç parametreleri doğrulanamadı.")
    if selected["action"] not in SCHEMA["properties"]["action"]["enum"]:
        raise ModelUnavailable("Geçersiz araç.")
    if selected["topic"] not in SCHEMA["properties"]["topic"]["enum"]:
        raise ModelUnavailable("Geçersiz kural.")
    if explicit_topic and selected["action"] == "rule" and selected["topic"] != explicit_topic:
        raise ModelUnavailable("Kural konusu kullanıcı sorusuyla eşleşmiyor.")
    for field, minimum, maximum in (("year", 1900, 2199), ("month", 1, 12)):
        value = selected[field]
        if value is not None and (type(value) is not int or not minimum <= value <= maximum):
            raise ModelUnavailable("Geçersiz tarih.")
    if selected["year"] != year or selected["month"] != month:
        raise ModelUnavailable("Tarih kullanıcı sorusuyla eşleşmiyor.")
    return selected, usage


def ask_llm(*, user, store_pk, question, version="v3", completion=None, backend="local"):
    store = get_object_or_404(Store, pk=store_pk, owner=user)
    if not isinstance(question, str) or not question.strip() or len(question) > 1000:
        return {"status": "clarify", "answer": "Kısa bir soru yazın.", "tool": None}
    if unsafe_question(question):
        return {"status": "refused", "answer": MESSAGES["refuse"], "tool": None}
    period = resolve_period(question)
    if period.error:
        return {"status": "clarify", "answer": period.error, "tool": None}
    if unsupported_amount_filter(question):
        return {"status": "unsupported", "answer": MESSAGES["unsupported"], "tool": None}
    try:
        selected, usage = (
            select_tool(question, version, completion=completion)
            if completion
            else select_tool(question, version)
        )
    except ModelUnavailable:
        return {
            "status": "unavailable",
            "answer": (
                "Dil modeli şu anda kullanılamıyor. Kâr raporunu açarak tutarları görebilirsiniz."
            ),
            "tool": None,
            "backend": backend,
            "prompt_version": version,
            "model_attempted": True,
        }
    action = selected["action"]
    metadata = {
        "selection": selected,
        "usage": usage,
        "prompt_version": version,
        "backend": backend,
        "model_attempted": True,
    }
    if action in MESSAGES:
        return {
            "status": "refused" if action == "refuse" else action,
            "answer": MESSAGES[action],
            "tool": None,
            **metadata,
        }
    year, month = selected["year"], selected["month"]
    if month and not year:
        return {"status": "clarify", "answer": MESSAGES["clarify"], "tool": None, **metadata}
    # A model may not manufacture the year. Dates are authorized by the user question.
    if (year, month) != (period.year, period.month):
        return {"status": "clarify", "answer": MESSAGES["clarify"], "tool": None, **metadata}
    filters = period.filters
    if action == "rule":
        if not selected["topic"]:
            return {"status": "clarify", "answer": MESSAGES["clarify"], "tool": None, **metadata}
        data = explain_rule(selected["topic"])
    else:
        data = TOOLS[action](store, filters)
    if data["kind"] != "rule":
        data["period"] = {**{k: v.isoformat() for k, v in filters.items()}, "label": period.label}
    answer, allowed = _render(data)
    if not guardrail(answer, allowed):
        return {"status": "blocked", "answer": "Yanıt doğrulanamadı.", "tool": data, **metadata}
    return {
        "status": "ok",
        "answer": answer,
        "tool": data,
        "allowed_numbers": sorted(allowed),
        **metadata,
    }
