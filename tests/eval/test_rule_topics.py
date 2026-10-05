"""Synthetic v3 topic-routing contracts; no model scores or human labels are generated."""

from copy import deepcopy
from itertools import combinations

import pytest

from apps.assistant import llm
from apps.assistant.tools import RULES

pytestmark = pytest.mark.eval
TOPICS = tuple(RULES)


@pytest.fixture(autouse=True)
def no_real_model_http(monkeypatch):
    monkeypatch.setattr(
        llm.urllib.request, "urlopen", lambda *args, **kwargs: pytest.fail("Real HTTP forbidden")
    )


def selected(action="rule", topic="", year=None, month=None):
    return {"action": action, "topic": topic, "year": year, "month": month}


@pytest.mark.parametrize("topic", TOPICS)
def test_explicit_rule_topic_rejects_another_supported_topic_without_overwrite(topic):
    wrong_topic = TOPICS[(TOPICS.index(topic) + 1) % len(TOPICS)]
    response = selected(topic=wrong_topic)
    original = deepcopy(response)
    with pytest.raises(llm.ModelUnavailable, match="Kural konusu.*eşleşmiyor"):
        llm.select_tool(f"{topic} kuralı nedir?", completion=lambda **kw: (response, {}))
    assert response == original


@pytest.mark.parametrize("topic", TOPICS)
def test_explicit_rule_topic_rejects_empty_rule_topic(topic):
    with pytest.raises(llm.ModelUnavailable, match="Kural konusu.*eşleşmiyor"):
        llm.select_tool(f"{topic} kuralı nedir?", completion=lambda **kw: (selected(), {}))


@pytest.mark.parametrize("topic", TOPICS)
def test_correct_rule_topic_uses_per_request_enum_and_preserves_selection(topic):
    response = selected(topic=topic)
    usage = {"total_tokens": 7}
    original_schema = deepcopy(llm.SCHEMA)

    def complete(**kwargs):
        assert kwargs["schema"]["properties"]["topic"] == {
            "type": "string",
            "enum": ["", topic],
        }
        assert kwargs["schema"]["properties"]["action"] == original_schema["properties"]["action"]
        return response, usage

    result, result_usage = llm.select_tool(f"{topic} kuralı nedir?", completion=complete)
    assert result is response
    assert result_usage is usage
    assert llm.SCHEMA == original_schema


@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("action", ["summary", "products", "returns"])
def test_single_topic_still_allows_nonrule_report_actions(topic, action):
    response = selected(action=action)
    original = deepcopy(response)
    assert (
        llm.select_tool(f"{topic} raporunu göster", completion=lambda **kw: (response, {}))[0]
        is response
    )
    assert response == original


@pytest.mark.parametrize(
    "question",
    [
        "Kurallar nedir?",
        "Kuralları açıkla",
        "Kurgu raporunu kurgula",
        "kuryesi nedir?",
        "kurları göster",
        "kur_kuralı nedir?",
        "fiyatkur nedir?",
        "kur2 nedir?",
        "2kur nedir?",
        "iadeci",
        "kargocu",
        "stopajsız",
        "kuponlu",
        "kdvli",
        "kдv nedir?",
        "Kâr nasıl hesaplanır?",
    ],
)
def test_substrings_and_unknown_topics_keep_full_enum(question):
    response = selected(topic="kdv")

    def complete(**kwargs):
        assert kwargs["schema"]["properties"]["topic"] == llm.SCHEMA["properties"]["topic"]
        return response, {}

    assert llm.select_tool(question, completion=complete)[0] is response


@pytest.mark.parametrize(
    "question,topic",
    [
        ("KUR kuralı nedir?", "kur"),
        ("[kur]: nasıl uygulanır?", "kur"),
        ("Kur'un etkisi nedir?", "kur"),
        ("kur, kur ve KUR", "kur"),
        ("İADE kuralı nedir?", "iade"),
        ("I\u0307ADE kuralı nedir?", "iade"),
        ("ＫＤＶ nasıl hesaplanır?", "kdv"),
        ("KDV’si nasıl hesaplanır?", "kdv"),
    ],
)
def test_word_normalization_and_punctuation_resolve_one_topic(question, topic):
    def complete(**kwargs):
        assert kwargs["schema"]["properties"]["topic"]["enum"] == ["", topic]
        return selected(topic=topic), {}

    assert llm.select_tool(question, completion=complete)[0]["topic"] == topic


