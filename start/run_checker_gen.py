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


def resolve_out_for_spec(root: Path, spec: Path, out_arg: str) -> Path:
    p = Path(out_arg)
    if p.is_absolute():
        return p
    if p.parent == Path("."):
        return spec.parent / p.name
    return (root / p).resolve()


def find_program_dirs(dataset_root: Path) -> list[Path]:
    return sorted([p for p in dataset_root.iterdir() if p.is_dir()])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default=None, help="Single spec.txt path. If omitted, run for all <dataset-root>/*/spec.txt")
    ap.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    ap.add_argument("--template", default="geninput_inspector")
    ap.add_argument("--out", default="check_input.py", help="Default writes next to spec.txt")
    ap.add_argument("--model", default="deepseek-chat")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable

    if args.spec:
        spec = resolve_path(root, args.spec)
        out = resolve_out_for_spec(root, spec, args.out)
        if out.exists():
            print(f"[SKIP] checker exists: {out}")
            return
        run([
            py, "-m", "LLM_Gen.checker_generator",
            "--spec", str(spec),
            "--template", str(args.template),
            "--out", str(out),
            "--model", str(args.model),
        ], cwd=root)
        print(f"[DONE] checker: {out}")
        return

    dataset_root = resolve_path(root, args.dataset_root)
    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    ok = 0
    skipped = 0
    for program_dir in find_program_dirs(dataset_root):
        spec = program_dir / "spec.txt"
        if not spec.exists():
            skipped += 1
            continue

        out = resolve_out_for_spec(root, spec, args.out)
        if out.exists():
            skipped += 1
            print(f"[SKIP] checker exists: {out}")
            continue
        run([
            py, "-m", "LLM_Gen.checker_generator",
            "--spec", str(spec),
            "--template", str(args.template),
            "--out", str(out),
            "--model", str(args.model),
        ], cwd=root)
        ok += 1

    print(f"[DONE] generated={ok}, skipped={skipped}, dataset={dataset_root}")


if __name__ == "__main__":
    main()
