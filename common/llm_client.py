from __future__ import annotations

import re


_CODE_FENCE_RE = re.compile(r"```(?:[a-zA-Z0-9_+\-#.]*)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def only_code(text: str) -> str:
    if not text:
        return ""
    match = _CODE_FENCE_RE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def get_client():
    from src.llm_utils import get_client as _get_client

    return _get_client()


def generate_text(*, prompt: str, model: str) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""


__all__ = ["generate_text", "get_client", "only_code"]
