import argparse
from pathlib import Path
import os
import re
import time

from src.llm_utils import get_client, only_code

PROMPT_TMPL = """You are a software testing expert.

Generate ONE valid test input for the problem below.

STRICT OUTPUT RULES:
- Output MUST contain ONLY integers, spaces, and newlines.
- Do NOT include any explanations, labels, markdown, or code fences.

INPUT FORMAT:
- First line: n m k
- Second line: n integers a[i]
- Third line: m integers b[j]

Constraints:
- 1 <= n,m <= 50
- 0 <= k <= 20
- 0 <= a[i], b[j] <= 50

Additionally, with at least 50% probability, ensure there exists a pair (a[i], b[j]) such that |a[i] - b[j]| = k exactly.

[PROBLEM SPEC]
{spec}
"""

def extract_ints(text: str):
    return list(map(int, re.findall(r"-?\d+", text)))

def is_valid_case(ints):
    # must have at least n,m,k
    if len(ints) < 3:
        return False
    n, m, k = ints[0], ints[1], ints[2]
    if not (1 <= n <= 50 and 1 <= m <= 50 and 0 <= k <= 20):
        return False
    need = 3 + n + m
    if len(ints) < need:
        return False
    return True

def format_case(ints):
    n, m, k = ints[0], ints[1], ints[2]
    a = ints[3:3+n]
    b = ints[3+n:3+n+m]
    lines = [
        f"{n} {m} {k}",
        " ".join(map(str, a)),
        " ".join(map(str, b)),
        ""
    ]
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--num", type=int, default=20)
    ap.add_argument("--max_retry", type=int, default=8)
    args = ap.parse_args()

    spec = Path(args.spec).read_text(encoding="utf-8")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = get_client()
    model = os.getenv("MODEL_NAME") or "deepseek-chat"

    for i in range(args.num):
        ok = False
        last_preview = ""
        for r in range(args.max_retry):
            prompt = PROMPT_TMPL.format(spec=spec)
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=512,
            )
            raw = resp.choices[0].message.content or ""
            raw = only_code(raw)
            ints = extract_ints(raw)

            if is_valid_case(ints):
                text = format_case(ints)
                (out_dir / f"test_{i:03d}.in").write_text(text, encoding="utf-8")
                print(f"[OK] wrote test_{i:03d}.in (retry={r})")
                ok = True
                break

            # keep a short preview for debugging
            last_preview = raw[:120].replace("\n", "\\n")
            time.sleep(0.2)

        if not ok:
            raise RuntimeError(f"Failed to generate a valid input for test_{i:03d}. Last preview: {last_preview}")

if __name__ == "__main__":
    main()