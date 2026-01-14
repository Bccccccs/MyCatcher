import argparse
import os
from dotenv import load_dotenv

load_dotenv()

import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from openai import OpenAI


# --------- Path helpers (match variant_generator style) ---------

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATES_DIR = BASE_DIR / "PromptTemplates"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_template_path(tmpl: str) -> Path:
    """
    Allow:
    - pass a real path: PromptTemplates/geninput_direct
    - or pass a name: geninput_direct -> PromptTemplates/geninput_direct(.txt)
    Also tolerate typo: geninput_gengrator -> geninput_generator
    """
    if tmpl == "geninput_gengrator":
        tmpl = "geninput_generator"

    p = Path(tmpl)
    if p.is_file():
        return p

    candidate = DEFAULT_TEMPLATES_DIR / tmpl
    if candidate.is_file():
        return candidate

    candidate_txt = DEFAULT_TEMPLATES_DIR / f"{tmpl}.txt"
    if candidate_txt.is_file():
        return candidate_txt

    raise FileNotFoundError(
        f"Template not found: '{tmpl}'. Tried: {p}, {candidate}, {candidate_txt}"
    )


def build_prompt(template: str, pro_des: str, code: str, num: int) -> str:
    """
    Support placeholders:
      - {pro_des}
      - {code}
      - {num}   (optional; template may not use it)
    """
    # Use safe replacement: if template doesn't have {num}, it's fine.
    try:
        return template.format(pro_des=pro_des, code=code, num=num)
    except KeyError as e:
        raise ValueError(
            f"Template placeholder missing: {e}. "
            f"Expected placeholders: {{pro_des}}, {{code}}, optional {{num}}"
        )


# --------- LLM client helpers ---------

def get_client() -> OpenAI:
    """
    Compatible with OpenAI-style and DeepSeek-style.
    Required env:
      - OPENAI_API_KEY
    Optional:
      - BASE_URL (e.g. DeepSeek base url)
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    base_url = os.getenv("BASE_URL")
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)

    return OpenAI(api_key=api_key)


# --------- Output parsing ---------

_CODE_FENCE = re.compile(r"```(?:python)?\s*([\s\S]*?)```", re.IGNORECASE)
_INPUT_TAG = re.compile(r"^\s*INPUT\s*\d+\s*:\s*$", re.IGNORECASE)
_DELIM = "<<<CASE>>>"


def extract_code_block(text: str) -> str:
    m = _CODE_FENCE.search(text or "")
    if m:
        return m.group(1).strip()
    return (text or "").strip()


def split_cases_from_text(text: str) -> list[str]:
    """
    Robust splitting for direct input generation.

    Priority:
    1) delimiter line: <<<CASE>>>
    2) legacy tag blocks: INPUT1: ... INPUT2: ...
    3) blank line separation (fallback)
    """
    s = (text or "").strip()
    if not s:
        return []

    # 1) delimiter mode
    if _DELIM in s:
        parts = [p.strip() for p in s.split(_DELIM)]
        cases = [p + "\n" for p in parts if p.strip()]
        return cases

    # 2) INPUTk: tag mode
    lines = s.splitlines()
    cases: list[str] = []
    buf: list[str] = []
    seen_tag = False
    for ln in lines:
        if _INPUT_TAG.match(ln):
            seen_tag = True
            if buf:
                cases.append("\n".join(buf).strip() + "\n")
                buf = []
            continue
        buf.append(ln.rstrip("\n"))
    if buf:
        cases.append("\n".join(buf).strip() + "\n")

    if seen_tag:
        cases = [c for c in cases if c.strip()]
        return cases

    # 3) fallback: blank line separation
    cases = []
    buf = []
    for ln in lines:
        if ln.strip() == "":
            if buf:
                cases.append("\n".join(buf).strip() + "\n")
                buf = []
        else:
            buf.append(ln.rstrip("\n"))
    if buf:
        cases.append("\n".join(buf).strip() + "\n")

    return [c for c in cases if c.strip()]


def is_generator_template(template_path: Path) -> bool:
    name = template_path.name.lower()
    return ("generator" in name) or ("geninput_generator" in name)


# --------- Generator execution (for geninput_generator) ---------

def run_generator_code(gen_code: str, num: int, timeout_sec: int = 10) -> list[str]:
    wrapper = f"""
