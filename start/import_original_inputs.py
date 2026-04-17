from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (ROOT / path).resolve()


def list_problem_dirs(root_dir: Path, pid: str | None = None) -> list[Path]:
    if pid:
        return [root_dir / pid]
    return sorted(path for path in root_dir.iterdir() if path.is_dir())


def collect_input_files(problem_dir: Path) -> list[Path]:
    return sorted(path for path in problem_dir.glob("*.in") if path.is_file())


def normalize_input_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip()
    return normalized + "\n" if normalized else ""


def content_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def import_problem(
    *,
    pid: str,
    source_dirs: list[Path],
    out_root: Path,
    overwrite: bool,
    dedup: bool,
) -> tuple[str, str]:
    existing_sources = [path for path in source_dirs if path.exists()]
    if not existing_sources:
        return ("skipped", f"[SKIP] {pid}: no source directories found")

    collected: list[tuple[Path, str]] = []
    for source_dir in existing_sources:
        for input_path in collect_input_files(source_dir):
            text = normalize_input_text(input_path.read_text(encoding="utf-8", errors="ignore"))
            if not text.strip():
                continue
            collected.append((input_path, text))

    if not collected:
        return ("skipped", f"[SKIP] {pid}: no usable .in files found")

    unique_rows: list[tuple[Path, str]] = []
    seen: set[str] = set()
    for input_path, text in collected:
        key = content_key(text) if dedup else str(input_path)
        if key in seen:
            continue
        seen.add(key)
        unique_rows.append((input_path, text))

    out_dir = out_root / pid
    if overwrite and out_dir.exists():
        for old_file in out_dir.glob("test_*.in"):
            old_file.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)

    for index, (_, text) in enumerate(unique_rows):
        out_path = out_dir / f"test_{index:03d}.in"
        out_path.write_text(text, encoding="utf-8")

    return (
        "imported",
        f"[DONE] {pid}: imported={len(unique_rows)} raw={len(collected)} out={out_dir}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import original-paper input files into the project's outputs/inputs/<pid>/test_XXX.in layout."
    )
    parser.add_argument("--pid", default=None, help="Single problem id, e.g. p02594")
    parser.add_argument(
        "--dataset",
        choices=["trickybugs"],
        default="trickybugs",
        help="Which original dataset layout to import from. Current importer supports trickybugs.",
    )
    parser.add_argument(
        "--source-root",
        default="orgrin_Datasets/TrickyBugs/GenInputs",
        help="Root directory containing original input data.",
    )
    parser.add_argument(
        "--source-kind",
        choices=["direct", "testcases", "both"],
        default="both",
        help="Which original input folders to import.",
    )
    parser.add_argument(
        "--out-root",
        default="outputs/inputs",
        help="Project-native inputs root written as outputs/inputs/<pid>/test_XXX.in",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete existing test_*.in files in the destination pid directory before importing.",
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="Keep duplicate input contents instead of deduplicating them.",
    )
    args = parser.parse_args()

    source_root = resolve_path(args.source_root)
    out_root = resolve_path(args.out_root)
    if not source_root.exists():
        raise FileNotFoundError(f"Source root not found: {source_root}")

    source_names = {
        "direct": ["gen_inputs_direct"],
        "testcases": ["gen_testcases"],
        "both": ["gen_inputs_direct", "gen_testcases"],
    }[args.source_kind]

    pid_candidates: set[str] = set()
    for source_name in source_names:
        source_dir = source_root / source_name
        if not source_dir.exists():
            continue
        for problem_dir in list_problem_dirs(source_dir, args.pid):
            if problem_dir.exists():
                pid_candidates.add(problem_dir.name)

    if not pid_candidates:
        raise RuntimeError(f"No importable problem directories found under: {source_root}")

    imported = 0
    skipped = 0
    for pid in sorted(pid_candidates):
        status, message = import_problem(
            pid=pid,
            source_dirs=[source_root / source_name / pid for source_name in source_names],
            out_root=out_root,
            overwrite=args.overwrite,
            dedup=not args.no_dedup,
        )
        print(message)
        if status == "imported":
            imported += 1
        else:
            skipped += 1

    print(f"[SUMMARY] imported={imported} skipped={skipped} out_root={out_root}")


if __name__ == "__main__":
    main()
