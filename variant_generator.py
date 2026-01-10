import argparse
import re
import time
from pathlib import Path

from src.llm_utils import get_client, only_code


# ----------------------------
# helpers
# ----------------------------
def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_template_path(t: str) -> Path:
    """
    Accept:
      - absolute/relative path to a template file
      - or a bare name like 'genprog_tc' / 'genprog_dfp'
    Search order:
      1) as-is
      2) PromptTemplates/<t>
      3) PromptTemplates/<t>.txt
    """
    cand = [Path(t)]
    cand.append(Path("PromptTemplates") / t)
    cand.append(Path("PromptTemplates") / f"{t}.txt")

    for p in cand:
        if p.exists() and p.is_file():
            return p

    tried = ", ".join(str(p) for p in cand)
    raise FileNotFoundError(f"Template not found: '{t}'. Tried: {tried}")


def inject_language_hint(prompt: str, lang: str) -> str:
    """
    If the template doesn't include language constraints explicitly,
    we prepend a strong instruction.
    """
    lang_name = "Python" if lang == "py" else "C++"
    header = (
        f"**IMPORTANT**: You MUST output ONLY {lang_name} source code. "
        f"Do NOT output explanations, markdown, or code fences.\n\n"
    )
    return header + prompt


def build_prompt(template: str, pro_des: str, code: str, lang: str) -> str:
    """
    Support placeholders:
      - {pro_des}, {code}
      - optional: {lang} or {language}
    """
    fmt_kwargs = {
        "pro_des": pro_des,
        "code": code,
        "lang": lang,
        "language": ("Python" if lang == "py" else "C++"),
    }

    try:
        rendered = template.format(**fmt_kwargs)
    except KeyError as e:
        # 只强制要求 pro_des/code；lang/language 没写不算错
        missing = str(e)
        raise ValueError(
            f"Template placeholder missing: {missing}. "
            f"Required placeholders: {{pro_des}} and {{code}}. "
            f"Optional: {{lang}} or {{language}}."
        )

    # 即使模板没用到 {lang}/{language}，也加一道“语言约束”保险
    rendered = inject_language_hint(rendered, lang)
    return rendered


def sanitize_llm_code(raw: str, lang: str) -> str:
    """
    - Extract code via only_code()
    - Remove leading language tags like 'cpp'/'c++'
    - Remove markdown fences if any slipped through
    """
    code = (only_code(raw) or "").strip()

    # remove code fences if only_code didn't
    code = re.sub(r"^```[a-zA-Z+\-]*\s*", "", code)
    code = re.sub(r"\s*```$", "", code).strip()

    # remove a single leading line that is just 'cpp' / 'c++' / 'python'
    first_line, *rest = code.splitlines() if code else ([],)
    if first_line:
        fl = first_line.strip().lower()
        if fl in {"cpp", "c++", "python", "py"}:
            code = "\n".join(rest).lstrip()

    # If user asked for C++ but model returned Python-style "def", fail fast (可选更严格)
    if lang == "cpp":
        # 非严格判断：出现明显 Python 关键字则提示（不直接报错也行）
        if re.search(r"^\s*def\s+\w+\s*\(", code, flags=re.M):
            # 这里不强制 raise，避免误伤；但建议你先让它报错更早发现问题
            pass

    return code.strip()


# ----------------------------
# main
# ----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="Path to spec.txt (problem description)")
    parser.add_argument("--put", required=True, help="Path to PUT file (py or cpp)")
    parser.add_argument("--out", required=True, help="Output directory for variants")
    parser.add_argument("--k", type=int, default=5, help="Number of variants to generate")

    # 只保留 tc/dfp 两种（你传 PromptTemplates/genprog_tc 也行）
    parser.add_argument(
        "--template",
        default="genprog_tc",
        help="Prompt template (genprog_tc or genprog_dfp, or a file path under PromptTemplates/)",
    )

    parser.add_argument(
        "--lang",
        choices=["py", "cpp"],
        default="py",
        help="Target language of variants: py or cpp",
    )

    parser.add_argument(
        "--model",
        default="deepseek-chat",
        help="Model name (OpenAI-style). For DeepSeek, keep base_url in env.",
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

    template_path = resolve_template_path(args.template)

    out_dir.mkdir(parents=True, exist_ok=True)

    pro_des = load_text(spec_path).strip()
    code = load_text(put_path).strip()
    template = load_text(template_path)

    client = get_client()

    ext = ".py" if args.lang == "py" else ".cpp"

    for i in range(1, args.k + 1):
        prompt = build_prompt(template, pro_des=pro_des, code=code, lang=args.lang)

        resp = client.chat.completions.create(
            model=args.model,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = resp.choices[0].message.content or ""
        variant_code = sanitize_llm_code(raw, lang=args.lang)

        if not variant_code:
            raise RuntimeError(
                f"LLM returned empty code for variant {i}. Raw response preview:\n{raw[:400]}"
            )

        out_file = out_dir / f"variant_{i:03d}{ext}"
        out_file.write_text(variant_code + "\n", encoding="utf-8")
        print(f"[OK] wrote {out_file}")

        if args.sleep > 0:
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()