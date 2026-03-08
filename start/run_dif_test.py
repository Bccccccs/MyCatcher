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


def is_probably_text_file(path: Path) -> bool:
    try:
        raw = path.read_bytes()
    except OSError:
        return False
    if b"\x00" in raw:
        return False
    try:
        raw.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def find_put_file(program_dir: Path, lang: str) -> Path | None:
    if lang == "cpp":
        candidates = [program_dir / "put.cpp"]
        candidates.extend(sorted(program_dir.glob("sol_*.cpp")))
        put_no_ext = program_dir / "put"
        if put_no_ext.exists() and is_probably_text_file(put_no_ext):
            candidates.append(put_no_ext)
    else:
        candidates = [program_dir / "put.py", program_dir / "put"]
        candidates.extend(sorted(program_dir.glob("sol_*.py")))

    for c in candidates:
        if c.exists():
            return c
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pid", default=None, help="Single problem id (e.g. p02547). If omitted, run all problems.")
    ap.add_argument("--lang", choices=["py", "cpp"], default="cpp")
    ap.add_argument("--variant-mode", choices=["my", "trickybugs"], default="trickybugs")
    ap.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    ap.add_argument("--variants-root", default="Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp")
    ap.add_argument("--tests-root", default="outputs/inputs")
    ap.add_argument("--out-root", default="outputs/tcases")
    ap.add_argument("--timeout", type=float, default=2.0)
    ap.add_argument("--min-votes", type=int, default=None)
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable

    dataset_root = resolve_path(root, args.dataset_root)
    variants_root = resolve_path(root, args.variants_root)
    tests_root = resolve_path(root, args.tests_root)
    out_root = resolve_path(root, args.out_root) / args.lang

    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")
    if not variants_root.exists():
        raise FileNotFoundError(f"Variants root not found: {variants_root}")
    if not tests_root.exists():
        raise FileNotFoundError(f"Tests root not found: {tests_root}")

    if args.pid:
        program_dirs = [dataset_root / args.pid]
    else:
        program_dirs = find_program_dirs(dataset_root)

    ok = 0
    skipped = 0
    failed = 0

    for program_dir in program_dirs:
        pid = program_dir.name
        put = find_put_file(program_dir, args.lang)
        variants_dir = variants_root / pid
        tests_dir = tests_root / pid
        out_dir = out_root / pid

        if not program_dir.exists():
            skipped += 1
            print(f"[SKIP] problem dir not found: {program_dir}")
            continue
        if put is None:
            skipped += 1
            print(f"[SKIP] missing put/sol in: {program_dir}")
            continue
        if not variants_dir.exists():
            skipped += 1
            print(f"[SKIP] variants not found: {variants_dir}")
            continue
        if not tests_dir.exists():
            skipped += 1
            print(f"[SKIP] tests not found: {tests_dir}")
            continue

        cmd = [
            py, str(root / "LLM_Gen" / "differential_testing.py"),
            "--lang", args.lang,
            "--variant_mode", args.variant_mode,
            "--put", str(put),
            "--variants", str(variants_dir),
            "--tests", str(tests_dir),
            "--out", str(out_dir),
            "--timeout", str(args.timeout),
        ]
        if args.min_votes is not None:
            cmd.extend(["--min_votes", str(args.min_votes)])

        try:
            run(cmd, cwd=root)
            ok += 1
        except subprocess.CalledProcessError as e:
            failed += 1
            print(f"[FAIL] {pid}: {e}")

    print(
        f"[DONE] total={len(program_dirs)} ok={ok} skipped={skipped} failed={failed} out_root={out_root}"
    )


if __name__ == "__main__":
    main()