@pytest.mark.parametrize("first,second", list(combinations(TOPICS, 2)))
def test_multiple_explicit_topics_keep_full_enum_and_no_forced_topic(first, second):
    response = selected(topic=second)

    def complete(**kwargs):
        assert kwargs["schema"]["properties"]["topic"] == llm.SCHEMA["properties"]["topic"]
        return response, {}

    assert (
        llm.select_tool(f"{first} ve {second} kurallarını açıkla", completion=complete)[0]
        is response
    )


@pytest.mark.parametrize("version", ["v1", "v2"])
@pytest.mark.parametrize("topic", TOPICS)
def test_frozen_versions_keep_prior_topic_schema_and_validation(version, topic):
    response = selected(topic=TOPICS[(TOPICS.index(topic) + 1) % len(TOPICS)])

    def complete(**kwargs):
        assert kwargs["schema"]["properties"]["topic"] == llm.SCHEMA["properties"]["topic"]
        assert kwargs["messages"][0]["content"] == (llm.PROMPTS / f"{version}.txt").read_text(
            encoding="utf-8"
        )
        return response, {}

    assert (
        llm.select_tool(f"{topic} kuralı nedir?", version=version, completion=complete)[0]
        is response
    )


def test_per_request_topic_constraint_does_not_leak_to_next_request_or_global_schema():
    original = deepcopy(llm.SCHEMA)
    captured = []

    def complete(**kwargs):
        schema = kwargs["schema"]
        captured.append(schema)
        return selected(action="summary"), {}

    for question in ("Kur kuralı nedir?", "KDV raporunu göster", "Kur ve KDV nedir?", "özet"):
        llm.select_tool(question, completion=complete)
    assert [schema["properties"]["topic"]["enum"] for schema in captured] == [
        ["", "kur"],
        ["", "kdv"],
        original["properties"]["topic"]["enum"],
        original["properties"]["topic"]["enum"],
    ]
    assert llm.SCHEMA == original


def test_topic_and_authorized_period_constraints_coexist_for_a_kdv_report():
    response = selected(action="summary", year=2026, month=9)

    def complete(**kwargs):
        assert kwargs["schema"]["properties"]["topic"]["enum"] == ["", "kdv"]
        assert kwargs["schema"]["properties"]["year"] == {"enum": [2026]}
        assert kwargs["schema"]["properties"]["month"] == {"enum": [9]}
        return response, {}

    assert llm.select_tool("2026 Eylül KDV raporu", completion=complete)[0] is response


@pytest.mark.django_db
def test_wrong_kur_rule_is_unavailable_and_never_executes_a_different_rule(evaluation, monkeypatch):
    owner, store = evaluation
    response = selected(topic="kdv")
    monkeypatch.setattr(llm, "explain_rule", lambda *a: pytest.fail("Wrong rule executed"))
    result = llm.ask_llm(
        user=owner,
        store_pk=store.pk,
        question="Kur kuralı nedir?",
        completion=lambda **kw: (response, {}),
    )
    assert result["status"] == "unavailable"
    assert result["model_attempted"] is True
    assert result["tool"] is None
    assert "selection" not in result
    assert response["topic"] == "kdv"


@pytest.mark.django_db
def test_correct_kur_rule_reaches_only_the_existing_rule_source(evaluation):
    owner, store = evaluation
    result = llm.ask_llm(
        user=owner,
        store_pk=store.pk,
        question="Kur kuralı nedir?",
        completion=lambda **kw: (selected(topic="kur"), {}),
    )
    assert result["status"] == "ok"
    assert result["selection"]["topic"] == "kur"
    assert result["answer"] == RULES["kur"]
    assert result["tool"]["source"] == "docs/KURALLAR.md"
