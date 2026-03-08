import argparse
import subprocess
import sys
from pathlib import Path

# 用于启动输入生成器
def run(cmd: list[str], cwd: Path) -> None:
    try:
        subprocess.run(cmd, check=True, cwd=str(cwd))
    except subprocess.CalledProcessError as e:
        joined = " ".join(str(x) for x in cmd)
        raise RuntimeError(f"Command failed (exit={e.returncode}): {joined}") from e


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
    # Program folders are immediate children under PUT_cpp (e.g., p02547).
    return sorted([p for p in dataset_root.iterdir() if p.is_dir()])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="data/spec.txt")
    ap.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    ap.add_argument("--batch", action="store_true", help="Generate from every <program>/spec.txt under --dataset-root")
    ap.add_argument("--template", default="geninput_generator")
    ap.add_argument("--out", default="input_gen.py")
    ap.add_argument("--model", default="deepseek-chat")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable
    dataset_root = resolve_path(root, args.dataset_root)

    if args.batch:
        if not dataset_root.exists():
            raise FileNotFoundError(f"Dataset root not found: {dataset_root}")
        program_dirs = find_program_dirs(dataset_root)

        if not program_dirs:
            raise RuntimeError(f"No program folders found under: {dataset_root}")

        ok = 0
        skipped = 0
        for program_dir in program_dirs:
            spec = program_dir / "spec.txt"
            if not spec.exists():
                print(f"[SKIP] missing spec.txt: {spec}")
                skipped += 1
                continue

            out = resolve_out_for_spec(root, spec, args.out)
            run([
                py, "-m", "LLM_Gen.generator_generator",
                "--spec", str(spec),
                "--template", str(args.template),
                "--out", str(out),
                "--model", str(args.model),
            ], cwd=root)
            ok += 1

        print(f"[DONE] generated: {ok}, skipped: {skipped}, dataset: {dataset_root}")
        return

    spec = resolve_path(root, args.spec)
    out = resolve_out_for_spec(root, spec, args.out)

    run([
        py, "-m", "LLM_Gen.generator_generator",
        "--spec", str(spec),
        "--template", str(args.template),
        "--out", str(out),
        "--model", str(args.model),
    ], cwd=root)


if __name__ == "__main__":
    main()
