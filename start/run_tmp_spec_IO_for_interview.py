
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


def resolve_output(spec: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (spec.parent / p).resolve()


def ensure_writable(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(
            f"Refusing to overwrite existing file: {path}. "
            "Use --force if you want to replace it."
        )


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Temporary wrapper: generate an input generator and checker from one spec.txt.txt."
    )
    ap.add_argument("--spec.txt", default="data/spec.txt.txt", help="Spec path relative to repo root or absolute path")
    ap.add_argument("--generator-out", default="tmp_input_gen.py", help="Generator output path, default next to spec.txt")
    ap.add_argument("--checker-out", default="tmp_check_input.py", help="Checker output path, default next to spec.txt")
    ap.add_argument("--generator-template", default="geninput_generator")
    ap.add_argument("--checker-template", default="geninput_inspector")
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--force", action="store_true", help="Overwrite output files if they already exist")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable

    spec = resolve_path(root, args.spec)
    if not spec.exists():
        raise FileNotFoundError(f"Spec not found: {spec}")

    generator_out = resolve_output(spec, args.generator_out)
    checker_out = resolve_output(spec, args.checker_out)

    ensure_writable(generator_out, args.force)
    ensure_writable(checker_out, args.force)

    run([
        py, "-m", "LLM_Gen.generator_generator",
        "--spec.txt", str(spec),
        "--template", str(args.generator_template),
        "--out", str(generator_out),
        "--model", str(args.model),
    ], cwd=root)

    run([
        py, "-m", "LLM_Gen.checker_generator",
        "--spec.txt", str(spec),
        "--template", str(args.checker_template),
        "--out", str(checker_out),
        "--model", str(args.model),
    ], cwd=root)

    print(f"[DONE] generator: {generator_out}")
    print(f"[DONE] checker: {checker_out}")


if __name__ == "__main__":
    main()
