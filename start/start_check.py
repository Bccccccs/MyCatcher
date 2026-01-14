import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Batch-run outputs/checker/check_input.py on outputs/inputs/test_XXX.in"
    )
    parser.add_argument(
        "--max",
        type=int,
        required=True,
        help="Max input index (inclusive). Example: --max 9 checks test_000.in ~ test_009.in",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start input index (default: 0)",
    )
    parser.add_argument(
        "--stop_on_error",
        action="store_true",
        help="Stop immediately when a bad input is found",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Timeout seconds for each check run (default: 2.0)",
    )
    args = parser.parse_args()

    if args.start < 0 or args.max < 0 or args.max < args.start:
        raise ValueError("Invalid range: require 0 <= start <= max")

    # Project root = parent of start/
    root = Path(__file__).resolve().parent.parent

    checker = root / "outputs" / "checker" / "check_input.py"
    inputs_dir = root / "outputs" / "inputs"

    if not checker.exists():
        raise FileNotFoundError(f"Checker not found: {checker}")

    if not inputs_dir.exists():
        raise FileNotFoundError(f"Inputs directory not found: {inputs_dir}")

    python = sys.executable  # use current venv python

    print(f"[INFO] Checker : {checker}")
    print(f"[INFO] Inputs  : {inputs_dir}")
    print(f"[INFO] Range   : {args.start}..{args.max} (inclusive)")

    checked = 0
    missing = 0
    bad = []

    for i in range(args.start, args.max + 1):
        infile = inputs_dir / f"test_{i:03d}.in"
        if not infile.exists():
            print(f"[WARN] missing test_{i:03d}.in")
            missing += 1
            continue

        checked += 1
        try:
            r = subprocess.run(
                [python, str(checker)],
                stdin=infile.open("r", encoding="utf-8", errors="ignore"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired:
            print(f"[BAD]  test_{i:03d}.in  (timeout)")
            bad.append(i)
            if args.stop_on_error:
                break
            continue

        # Convention: checker returns exit code 0 if ok, non-zero if invalid
        if r.returncode == 0:
            print(f"[OK]   test_{i:03d}.in")
        else:
            msg = (r.stdout.strip() or r.stderr.strip() or "invalid input").strip()
            print(f"[BAD]  test_{i:03d}.in  -> {msg}")
            bad.append(i)
            if args.stop_on_error:
                break

    print("-" * 50)
    print(f"[DONE] checked={checked}, missing={missing}, bad={len(bad)}")
    if bad:
        print("[BAD INDICES]", bad)


if __name__ == "__main__":
    main()