import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("BASE_URL")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Put it in .env or export it.")
    return OpenAI(api_key=api_key, base_url=base_url)

_CODE_FENCE_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)

def only_code(text: str) -> str:
    """
    Extract python code from an LLM response.
    Priority: fenced code block; fallback: raw text.
    """
    if not text:
        return ""
    m = _CODE_FENCE_RE.search(text)
    if m:
        return m.group(1).strip()
    return text.strip()