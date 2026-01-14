#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

# ----------------------------
# bootstrap: make project root importable
# ----------------------------
ROOT = Path(__file__).resolve().parents[1]  # .../MyCatcher
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import time

from src.llm_utils import get_client, only_code


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def resolve_template_path(tmpl: str) -> Path:
    """
    Accept:
      - absolute path
      - relative path (to project root)
      - bare name like 'geninput_inspector' (search in PromptTemplates/)
    """
    p = Path(tmpl)
    if p.is_absolute() and p.exists():
        return p

    # try relative to root
    p2 = (ROOT / tmpl)
    if p2.exists():
        return p2

    # try PromptTemplates
    p3 = ROOT / "PromptTemplates" / tmpl
    if p3.exists():
        return p3

    # try PromptTemplates + .txt
    p4 = ROOT / "PromptTemplates" / f"{tmpl}.txt"
    if p4.exists():
        return p4

    raise FileNotFoundError(f"Template not found: {tmpl}")


def build_prompt(template: str, pro_des: str, code: str) -> str:
    # your template uses {pro_des} and {code}
    return template.format(pro_des=pro_des, code=code)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="problem spec file, e.g. data/spec.txt")
    ap.add_argument("--template", required=True, help="template name or path, e.g. geninput_inspector")
    ap.add_argument("--out", required=True, help="output checker path, e.g. outputs/checker/check_input.py")
    ap.add_argument("--model", default="deepseek-chat", help="LLM model name")
    ap.add_argument("--sleep", type=float, default=0.2, help="sleep seconds between calls")
    args = ap.parse_args()

    spec_path = (ROOT / args.spec) if not Path(args.spec).is_absolute() else Path(args.spec)
    tmpl_path = resolve_template_path(args.template)
    out_path = (ROOT / args.out) if not Path(args.out).is_absolute() else Path(args.out)

    pro_des = read_text(spec_path).strip()
    template = read_text(tmpl_path)

    # code placeholder: for inspector generation, you can pass empty code or a sample PUT code if you want
    # Here we pass empty string by default.
    prompt = build_prompt(template, pro_des=pro_des, code="")

    client = get_client()
    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = resp.choices[0].message.content or ""
    checker_code = only_code(raw).strip()
    if not checker_code:
        raise RuntimeError(f"LLM returned empty code. Raw preview:\n{raw[:400]}")

    write_text(out_path, checker_code + "\n")
    print(f"[OK] wrote inspector -> {out_path}")

    if args.sleep and args.sleep > 0:
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()