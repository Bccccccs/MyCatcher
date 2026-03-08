import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print("\n>>>", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True, cwd=str(cwd))


def resolve_path(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (root / p).resolve()


def find_program_dirs(dataset_root: Path) -> list[Path]:
    return sorted([p for p in dataset_root.iterdir() if p.is_dir()])


def find_put_file(program_dir: Path) -> Path | None:
    candidates = [
        program_dir / "put",
        program_dir / "put.py",
        program_dir / "put.cpp",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=None, help="Single spec.txt path. If omitted, run for all <dataset-root>/*/spec.txt")
    ap.add_argument("--put", default=None, help="PUT file path in single mode; default auto-detect from spec.txt folder")
    ap.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    ap.add_argument("--out-root", default="outputs/inputs", help="Input data output root")
    ap.add_argument("--num", default="10")
    ap.add_argument("--template", default="PromptTemplates/geninput_direct")
    ap.add_argument("--model", default="deepseek-chat")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable
    out_root = resolve_path(root, args.out_root)

    if args.spec:
        spec = resolve_path(root, args.spec)
        put = resolve_path(root, args.put) if args.put else (find_put_file(spec.parent) or spec.parent / "put")
        run([
            py, "-m", "LLM_Gen.input_generator",
            "--spec", str(spec),
            "--put", str(put),
            "--out", str(out_root),
            "--num", str(args.num),
            "--template", str(args.template),
            "--model", str(args.model),
        ], cwd=root)
        print(f"[DONE] inputs -> {out_root}")
        return

    dataset_root = resolve_path(root, args.dataset_root)
    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    ok = 0
    skipped = 0
    for program_dir in find_program_dirs(dataset_root):
        spec = program_dir / "spec.txt"
        put = find_put_file(program_dir)
        if not spec.exists() or put is None:
            skipped += 1
            print(f"[SKIP] missing spec.txt/put: {program_dir}")
            continue

        out_dir = out_root / program_dir.name
        run([
            py, "-m", "LLM_Gen.input_generator",
            "--spec", str(spec),
            "--put", str(put),
            "--out", str(out_dir),
            "--num", str(args.num),
            "--template", str(args.template),
            "--model", str(args.model),
        ], cwd=root)
        ok += 1

    print(f"[DONE] generated={ok}, skipped={skipped}, out_root={out_root}")


if __name__ == "__main__":
    main()
