import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import progress as _progress

log_line = getattr(_progress, "log_line", lambda message="": print(message, flush=True))
print_progress = _progress.print_progress
should_report_progress = _progress.should_report_progress


def resolve_path(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (root / p).resolve()


def find_program_dirs(dataset_root: Path) -> list[Path]:
    return sorted([p for p in dataset_root.iterdir() if p.is_dir()])


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def list_input_files(inputs_dir: Path) -> list[tuple[int, Path]]:
    files: list[tuple[int, Path]] = []
    for path in sorted(inputs_dir.glob("test_*.in")):
        stem = path.stem
        try:
            idx = int(stem.split("_")[-1])
        except ValueError:
            continue
        files.append((idx, path))
    return files


def check_one_input(
    python: str,
    checker: Path,
    infile: Path,
    timeout: float,
) -> tuple[str, int, str]:
    try:
        with infile.open("r", encoding="utf-8", errors="ignore") as fh:
            result = subprocess.run(
                [python, str(checker)],
                stdin=fh,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
    except subprocess.TimeoutExpired:
        infile.unlink(missing_ok=True)
        return ("removed", int(infile.stem.split("_")[-1]), f"[DEL] {infile} (checker timeout)")

    idx = int(infile.stem.split("_")[-1])
    if result.returncode == 0:
        return ("kept", idx, f"[OK ] {infile}")

    msg = (result.stdout.strip() or result.stderr.strip() or "invalid input").strip()
    checker_error_markers = (
        "Traceback (most recent call last)",
        "SyntaxError:",
        "IndentationError:",
        "NameError:",
        "TypeError:",
    )
    if any(marker in result.stderr for marker in checker_error_markers):
        first_line = msg.splitlines()[0] if msg else "checker failed"
        return ("checker_error", idx, f"[ERR] {infile} -> checker failed: {first_line}")

    infile.unlink(missing_ok=True)
    return ("removed", idx, f"[DEL] {infile} -> {msg}")


def check_inputs_for_one(
    python: str,
    checker: Path,
    inputs_dir: Path,
    start: int,
    max_i: int | None,
    timeout: float,
    jobs: int,
) -> tuple[int, list[int], list[str]]:
    kept = 0
    removed: list[int] = []
    log_lines: list[str] = []
    all_input_files = list_input_files(inputs_dir)
    if max_i is None:
        check_count = (len(all_input_files) * 9) // 10
        input_files = [path for _, path in all_input_files[:check_count]]
    else:
        input_files = [
            path
            for idx, path in all_input_files
            if start <= idx <= max_i
        ]
    print_progress(0, len(input_files), f"inputs dir={inputs_dir}")

    if jobs <= 1:
        for done, infile in enumerate(input_files, 1):
            status, idx, message = check_one_input(python, checker, infile, timeout)
            log_line(message)
            log_lines.append(message)
            if status == "kept":
                kept += 1
            elif status == "removed":
                removed.append(idx)
            if should_report_progress(done, len(input_files)):
                print_progress(done, len(input_files), f"inputs latest={infile.name}")
        return kept, sorted(removed), log_lines

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = [
            executor.submit(check_one_input, python, checker, infile, timeout)
            for infile in input_files
        ]
        for done, future in enumerate(as_completed(futures), 1):
            status, idx, message = future.result()
            log_line(message)
            log_lines.append(message)
            if status == "kept":
                kept += 1
            elif status == "removed":
                removed.append(idx)
            if should_report_progress(done, len(input_files)):
                print_progress(done, len(input_files), f"inputs checked={done}")

    log_lines.sort()
    return kept, sorted(removed), log_lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch-run checker and delete invalid inputs automatically")
    parser.add_argument("--spec", default=None, help="Single spec.txt path. If omitted, run for all <dataset-root>/*/spec.txt")
    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--checker-name", default="check_input.py")
    parser.add_argument("--inputs-root", default="outputs/inputs")
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Max input index (inclusive). Default checks only the first 9/10 inputs and leaves the last 1/10 untouched",
    )
    parser.add_argument("--start", type=int, default=0, help="Start input index")
    parser.add_argument("--timeout", type=float, default=10.0, help="Timeout seconds for checker")
    parser.add_argument("--jobs", type=int, default=8, help="Number of input files to check in parallel per problem")
    parser.add_argument("--log-name", default="checker_log.txt", help="Per-problem checker log filename")
    parser.add_argument("--summary-log", default="outputs/checker_logs/summary.txt", help="Batch summary log path")
    args = parser.parse_args()

    if args.start < 0:
        raise ValueError("Invalid range: require start >= 0")
    if args.max is not None and args.max < args.start:
        raise ValueError("Invalid range: require 0 <= start <= max")
    if args.jobs <= 0:
        raise ValueError("Invalid jobs: require jobs >= 1")

    root = Path(__file__).resolve().parent.parent
    python = sys.executable
    inputs_root = resolve_path(root, args.inputs_root)
    summary_log_path = resolve_path(root, args.summary_log)

    if args.spec:
        spec = resolve_path(root, args.spec)
        checker = spec.parent / args.checker_name
        inputs_dir = inputs_root
        log_path = inputs_dir / args.log_name
        if not checker.exists():
            raise FileNotFoundError(f"Checker not found: {checker}")
        if not inputs_dir.exists():
            raise FileNotFoundError(f"Inputs dir not found: {inputs_dir}")
        kept, removed, log_lines = check_inputs_for_one(
            python, checker, inputs_dir, args.start, args.max, args.timeout, args.jobs
        )
        report_lines = [
            "Checker Log",
            f"checker={checker}",
            f"inputs_dir={inputs_dir}",
            f"kept={kept}",
            f"removed={len(removed)}",
            f"jobs={args.jobs}",
            "",
            "Details",
            *log_lines,
        ]
        write_lines(log_path, report_lines)
        log_line("-" * 50)
        log_line(f"[DONE] kept={kept}, removed={len(removed)}, jobs={args.jobs}")
        log_line(f"[LOG] {log_path}")
        return

    dataset_root = resolve_path(root, args.dataset_root)
    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    total_kept = 0
    total_removed = 0
    skipped = 0
    summary_lines = [
        "Checker Batch Summary",
        f"dataset_root={dataset_root}",
        f"inputs_root={inputs_root}",
        f"jobs={args.jobs}",
        "",
        "Problems",
    ]

    program_dirs = find_program_dirs(dataset_root)
    for done, program_dir in enumerate(program_dirs, 1):
        spec = program_dir / "spec.txt"
        checker = program_dir / args.checker_name
        inputs_dir = inputs_root / program_dir.name
        if not spec.exists() or not checker.exists() or not inputs_dir.exists():
            skipped += 1
            print_progress(done, len(program_dirs), f"problems skipped={program_dir.name}")
            continue

        log_line(f"[INFO] checking {program_dir.name}")
        kept, removed, log_lines = check_inputs_for_one(
            python, checker, inputs_dir, args.start, args.max, args.timeout, args.jobs
        )
        log_path = inputs_dir / args.log_name
        write_lines(
            log_path,
            [
                "Checker Log",
                f"problem={program_dir.name}",
                f"checker={checker}",
                f"inputs_dir={inputs_dir}",
                f"kept={kept}",
                f"removed={len(removed)}",
                f"jobs={args.jobs}",
                "",
                "Details",
                *log_lines,
            ],
        )
        total_kept += kept
        total_removed += len(removed)
        summary_lines.append(
            f"{program_dir.name}: kept={kept} removed={len(removed)} log={log_path}"
        )
        print_progress(done, len(program_dirs), f"problems latest={program_dir.name}")

    summary_lines.extend(
        [
            "",
            "Totals",
            f"kept={total_kept}",
            f"removed={total_removed}",
            f"skipped={skipped}",
        ]
    )
    write_lines(summary_log_path, summary_lines)

    log_line("-" * 50)
    log_line(f"[DONE] kept={total_kept}, removed={total_removed}, skipped={skipped}, jobs={args.jobs}")
    log_line(f"[SUMMARY_LOG] {summary_log_path}")


if __name__ == "__main__":
    main()
