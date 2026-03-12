import argparse
import subprocess
import sys
from pathlib import Path
import random

def run(cmd: list[str], cwd: Path) -> None:
    print("\n>>>", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True, cwd=str(cwd))


def resolve_path(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (root / p).resolve()


def find_program_dirs(dataset_root: Path) -> list[Path]:
    return sorted([p for p in dataset_root.iterdir() if p.is_dir()])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=None, help="Single spec.txt path. If omitted, run for all <dataset-root>/*/spec.txt")
    ap.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    ap.add_argument("--generator-name", default="input_gen.py", help="Generator filename next to spec.txt")
    ap.add_argument("--out-root", default="outputs/inputs", help="Input data output root")
    ap.add_argument("--num", type=int, default=10)
    ap.add_argument("--seed", type=int, default=2)
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable
    out_root = resolve_path(root, args.out_root)

    if args.spec:
        spec = resolve_path(root, args.spec)
        generator = spec.parent / args.generator_name
        if not generator.exists():
            raise FileNotFoundError(f"Generator not found: {generator}")
        out_dir = out_root / spec.parent.name
        run([
            py, str(generator),
            "--out_dir", str(out_dir),
            "--num", str(args.num),
            "--seed", str(args.seed),
        ], cwd=root)
        print(f"[DONE] inputs -> {out_dir}")
        return

    dataset_root = resolve_path(root, args.dataset_root)
    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    ok = 0
    skipped = 0
    for program_dir in find_program_dirs(dataset_root):
        spec = program_dir / "spec.txt"
        generator = program_dir / args.generator_name
        if not spec.exists() or not generator.exists():
            skipped += 1
            continue

        out_dir = out_root / program_dir.name
        run([
            py, str(generator),
            "--out_dir", str(out_dir),
            "--num", str(args.num),
            "--seed", str(args.seed),
        ], cwd=root)
        ok += 1

    print(f"[DONE] generated={ok}, skipped={skipped}, out_root={out_root}")


if __name__ == "__main__":
    main()
