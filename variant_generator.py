import argparse
from pathlib import Path
import time

from src.llm_utils import get_client, only_code


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_prompt(template: str, pro_des: str, code: str) -> str:
    # 统一占位符：你给的模板用 {pro_des} 和 {code}
    try:
        return template.format(pro_des=pro_des, code=code)
    except KeyError as e:
        raise ValueError(
            f"Template placeholder missing: {e}. "
            f"Expected placeholders: {{pro_des}} and {{code}}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="Path to spec.txt (problem description)")
    parser.add_argument("--puts", required=True, help="Path to PUT python file")
    parser.add_argument("--out", required=True, help="Output directory for variants")
    parser.add_argument("--k", type=int, default=5, help="Number of variants to generate")
    parser.add_argument(
        "--template",
        default="genprog_tc",
        help="Prompt template file path (e.g., genprog_tc or genprog_dfp)",
    )
    parser.add_argument(
        "--model",
        default="deepseek-chat",
        help="Override model name; if None, llm_utils will use env/config default",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.2,
        help="Sleep seconds between calls (avoid rate limit)",
    )

    args = parser.parse_args()

    spec_path = Path(args.spec)
    put_path = Path(args.put)
    out_dir = Path(args.out)
    tmpl_path = Path(args.template)

    out_dir.mkdir(parents=True, exist_ok=True)

    pro_des = load_text(spec_path).strip()
    code = load_text(put_path).strip()
    template = load_text(tmpl_path)

    client = get_client()

    for i in range(1, args.k + 1):
        prompt = build_prompt(template, pro_des=pro_des, code=code)

        resp = client.chat.completions.create(
            model=args.model,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = resp.choices[0].message.content or ""
        variant_code = only_code(raw).strip()
        if not variant_code:
            raise RuntimeError(
                f"LLM returned empty code for variant {i}. Raw response preview:\n{raw[:400]}"
            )

        out_file = out_dir / f"variant_{i:03d}.py"
        out_file.write_text(variant_code + "\n", encoding="utf-8")
        print(f"[OK] wrote {out_file}")

        if args.sleep > 0:
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()