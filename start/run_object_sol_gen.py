import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from LLM_Gen.variant_generator import (
    build_prompt,
    extract_code_body,
    load_text,
    resolve_template_path,
    sanitize_llm_code,
)
from src.progress import log_line, print_progress
from src.llm_utils import get_client


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def find_program_dirs(dataset_root: Path) -> list[Path]:
    return sorted(
        program_dir
        for program_dir in dataset_root.iterdir()
        if program_dir.is_dir() and (program_dir / "spec.txt").exists()
    )


def has_meaningful_content(path: Path) -> bool:
    if not path.exists():
        return False
    return bool(path.read_text(encoding="utf-8", errors="ignore").strip())


def generate_object_solution(
    client,
    template: str,
    spec_path: Path,
    model: str,
) -> str:
    prompt = build_prompt(
        template=template,
        pro_des=load_text(spec_path).strip(),
        code="",
        lang="cpp",
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.choices[0].message.content or ""
    code = sanitize_llm_code(raw, lang="cpp")
    if not code:
        raise RuntimeError(f"LLM returned empty code for: {spec_path}")

    normalized = extract_code_body(code, lang="cpp").strip()
    if not normalized:
        raise RuntimeError(f"Failed to normalize generated code for: {spec_path}")
    return normalized + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pid", default=None, help="Single problem id such as p02547")
    ap.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    ap.add_argument("--template", default="PromptTemplates/genprog_dfp")
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--out-name", default="object_sol.cpp")
    ap.add_argument("--sleep", type=float, default=0.2)
    ap.add_argument("--force", action="store_true", help="Overwrite existing object solutions")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    dataset_root = resolve_path(root, args.dataset_root)
    template_path = resolve_template_path(args.template)
    template = load_text(template_path)

    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    if args.pid:
        program_dirs = [dataset_root / args.pid]
    else:
        program_dirs = find_program_dirs(dataset_root)

    client = get_client()
    generated = 0
    skipped = 0

    print_progress(0, len(program_dirs), f"object-sol dataset={dataset_root}")
    for done, program_dir in enumerate(program_dirs, 1):
        spec_path = program_dir / "spec.txt"
        out_path = program_dir / args.out_name
        if not spec_path.exists():
            log_line(f"[SKIP] missing spec: {program_dir}")
            skipped += 1
            print_progress(done, len(program_dirs), f"object-sol skipped={program_dir.name}")
            continue
        if has_meaningful_content(out_path) and not args.force:
            log_line(f"[SKIP] exists: {out_path}")
            skipped += 1
            print_progress(done, len(program_dirs), f"object-sol skipped={program_dir.name}")
            continue

        code = generate_object_solution(
            client=client,
            template=template,
            spec_path=spec_path,
            model=args.model,
        )
        out_path.write_text(code, encoding="utf-8")
        generated += 1
        log_line(f"[OK] wrote {out_path}")
        print_progress(done, len(program_dirs), f"object-sol latest={program_dir.name}")
        if args.sleep > 0:
            time.sleep(args.sleep)

    log_line(f"[DONE] generated={generated}, skipped={skipped}, dataset={dataset_root}")


if __name__ == "__main__":
    main()
