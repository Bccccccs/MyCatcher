import argparse
import json
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.progress import log_line, print_progress


HELP_TEXT = """
How to use:
  1. Run differential testing on TrickyBugs-style datasets:
     python3 start/run_dif_test.py --layout dataset

  2. Run only one dataset problem:
     python3 start/run_dif_test.py --layout dataset --pid p02547

  3. Run differential testing on AC problems:
     python3 start/run_dif_test.py --layout ac

  4. Run only one AC problem:
     python3 start/run_dif_test.py --layout ac --pid p02730

Layout meanings:
  - dataset: use dataset-root / variants-root / tests-root / out-root
  - ac: use AC/<pid>/solution + AC/<pid>/gen_bundle/variants + shared inputs root
""".strip()


def run(cmd: list[str], cwd: Path, *, line_prefix: str = "") -> str:
    process = subprocess.Popen(
        list(map(str, cmd)),
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    assert process.stdout is not None
    output_lines: list[str] = []
    for line in process.stdout:
        output_lines.append(line)
        rendered = f"{line_prefix}{line.rstrip()}" if line_prefix else line.rstrip()
        log_line(rendered)
    return_code = process.wait()
    output = "".join(output_lines)
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, list(map(str, cmd)), output=output)
    return output


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def find_program_dirs(root_dir: Path) -> list[Path]:
    return sorted(program_dir for program_dir in root_dir.iterdir() if program_dir.is_dir())


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


def find_dataset_put_file(program_dir: Path, lang: str) -> Path | None:
    if lang == "cpp":
        candidates = [program_dir / "put.cpp"]
        candidates.extend(sorted(program_dir.glob("sol_*.cpp")))
        put_no_ext = program_dir / "put"
        if put_no_ext.exists() and is_probably_text_file(put_no_ext):
            candidates.append(put_no_ext)
    else:
        candidates = [program_dir / "put.py", program_dir / "put"]
        candidates.extend(sorted(program_dir.glob("sol_*.py")))

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_ac_put_file(program_dir: Path, lang: str, put_name: str | None) -> Path | None:
    if put_name:
        candidate = program_dir / put_name
        return candidate if candidate.exists() else None

    if lang == "cpp":
        candidates = [program_dir / "ac_sol.cpp", program_dir / "put.cpp", program_dir / "ac_sol"]
    else:
        candidates = [program_dir / "ac_sol.py", program_dir / "put.py", program_dir / "ac_sol"]

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_canonical_file(ac_root: Path, pid: str, lang: str, canonical_name: str | None) -> Path | None:
    canonical_dir = ac_root / pid
    if canonical_name:
        candidate = canonical_dir / canonical_name
        return candidate if candidate.exists() else None
    return find_ac_put_file(canonical_dir, lang, None)


def build_diff_test_cmd(
    root: Path,
    py: str,
    lang: str,
    variant_mode: str,
    put: Path,
    canonical: Path | None,
    variants_dir: Path,
    tests_dir: Path,
    out_dir: Path,
    timeout: float,
    min_votes: int | None,
    fixed_min_votes: int,
    prefilter_variants: bool,
    prefilter_sample_size: int,
    prefilter_max_fail_rate: float,
    prefilter_max_mismatch_rate: float,
    prefilter_min_keep: int,
) -> list[str]:
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
    if canonical is not None:
        cmd.extend(["--canonical", str(canonical)])
    if min_votes is not None:
        cmd.extend(["--min_votes", str(min_votes)])
    else:
        cmd.extend(["--fixed-min-votes", str(fixed_min_votes)])
    if prefilter_variants:
        cmd.extend([
            "--prefilter-variants",
            "--prefilter-sample-size", str(prefilter_sample_size),
            "--prefilter-max-fail-rate", str(prefilter_max_fail_rate),
            "--prefilter-max-mismatch-rate", str(prefilter_max_mismatch_rate),
            "--prefilter-min-keep", str(prefilter_min_keep),
        ])
    return cmd


