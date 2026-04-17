import argparse
from pathlib import Path

from src.llm_utils import get_client, only_code


def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def resolve_template_path(name_or_path: str) -> Path:
    p = Path(name_or_path)
    if p.exists():
        return p
    root = Path(__file__).resolve().parent.parent  # MyCatcher
    cand = [
        root / "PromptTemplates" / name_or_path,
        root / "PromptTemplates" / f"{name_or_path}.txt",
        root / "Prompt" / "Templates" / name_or_path,
        root / "Prompt" / "Templates" / f"{name_or_path}.txt",
    ]
    for c in cand:
        if c.exists():
            return c
    raise FileNotFoundError(f"Template not found: {name_or_path}. Tried: " + ", ".join(map(str, cand)))


def build_prompt(template: str, pro_des: str) -> str:
    try:
        return template.format(pro_des=pro_des)
    except KeyError as e:
        raise ValueError(f"Template placeholder missing: {e}. Expected {{pro_des}}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="Path to spec.txt")
    ap.add_argument("--template", default="geninput_generator", help="Prompt template name or path")
    ap.add_argument("--out", required=True, help="Output path of generated generator script, e.g. outputs/generators/input_gen.py")
    ap.add_argument("--model", default=None, help="Model name override; if None use env/config default")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    spec_path = (root / args.spec) if not Path(args.spec).is_absolute() else Path(args.spec)
    tmpl_path = resolve_template_path(args.template)
    out_path = (root / args.out) if not Path(args.out).is_absolute() else Path(args.out)

    pro_des = load_text(spec_path).strip()
    template = load_text(tmpl_path)

    prompt = build_prompt(template, pro_des=pro_des)
    client = get_client()

    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = resp.choices[0].message.content or ""
    code = only_code(raw).strip()
    if not code:
        raise RuntimeError(f"LLM returned empty code. Raw preview:\n{raw[:400]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(code + "\n", encoding="utf-8")
    print(f"[OK] wrote generator script: {out_path}")


if __name__ == "__main__":
    main()
