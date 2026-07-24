"""Groq LLM factory + robust JSON call helper.

Small models (gemma2-9b-it) are unreliable at returning clean JSON, so every
structured call is wrapped with: json-mode request -> tolerant extraction ->
one corrective retry. Nothing downstream ever sees a raw model string.
"""
from __future__ import annotations

import json
import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from ..config import settings

_llm_cache: dict[str, ChatGroq] = {}


def get_llm(model: str, temperature: float = 0.0) -> ChatGroq:
    key = f"{model}:{temperature}"
    if key not in _llm_cache:
        _llm_cache[key] = ChatGroq(
            model=model,
            temperature=temperature,
            api_key=settings.groq_api_key,
            max_retries=2,
        )
    return _llm_cache[key]


def _extract_json_block(text: str) -> str:
    """Pull the first balanced {...} object out of an LLM response."""
    text = text.strip()
    if text.startswith("```"):
        # strip ```json ... ``` fences
        text = text.split("```", 2)[1]
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
    start = text.find("{")
    if start == -1:
        return text
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return text[start:]


def structured_call(
    model: str,
    system: str,
    user: str,
    temperature: float = 0.0,
) -> tuple[dict[str, Any], int]:
    """Call the model and return (parsed_json_dict, latency_ms).

    Retries once with a stricter instruction if the first parse fails.
    """
    llm = get_llm(model, temperature)
    started = time.perf_counter()

    messages = [SystemMessage(content=system), HumanMessage(content=user)]
    raw = ""
    for attempt in range(2):
        response = llm.invoke(messages)
        raw = response.content if isinstance(response.content, str) else str(response.content)
        try:
            parsed = json.loads(_extract_json_block(raw))
            latency_ms = int((time.perf_counter() - started) * 1000)
            return parsed, latency_ms
        except (json.JSONDecodeError, ValueError):
            messages.append(HumanMessage(
                content="That was not valid JSON. Respond again with ONLY a single "
                        "valid JSON object, no prose, no markdown fences."
            ))

    # Both attempts failed: fail soft with an empty object.
    latency_ms = int((time.perf_counter() - started) * 1000)
    return {}, latency_ms
