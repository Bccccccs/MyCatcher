import argparse
import re
import time
from pathlib import Path

from src.llm_utils import get_client, only_code
ROOT = Path(__file__).resolve().parents[1]   # .../MyCatcher

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
    cand.append(Path("../PromptTemplates") / t)
    cand.append(Path("../PromptTemplates") / f"{t}.txt")

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

    code = extract_code_body(code, lang)

    return code.strip()


def extract_code_body(code: str, lang: str) -> str:
    if not code:
        return ""

    lines = code.splitlines()
    if lang == "cpp":
        start_patterns = (
            r"^\s*#include\b",
            r"^\s*using\s+namespace\b",
            r"^\s*int\s+main\s*\(",
            r"^\s*(?:static\s+)?(?:inline\s+)?(?:long\s+long|long|int|void|bool|char|double|string|vector<)",
            r"^\s*template\s*<",
        )
    else:
        start_patterns = (
            r"^\s*from\s+\S+\s+import\s+",
            r"^\s*import\s+\S+",
            r"^\s*def\s+\w+\s*\(",
            r"^\s*class\s+\w+\s*[\(:]",
            r"^\s*if\s+__name__\s*==\s*[\"']__main__[\"']\s*:",
        )

    start_idx = 0
    for i, line in enumerate(lines):
        if any(re.search(pattern, line) for pattern in start_patterns):
            start_idx = i
            break

    trimmed = "\n".join(lines[start_idx:]).strip()
    if not trimmed:
        return ""

    if lang == "cpp":
        end_markers = (
            "\nI have made the following changes",
            "\nExplanation:",
            "\nHere is",
            "\nThis code",
            "\nNote:",
        )
    else:
        end_markers = (
            "\nI have made the following changes",
            "\nExplanation:",
            "\nHere is",
            "\nThis Python",
            "\nNote:",
        )

    cut_positions = [trimmed.find(marker) for marker in end_markers if trimmed.find(marker) != -1]
    if cut_positions:
        trimmed = trimmed[:min(cut_positions)].rstrip()

    return trimmed


def build_output_file(out_dir: Path, lang: str, naming: str, name_prefix: str | None, index: int) -> Path:
    ext = ".py" if lang == "py" else ".cpp"
    if naming == "trickybugs":
        if not name_prefix:
            raise ValueError("--name-prefix is required when --naming=trickybugs")
        return out_dir / f"{name_prefix}{index}"
    return out_dir / f"variant_{index:03d}{ext}"


def build_parsed_output_file(out_file: Path, lang: str) -> Path:
    ext = ".py" if lang == "py" else ".cpp"
    if out_file.suffix == ext:
        return out_file.with_name(f"{out_file.stem}_parsed{ext}")
    return out_file.with_name(f"{out_file.name}_parsed{ext}")


# ----------------------------
# main
# ----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec.txt", dest="spec_txt", required=True, help="Path to spec.txt (problem description)")
    parser.add_argument("--put", required=True, help="Path to PUT file (py or cpp)")
    parser.add_argument("--out", required=True, help="Output directory for variants")
    parser.add_argument("--k", type=int, default=5, help="Number of variants to generate")
    parser.add_argument(
        "--naming",
        choices=["default", "trickybugs"],
        default="default",
        help="Output naming scheme",
    )
    parser.add_argument(
        "--name-prefix",
        default=None,
        help="Custom prefix for variant filenames, e.g. p03000_num",
    )
    parser.add_argument(
        "--index-start",
        type=int,
        default=1,
        help="Starting index for variant numbering",
    )

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

    spec_path = Path(args.spec_txt)
    put_path = Path(args.put)
    out_dir = Path(args.out)

    template_path = resolve_template_path(args.template)

    out_dir.mkdir(parents=True, exist_ok=True)

    pro_des = load_text(spec_path).strip()
    code = load_text(put_path).strip()
    template = load_text(template_path)

    client = get_client()

    print("Trying to generate {} variant code by {}...".format(args.k,args.lang))
    print("#"*50)
    for offset in range(args.k):
        index = args.index_start + offset
        prompt = build_prompt(template, pro_des=pro_des, code=code, lang=args.lang)

        resp = client.chat.completions.create(
            model=args.model,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = resp.choices[0].message.content or ""
        variant_code = sanitize_llm_code(raw, lang=args.lang)

        if not variant_code:
            raise RuntimeError(
                f"LLM returned empty code for variant {index}. Raw response preview:\n{raw[:400]}"
            )

        out_file = build_output_file(
            out_dir=out_dir,
            lang=args.lang,
            naming=args.naming,
            name_prefix=args.name_prefix,
            index=index,
        )
        parsed_out_file = build_parsed_output_file(out_file, args.lang)

        out_file.write_text(variant_code + "\n", encoding="utf-8")
        parsed_out_file.write_text(variant_code + "\n", encoding="utf-8")
        print(f"[OK] wrote {out_file}")
        print(f"[OK] wrote {parsed_out_file}")

        if args.sleep > 0:
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
