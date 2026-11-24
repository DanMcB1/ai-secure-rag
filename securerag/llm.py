"""Optional LLM rewrite of an extractive answer. Off by default.

The app must run fully offline with no API key. If OPENAI_API_KEY is set
(and optionally OPENAI_BASE_URL / OPENAI_MODEL for a local Ollama or
other OpenAI-compatible endpoint), the model may rewrite the answer
using only the already-filtered passages. Unauthorized chunks are never
sent. Any failure falls back to the extractive text.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

SYSTEM_PROMPT = (
    "You answer a question for a dealership employee using only the "
    "numbered passages you are given. Those passages have already been "
    "filtered by access control. Do not use outside knowledge. Do not "
    "invent numbers, names, or documents. Quote or closely paraphrase "
    "the passages and keep the numeric citation marks like [1]. If the "
    "passages do not answer the question, say so. Return only the answer, "
    "plain language, no markdown heading."
)


def llm_config() -> dict[str, str] | None:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    base = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE") or "https://api.openai.com/v1"
    base = base.rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    return {"key": key, "base": base, "model": model}


def maybe_rewrite_answer(
    question: str,
    extractive_text: str,
    passages: list[str],
) -> tuple[str, bool, str]:
    """Return (text, used_llm, note). Never raises to the caller."""
    cfg = llm_config()
    if not cfg:
        return extractive_text, False, "No OPENAI_API_KEY set; used the extractive answer."

    payload = {
        "model": cfg["model"],
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\n"
                    "Allowed passages:\n"
                    + "\n\n".join(passages)
                    + "\n\nExtractive draft (keep the same facts):\n"
                    + extractive_text
                ),
            },
        ],
    }
    url = cfg["base"] + "/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg['key']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = body["choices"][0]["message"]["content"].strip()
        if not text:
            return extractive_text, False, "LLM returned an empty answer; kept the extractive text."
        note = f"Answer rewritten with {cfg['model']} at {cfg['base']} from allowed passages only."
        return text, True, note
    except Exception as exc:  # noqa: BLE001 — fallback is the product behavior
        return (
            extractive_text,
            False,
            f"LLM rewrite failed ({type(exc).__name__}: {exc}); kept the extractive text.",
        )