def write_raw_log(out_dir: Path, output: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "raw.log"
    log_path.write_text(output, encoding="utf-8")
    return log_path


def run_problem_dataset(
    root: Path,
    py: str,
    program_dir: Path,
    lang: str,
    variants_root: Path,
    tests_root: Path,
    out_root: Path,
    canonical_root: Path,
    canonical_name: str | None,
    allow_missing_canonical: bool,
    timeout: float,
    min_votes: int | None,
    fixed_min_votes: int,
    prefilter_variants: bool,
    prefilter_sample_size: int,
    prefilter_max_fail_rate: float,
    prefilter_max_mismatch_rate: float,
    prefilter_min_keep: int,
    variant_mode: str,
) -> tuple[str, str, str, str]:
    pid = program_dir.name
    put = find_dataset_put_file(program_dir, lang)
    canonical = find_canonical_file(canonical_root, pid, lang, canonical_name)
    variants_dir = variants_root / pid
    tests_dir = tests_root / pid
    out_dir = out_root / pid

    if not program_dir.exists():
        return ("skipped", pid, f"[SKIP] problem dir not found: {program_dir}", "")
    if put is None:
        return ("skipped", pid, f"[SKIP] missing put/sol in: {program_dir}", "")
    if canonical is None and not allow_missing_canonical:
        return ("skipped", pid, f"[SKIP] missing canonical solution in: {canonical_root / pid}", "")
    if not variants_dir.exists():
        return ("skipped", pid, f"[SKIP] variants not found: {variants_dir}", "")
    if not tests_dir.exists():
        return ("skipped", pid, f"[SKIP] tests not found: {tests_dir}", "")

    cmd = build_diff_test_cmd(
        root=root,
        py=py,
        lang=lang,
        variant_mode=variant_mode,
        put=put,
        canonical=canonical,
        variants_dir=variants_dir,
        tests_dir=tests_dir,
        out_dir=out_dir,
        timeout=timeout,
        min_votes=min_votes,
        fixed_min_votes=fixed_min_votes,
        prefilter_variants=prefilter_variants,
        prefilter_sample_size=prefilter_sample_size,
        prefilter_max_fail_rate=prefilter_max_fail_rate,
        prefilter_max_mismatch_rate=prefilter_max_mismatch_rate,
        prefilter_min_keep=prefilter_min_keep,
    )
    try:
        output = run(cmd, cwd=root, line_prefix=f"[{pid}] ")
        log_path = write_raw_log(out_dir, output)
        return ("ok", pid, f"[OK] {pid} raw_log={log_path}", output)
    except subprocess.CalledProcessError as exc:
        output = exc.stdout or ""
        log_path = write_raw_log(out_dir, output)
        return ("failed", pid, f"[FAIL] {pid}: {exc} raw_log={log_path}", output)


def run_problem_ac(
    root: Path,
    py: str,
    program_dir: Path,
    lang: str,
    inputs_root: Path,
    bundle_dirname: str,
    variants_dirname: str,
    out_dirname: str,
    put_name: str | None,
    canonical_name: str | None,
    timeout: float,
    min_votes: int | None,
    fixed_min_votes: int,
    prefilter_variants: bool,
    prefilter_sample_size: int,
    prefilter_max_fail_rate: float,
    prefilter_max_mismatch_rate: float,
    prefilter_min_keep: int,
    variant_mode: str,
) -> tuple[str, str, str, str]:
    pid = program_dir.name
    put = find_ac_put_file(program_dir, lang, put_name)
    canonical = find_ac_put_file(program_dir, lang, canonical_name)
    bundle_dir = program_dir / bundle_dirname
    variants_dir = bundle_dir / variants_dirname
    tests_dir = inputs_root / pid
    out_dir = bundle_dir / out_dirname

    if not program_dir.exists():
        return ("skipped", pid, f"[SKIP] problem dir not found: {program_dir}", "")
    if put is None:
        return ("skipped", pid, f"[SKIP] missing AC solution in: {program_dir}", "")
    if canonical is None:
        return ("skipped", pid, f"[SKIP] missing canonical solution in: {program_dir}", "")
    if not variants_dir.exists():
        return ("skipped", pid, f"[SKIP] variants not found: {variants_dir}", "")
    if not tests_dir.exists():
        return ("skipped", pid, f"[SKIP] tests not found: {tests_dir}", "")

    cmd = build_diff_test_cmd(
        root=root,
        py=py,
        lang=lang,
        variant_mode=variant_mode,
        put=put,
        canonical=canonical,
        variants_dir=variants_dir,
        tests_dir=tests_dir,
        out_dir=out_dir,
        timeout=timeout,
        min_votes=min_votes,
        fixed_min_votes=fixed_min_votes,
        prefilter_variants=prefilter_variants,
        prefilter_sample_size=prefilter_sample_size,
        prefilter_max_fail_rate=prefilter_max_fail_rate,
        prefilter_max_mismatch_rate=prefilter_max_mismatch_rate,
        prefilter_min_keep=prefilter_min_keep,
    )
    try:
        output = run(cmd, cwd=root, line_prefix=f"[{pid}] ")
        log_path = write_raw_log(out_dir, output)
        return ("ok", pid, f"[OK] {pid} raw_log={log_path}", output)
    except subprocess.CalledProcessError as exc:
        output = exc.stdout or ""
        log_path = write_raw_log(out_dir, output)
        return ("failed", pid, f"[FAIL] {pid}: {exc} raw_log={log_path}", output)


SUMMARY_KEYS = [
    "saved",
    "agree",
    "found",
    "no_majority",
    "no_variant_output",
    "put_fail",
    "tp_count",
    "fp_count",
    "oracle_wrong_count",
    "canonical_fail_count",
]


def load_problem_summary(problem_out_dir: Path) -> dict[str, object] | None:
    summary_path = problem_out_dir / "summary.json"
    if summary_path.exists():
        return json.loads(summary_path.read_text(encoding="utf-8"))

    report_path = problem_out_dir / "report.txt"
    if not report_path.exists():
        return None

    summary: dict[str, object] = {"report": str(report_path)}
    lines = report_path.read_text(encoding="utf-8").splitlines()
    try:
        summary_index = lines.index("Summary")
    except ValueError:
        return None

    for line in lines[summary_index + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "Details" or stripped.startswith("Variant Fail Summary"):
            break
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key in SUMMARY_KEYS:
            summary[key] = int(value)

    for line in lines:
        if line.startswith("Tests dir size:"):
            summary["tests_dir_size"] = int(line.split(":", 1)[1].strip())
            break

    return summary


def format_stats_line(summary: dict[str, object] | None) -> str:
    if not summary:
        return ""
    return (
        "[STATS] "
        f"tests={summary.get('tests_dir_size', 0)} "
        f"saved={summary.get('saved', 0)} "
        f"agree={summary.get('agree', 0)} "
        f"found={summary.get('found', 0)} "
        f"no_majority={summary.get('no_majority', 0)} "
        f"no_variant_output={summary.get('no_variant_output', 0)} "
        f"put_fail={summary.get('put_fail', 0)} "
        f"tp_count={summary.get('tp_count', 0)} "
        f"fp_count={summary.get('fp_count', 0)} "
        f"oracle_wrong_count={summary.get('oracle_wrong_count', 0)} "
        f"canonical_fail_count={summary.get('canonical_fail_count', 0)} "
        f"report={summary.get('report', '')}"
    )


def write_batch_report(
    report_path: Path,
    total: int,
    ok: int,
    skipped: int,
    failed: int,
    jobs: int,
    out_root: Path,
    problem_results: list[tuple[str, str, str, str]],
) -> None:
    per_status = Counter(status for status, _, _, _ in problem_results)
    totals = Counter()
    lines = [
        "Differential Testing Batch Report",
        "Summary",
        f"total={total}",
        f"ok={ok}",
        f"skipped={skipped}",
        f"failed={failed}",
        f"jobs={jobs}",
        f"out_root={out_root}",
        "",
        "Problems",
    ]

    for status, pid, message, output in sorted(problem_results, key=lambda item: item[1]):
        lines.append(f"{pid}: {status} {message}")
        summary = load_problem_summary(out_root / pid)
        stats_line = format_stats_line(summary)
        if stats_line:
            lines.append(f"  {stats_line}")
            totals["tests"] += int(summary.get("tests_dir_size", 0))
            for key in SUMMARY_KEYS:
                totals[key] += int(summary.get(key, 0))

    lines.extend(
        [
            "",
            "Status Count Check",
            f"ok={per_status.get('ok', 0)}",
            f"skipped={per_status.get('skipped', 0)}",
            f"failed={per_status.get('failed', 0)}",
            "",
            "Metric Totals",
            f"tests={totals.get('tests', 0)}",
            f"saved={totals.get('saved', 0)}",
            f"agree={totals.get('agree', 0)}",
            f"found={totals.get('found', 0)}",
            f"no_majority={totals.get('no_majority', 0)}",
            f"no_variant_output={totals.get('no_variant_output', 0)}",
            f"put_fail={totals.get('put_fail', 0)}",
            f"tp_count={totals.get('tp_count', 0)}",
            f"fp_count={totals.get('fp_count', 0)}",
            f"oracle_wrong_count={totals.get('oracle_wrong_count', 0)}",
            f"canonical_fail_count={totals.get('canonical_fail_count', 0)}",
            (
                f"precision={totals.get('tp_count', 0) / (totals.get('tp_count', 0) + totals.get('fp_count', 0)):.6f}"
                if totals.get("tp_count", 0) + totals.get("fp_count", 0) > 0
                else "precision="
            ),
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run differential testing on dataset-style or AC-style problem layouts.",
        epilog=HELP_TEXT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--layout",
        choices=["dataset", "ac"],
        default="dataset",
        help="Choose problem directory layout. Default: dataset",
    )
    parser.add_argument("--pid", default=None, help="Single problem id (e.g. p02547). If omitted, run all problems.")
    parser.add_argument("--lang", choices=["py", "cpp"], default="cpp")
    parser.add_argument("--variant-mode", choices=["my", "trickybugs"], default="trickybugs")

    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--variants-root", default="Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp")
    parser.add_argument("--out-root", default="outputs/tcases")
    parser.add_argument("--canonical-root", default="AC", help="Dataset layout only. Canonical solutions root, using AC/<pid>/")
    parser.add_argument("--canonical-name", default=None, help="Canonical solution filename inside AC/<pid>/ or AC layout problem dir")
    parser.add_argument(
        "--allow-missing-canonical",
        action="store_true",
        help="Dataset layout only. Continue differential testing even when AC/<pid>/ canonical is missing.",
    )

    parser.add_argument("--ac-root", default="AC")
    parser.add_argument("--put-name", default=None, help="AC layout only. Solution filename inside AC/<pid>/")
    parser.add_argument("--bundle-dir", default="gen_bundle", help="AC layout only. Bundle directory inside AC/<pid>/")
    parser.add_argument("--variants-dirname", default="variants", help="AC layout only. Variants directory inside bundle dir")
    parser.add_argument("--out-dirname", default="tcases", help="AC layout only. Output directory inside bundle dir")

    parser.add_argument("--tests-root", default="outputs/inputs")
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--min-votes", type=int, default=None)
    parser.add_argument("--fixed-min-votes", type=int, default=6, help="Fixed-vote threshold")
    parser.add_argument("--prefilter-variants", action="store_true", help="Drop variants that fail or disagree with canonical on sample tests")
    parser.add_argument("--prefilter-sample-size", type=int, default=20, help="Number of input tests used for variant prefiltering")
    parser.add_argument("--prefilter-max-fail-rate", type=float, default=0.2, help="Maximum allowed prefilter runtime/compile fail rate")
    parser.add_argument("--prefilter-max-mismatch-rate", type=float, default=0.3, help="Maximum allowed mismatch rate against canonical among successful sample runs")
    parser.add_argument("--prefilter-min-keep", type=int, default=3, help="Fallback to all variants if fewer than this many variants pass prefilter")
    parser.add_argument("--jobs", type=int, default=8, help="Number of problems to run in parallel")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable
    tests_root = resolve_path(root, args.tests_root)
    if not tests_root.exists():
        raise FileNotFoundError(f"Tests root not found: {tests_root}")

    if args.layout == "dataset":
        problem_root = resolve_path(root, args.dataset_root)
        variants_root = resolve_path(root, args.variants_root)
        canonical_root = resolve_path(root, args.canonical_root)
        report_root = resolve_path(root, args.out_root) / args.lang
        if not problem_root.exists():
            raise FileNotFoundError(f"Dataset root not found: {problem_root}")
        if not variants_root.exists():
            raise FileNotFoundError(f"Variants root not found: {variants_root}")
        if not args.allow_missing_canonical and not canonical_root.exists():
            raise FileNotFoundError(f"Canonical root not found: {canonical_root}")
    else:
        problem_root = resolve_path(root, args.ac_root)
        variants_root = None
        canonical_root = None
        report_root = problem_root
        if not problem_root.exists():
            raise FileNotFoundError(f"AC root not found: {problem_root}")

    if args.pid:
        program_dirs = [problem_root / args.pid]
    else:
        program_dirs = find_program_dirs(problem_root)

    jobs = max(1, args.jobs)
    ok = 0
    skipped = 0
    failed = 0
    skip_messages: list[str] = []
    problem_results: list[tuple[str, str, str, str]] = []

    def run_one(program_dir: Path) -> tuple[str, str, str, str]:
        if args.layout == "dataset":
            return run_problem_dataset(
                root=root,
                py=py,
                program_dir=program_dir,
                lang=args.lang,
                variants_root=variants_root,
                tests_root=tests_root,
                out_root=report_root,
                canonical_root=canonical_root,
                canonical_name=args.canonical_name,
                allow_missing_canonical=args.allow_missing_canonical,
                timeout=args.timeout,
                min_votes=args.min_votes,
                fixed_min_votes=args.fixed_min_votes,
                prefilter_variants=args.prefilter_variants,
                prefilter_sample_size=args.prefilter_sample_size,
                prefilter_max_fail_rate=args.prefilter_max_fail_rate,
                prefilter_max_mismatch_rate=args.prefilter_max_mismatch_rate,
                prefilter_min_keep=args.prefilter_min_keep,
                variant_mode=args.variant_mode,
            )
        return run_problem_ac(
            root=root,
            py=py,
            program_dir=program_dir,
            lang=args.lang,
            inputs_root=tests_root,
            bundle_dirname=args.bundle_dir,
            variants_dirname=args.variants_dirname,
            out_dirname=args.out_dirname,
            put_name=args.put_name,
            canonical_name=args.canonical_name,
            timeout=args.timeout,
            min_votes=args.min_votes,
            fixed_min_votes=args.fixed_min_votes,
            prefilter_variants=args.prefilter_variants,
            prefilter_sample_size=args.prefilter_sample_size,
            prefilter_max_fail_rate=args.prefilter_max_fail_rate,
            prefilter_max_mismatch_rate=args.prefilter_max_mismatch_rate,
            prefilter_min_keep=args.prefilter_min_keep,
            variant_mode=args.variant_mode,
        )

    if jobs == 1:
        for done, program_dir in enumerate(program_dirs, 1):
            status, pid, message, output = run_one(program_dir)
            problem_results.append((status, pid, message, output))
            if status == "ok":
                log_line(message)
                stats_line = format_stats_line(load_problem_summary(report_root / pid))
                if stats_line:
                    log_line(stats_line)
                ok += 1
            elif status == "skipped":
                skip_messages.append(message)
                skipped += 1
            else:
                log_line(message)
                if output.strip():
                    log_line(output.strip())
                failed += 1
            print_progress(done, len(program_dirs), f"problems latest={pid}")
    else:
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = [executor.submit(run_one, program_dir) for program_dir in program_dirs]
            for done, future in enumerate(as_completed(futures), 1):
                status, pid, message, output = future.result()
                problem_results.append((status, pid, message, output))
                if status == "ok":
                    log_line(message)
                    stats_line = format_stats_line(load_problem_summary(report_root / pid))
                    if stats_line:
                        log_line(stats_line)
                    ok += 1
                elif status == "skipped":
                    skip_messages.append(message)
                    skipped += 1
                else:
                    log_line(message)
                    if output.strip():
                        log_line(output.strip())
                    failed += 1
                print_progress(done, len(program_dirs), f"problems latest={pid}")

    if skip_messages:
        log_line(f"[SKIP_SUMMARY] skipped={skipped}")
        for message in skip_messages[:5]:
            log_line(message)
        if len(skip_messages) > 5:
            log_line(f"[SKIP_SUMMARY] ... {len(skip_messages) - 5} more skipped problems")

    batch_report_path = report_root / "batch_report.txt"
    write_batch_report(
        report_path=batch_report_path,
        total=len(program_dirs),
        ok=ok,
        skipped=skipped,
        failed=failed,
        jobs=jobs,
        out_root=report_root,
        problem_results=problem_results,
    )

    log_line(
        f"[DONE] total={len(program_dirs)} ok={ok} skipped={skipped} failed={failed} "
        f"jobs={jobs} out_root={report_root}"
    )
    log_line(f"[BATCH_REPORT] {batch_report_path}")


if __name__ == "__main__":
    main()
