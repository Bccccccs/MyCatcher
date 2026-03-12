import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
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


def run_problem(
    root: Path,
    py: str,
    program_dir: Path,
    lang: str,
    variants_root: Path,
    tests_root: Path,
    out_root: Path,
    timeout: float,
    min_votes: int | None,
    variant_mode: str,
) -> tuple[str, str, str]:
    pid = program_dir.name
    put = find_put_file(program_dir, lang)
    variants_dir = variants_root / pid
    tests_dir = tests_root / pid
    out_dir = out_root / pid

    if not program_dir.exists():
        return ("skipped", pid, f"[SKIP] problem dir not found: {program_dir}")
    if put is None:
        return ("skipped", pid, f"[SKIP] missing put/sol in: {program_dir}")
    if not variants_dir.exists():
        return ("skipped", pid, f"[SKIP] variants not found: {variants_dir}")
    if not tests_dir.exists():
        return ("skipped", pid, f"[SKIP] tests not found: {tests_dir}")

    cmd = [
        py, str(root / "LLM_Gen" / "differential_testing.py"),
        "--lang", lang,
        "--variant_mode", variant_mode,
        "--put", str(put),
        "--variants", str(variants_dir),
        "--tests", str(tests_dir),
        "--out", str(out_dir),
        "--timeout", str(timeout),
    ]
    if min_votes is not None:
        cmd.extend(["--min_votes", str(min_votes)])

    try:
        run(cmd, cwd=root)
        return ("ok", pid, f"[OK] {pid}")
    except subprocess.CalledProcessError as e:
        return ("failed", pid, f"[FAIL] {pid}: {e}")


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
    ap.add_argument("--jobs", type=int, default=4, help="Number of problems to run in parallel")
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

    jobs = max(1, args.jobs)
    ok = 0
    skipped = 0
    failed = 0
    skip_messages: list[str] = []

    if jobs == 1:
        for program_dir in program_dirs:
            status, _, message = run_problem(
                root=root,
                py=py,
                program_dir=program_dir,
                lang=args.lang,
                variants_root=variants_root,
                tests_root=tests_root,
                out_root=out_root,
                timeout=args.timeout,
                min_votes=args.min_votes,
                variant_mode=args.variant_mode,
            )
            if status == "ok":
                print(message)
                ok += 1
            elif status == "skipped":
                skip_messages.append(message)
                skipped += 1
            else:
                print(message)
                failed += 1
    else:
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = [
                executor.submit(
                    run_problem,
                    root,
                    py,
                    program_dir,
                    args.lang,
                    variants_root,
                    tests_root,
                    out_root,
                    args.timeout,
                    args.min_votes,
                    args.variant_mode,
                )
                for program_dir in program_dirs
            ]
            for future in as_completed(futures):
                status, _, message = future.result()
                if status == "ok":
                    print(message)
                    ok += 1
                elif status == "skipped":
                    skip_messages.append(message)
                    skipped += 1
                else:
                    print(message)
                    failed += 1

    if skip_messages:
        print(f"[SKIP_SUMMARY] skipped={skipped}")
        for msg in skip_messages[:5]:
            print(msg)
        if len(skip_messages) > 5:
            print(f"[SKIP_SUMMARY] ... {len(skip_messages) - 5} more skipped problems")

    print(
        f"[DONE] total={len(program_dirs)} ok={ok} skipped={skipped} failed={failed} jobs={jobs} out_root={out_root}"
    )


if __name__ == "__main__":
    main()
