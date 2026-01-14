import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Batch-run checker and delete invalid inputs automatically"
    )
    parser.add_argument(
        "--max",
        type=int,
        required=True,
        help="Max input index (inclusive), e.g. --max 99",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start input index (default: 0)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Timeout seconds for checker (default: 2.0)",
    )
    args = parser.parse_args()

    if args.start < 0 or args.max < args.start:
        raise ValueError("Invalid range: require 0 <= start <= max")

    root = Path(__file__).resolve().parent.parent
    python = sys.executable

    checker = root / "outputs" / "checker" / "check_input.py"
    inputs_dir = root / "outputs" / "inputs"

    if not checker.exists():
        raise FileNotFoundError(f"Checker not found: {checker}")
    if not inputs_dir.exists():
        raise FileNotFoundError(f"Inputs dir not found: {inputs_dir}")

    print(f"[INFO] Checker: {checker}")
    print(f"[INFO] Inputs : {inputs_dir}")
    print(f"[INFO] Range  : {args.start}..{args.max}")

    kept = 0
    removed = []

    for i in range(args.start, args.max + 1):
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
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired:
            print(f"[DEL] test_{i:03d}.in  (checker timeout)")
            infile.unlink(missing_ok=True)
            removed.append(i)
            continue

        if r.returncode == 0:
            kept += 1
            print(f"[OK ] test_{i:03d}.in")
        else:
            msg = (r.stdout.strip() or r.stderr.strip() or "invalid input").strip()
            print(f"[DEL] test_{i:03d}.in  -> {msg}")
            infile.unlink(missing_ok=True)
            removed.append(i)

    print("-" * 50)
    print(f"[DONE] kept={kept}, removed={len(removed)}")
    if removed:
        print("[REMOVED INDICES]", removed)


if __name__ == "__main__":
    main()