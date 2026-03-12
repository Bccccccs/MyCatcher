import argparse
import subprocess
import sys
from pathlib import Path


def resolve_path(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (root / p).resolve()


def find_program_dirs(dataset_root: Path) -> list[Path]:
    return sorted([p for p in dataset_root.iterdir() if p.is_dir()])


def check_inputs_for_one(
    python: str,
    checker: Path,
    inputs_dir: Path,
    start: int,
    max_i: int,
    timeout: float,
) -> tuple[int, list[int]]:
    kept = 0
    removed: list[int] = []

    for i in range(start, max_i + 1):
        infile = inputs_dir / f"test_{i:03d}.in"
        if not infile.exists():
            continue

        try:
            r = subprocess.run(
                [python, str(checker)],
                stdin=infile.open("r", encoding="utf-8", errors="ignore"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            print(f"[DEL] {infile} (checker timeout)")
            infile.unlink(missing_ok=True)
            removed.append(i)
            continue

        if r.returncode == 0:
            kept += 1
            print(f"[OK ] {infile}")
        else:
            msg = (r.stdout.strip() or r.stderr.strip() or "invalid input").strip()
            print(f"[DEL] {infile} -> {msg}")
            infile.unlink(missing_ok=True)
            removed.append(i)

    return kept, removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch-run checker and delete invalid inputs automatically")
    parser.add_argument("--spec", default=None, help="Single spec.txt path. If omitted, run for all <dataset-root>/*/spec.txt")
    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--checker-name", default="check_input.py")
    parser.add_argument("--inputs-root", default="outputs/inputs")
    parser.add_argument("--max", type=int, default=99, help="Max input index (inclusive)")
    parser.add_argument("--start", type=int, default=0, help="Start input index")
    parser.add_argument("--timeout", type=float, default=2.0, help="Timeout seconds for checker")
    args = parser.parse_args()

    if args.start < 0 or args.max < args.start:
        raise ValueError("Invalid range: require 0 <= start <= max")

    root = Path(__file__).resolve().parent.parent
    python = sys.executable
    inputs_root = resolve_path(root, args.inputs_root)

    if args.spec:
        spec = resolve_path(root, args.spec)
        checker = spec.parent / args.checker_name
        inputs_dir = inputs_root
        if not checker.exists():
            raise FileNotFoundError(f"Checker not found: {checker}")
        if not inputs_dir.exists():
            raise FileNotFoundError(f"Inputs dir not found: {inputs_dir}")
        kept, removed = check_inputs_for_one(python, checker, inputs_dir, args.start, args.max, args.timeout)
        print("-" * 50)
        print(f"[DONE] kept={kept}, removed={len(removed)}")
        return

    dataset_root = resolve_path(root, args.dataset_root)
    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    total_kept = 0
    total_removed = 0
    skipped = 0

    for program_dir in find_program_dirs(dataset_root):
        spec = program_dir / "spec.txt"
        checker = program_dir / args.checker_name
        inputs_dir = inputs_root / program_dir.name
        if not spec.exists() or not checker.exists() or not inputs_dir.exists():
            skipped += 1
            continue

        print(f"[INFO] checking {program_dir.name}")
        kept, removed = check_inputs_for_one(python, checker, inputs_dir, args.start, args.max, args.timeout)
        total_kept += kept
        total_removed += len(removed)

    print("-" * 50)
    print(f"[DONE] kept={total_kept}, removed={total_removed}, skipped={skipped}")


if __name__ == "__main__":
    main()