import sys
import random
random.seed(0)

# ---- LLM generated code below ----
{gen_code}

def _emit_cases(n: int):
    if 'generate' in globals() and callable(globals()['generate']):
        out = globals()['generate']()
        cnt = 0
        for item in out:
            if item is None:
                continue
            s = str(item).rstrip() + "\\n"
            sys.stdout.write(s)
            sys.stdout.write("\\n")
            cnt += 1
            if cnt >= n:
                return
        return

    if 'gen_case' in globals() and callable(globals()['gen_case']):
        for _ in range(n):
            s = str(globals()['gen_case']()).rstrip() + "\\n"
            sys.stdout.write(s)
            sys.stdout.write("\\n")
        return

    return

if __name__ == "__main__":
    _emit_cases({num})
"""

    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "tmp_gen.py"
        fp.write_text(wrapper, encoding="utf-8")

        try:
            res = subprocess.run(
                [sys.executable, str(fp)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_sec,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Generated generator code timed out")

        out_text = (res.stdout or "").strip()
        err_text = (res.stderr or "").strip()

        if res.returncode != 0:
            raise RuntimeError(f"Generator code crashed:\n{err_text[:1000]}")

        cases = split_cases_from_text(out_text)

        if not cases and out_text.strip():
            cases = [out_text.strip() + "\n"]

        return cases[:num]


# --------- Main ---------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="Path to spec.txt (problem description)")
    parser.add_argument("--put", required=True, help="Path to PUT file")
    parser.add_argument("--out", required=True, help="Output directory for inputs")
    parser.add_argument("--num", type=int, default=20, help="Number of inputs to generate")
    parser.add_argument("--template", required=True, help="Template name or path. Default dir: PromptTemplates/")
    parser.add_argument(
        "--model",
        default=os.getenv("MODEL_NAME", "deepseek-chat"),
        help="LLM model name (default: env MODEL_NAME or deepseek-chat)",
    )
    parser.add_argument("--max_retry", type=int, default=3, help="Retries for LLM call if parsing fails")
    parser.add_argument("--sleep", type=float, default=0.2, help="Sleep seconds between retries/calls")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    put_path = Path(args.put)
    out_dir = Path(args.out)
    tmpl_path = resolve_template_path(args.template)

    pro_des = load_text(spec_path).strip()
    code = load_text(put_path).strip()
    template = load_text(tmpl_path)

    out_dir.mkdir(parents=True, exist_ok=True)

    client = get_client()

    print(f"[INFO] using template: {tmpl_path}")
    prompt = build_prompt(template, pro_des=pro_des, code=code, num=args.num)

    want_generator = is_generator_template(tmpl_path)

    for attempt in range(args.max_retry + 1):
        resp = client.chat.completions.create(
            model=args.model,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.choices[0].message.content or ""

        if want_generator:
            gen_code = extract_code_block(raw)
            if not gen_code.strip():
                print(f"[WARN] empty generator code, retry={attempt}")
                time.sleep(args.sleep)
                continue

            try:
                cases = run_generator_code(gen_code, num=args.num, timeout_sec=12)
            except Exception as e:
                print(f"[WARN] generator execution failed ({e}), retry={attempt}")
                time.sleep(args.sleep)
                continue
        else:
            cases = split_cases_from_text(raw)
            if not cases:
                print(f"[WARN] no inputs parsed, retry={attempt}")
                time.sleep(args.sleep)
                continue
            cases = cases[: args.num]

        written = 0
        for i, case in enumerate(cases):
            p = out_dir / f"test_{i:03d}.in"
            p.write_text(case, encoding="utf-8")
            written += 1
        print(f"[DONE] wrote {written} inputs into {out_dir}")
        return

    raise RuntimeError("Failed to generate valid inputs after retries. Please adjust template/spec.")


if __name__ == "__main__":
    main()