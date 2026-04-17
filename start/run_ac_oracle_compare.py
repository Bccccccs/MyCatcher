import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from LLM_Gen.differential_testing import run_program
from src.progress import log_line, print_progress, should_report_progress


VOTE_LINE_RE = re.compile(
    r"^\[VOTE\]\s+"
    r"(?P<test>\S+)\s+"
    r"status=(?P<status>\S+)\s+"
    r"votes=(?P<votes>\d+)/(?P<variant_total>\d+)"
    r"(?:\s+oracle='(?P<oracle>.*?)')?"
    r"(?:\s+put='(?P<put>.*?)')?"
    r"(?:\s+case=(?P<case>\S+))?"
    r"(?:\s+.*)?$"
)


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def find_program_dirs(ac_root: Path) -> list[Path]:
    return sorted(program_dir for program_dir in ac_root.iterdir() if program_dir.is_dir())


def find_put_file(program_dir: Path, lang: str, put_name: str | None) -> Path | None:
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_oracle_report(report_path: Path) -> dict[str, dict[str, str]]:
    oracle_by_test: dict[str, dict[str, str]] = {}
    for raw_line in report_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        match = VOTE_LINE_RE.match(line)
        if not match:
            continue
        info = match.groupdict()
        oracle_by_test[info["test"]] = {
            "status": info["status"] or "",
            "oracle": info["oracle"] or "",
            "put": info["put"] or "",
            "votes": info["votes"] or "",
            "variant_total": info["variant_total"] or "",
            "case": info["case"] or "",
        }
    return oracle_by_test


def write_problem_report(report_path: Path, rows: list[dict[str, str]], counts: Counter) -> None:
    lines = [
        "AC Solution vs Oracle Report",
        "",
        "Summary",
        f"total_inputs={counts['total_inputs']}",
        f"compared={counts['compared']}",
        f"match={counts['match']}",
        f"mismatch={counts['mismatch']}",
        f"run_fail={counts['run_fail']}",
        f"missing_oracle={counts['missing_oracle']}",
        "",
        "Details",
    ]

    for row in rows:
        detail = f"{row['test']} result={row['result']}"
        if row["oracle_status"]:
            detail += f" oracle_status={row['oracle_status']}"
        if row["oracle_votes"] and row["oracle_total"]:
            detail += f" votes={row['oracle_votes']}/{row['oracle_total']}"
        if row["oracle"] != "":
            detail += f" oracle='{row['oracle']}'"
        if row["actual"] != "":
            detail += f" actual='{row['actual']}'"
        if row["error"]:
            detail += f" error={row['error']}"
        lines.append(detail)

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Run AC solutions on legal inputs, save outputs, compare with differential-testing oracles, and summarize."
    )
    ap.add_argument("--pid", default=None, help="Single problem id under --ac-root, e.g. p02547")
    ap.add_argument("--ac-root", default="AC")
    ap.add_argument("--inputs-root", default="outputs/inputs", help="Legal input root, using <inputs-root>/<pid>/test_*.in")
    ap.add_argument("--oracle-root", default="outputs/tcases/cpp", help="Oracle report root, using <oracle-root>/<pid>/report.txt")
    ap.add_argument("--out-root", default="outputs/ac_oracle_compare/cpp", help="Directory to save actual outputs and comparison reports")
    ap.add_argument("--put-name", default=None, help="Correct solution filename inside each AC/<pid>/ directory")
    ap.add_argument("--lang", choices=["py", "cpp"], default="cpp")
    ap.add_argument("--timeout", type=float, default=2.0)
    args = ap.parse_args()

    root = ROOT
    ac_root = resolve_path(root, args.ac_root)
    inputs_root = resolve_path(root, args.inputs_root)
    oracle_root = resolve_path(root, args.oracle_root)
    out_root = resolve_path(root, args.out_root)

    if not ac_root.exists():
        raise FileNotFoundError(f"AC root not found: {ac_root}")
    if not inputs_root.exists():
        raise FileNotFoundError(f"Inputs root not found: {inputs_root}")
    if not oracle_root.exists():
        raise FileNotFoundError(f"Oracle root not found: {oracle_root}")

    if args.pid:
        program_dirs = [ac_root / args.pid]
    else:
        program_dirs = find_program_dirs(ac_root)

    build_dir = root / "build" / "cpp_bin"
    out_root.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, object]] = []
    global_counts: Counter = Counter()

    print_progress(0, len(program_dirs), f"problems ac_root={ac_root}")
    for problem_done, program_dir in enumerate(program_dirs, 1):
        pid = program_dir.name
        if not program_dir.exists():
            log_line(f"[SKIP] problem dir not found: {program_dir}")
            global_counts["skipped_problem_dir"] += 1
            print_progress(problem_done, len(program_dirs), f"problems skipped={pid}")
            continue

        put = find_put_file(program_dir, args.lang, args.put_name)
        if put is None:
            log_line(f"[SKIP] solution not found: {pid}")
            global_counts["skipped_missing_solution"] += 1
            print_progress(problem_done, len(program_dirs), f"problems skipped={pid}")
            continue

        tests_dir = inputs_root / pid
        report_path = oracle_root / pid / "report.txt"
        if not tests_dir.exists():
            log_line(f"[SKIP] inputs not found: {tests_dir}")
            global_counts["skipped_missing_inputs"] += 1
            print_progress(problem_done, len(program_dirs), f"problems skipped={pid}")
            continue
        if not report_path.exists():
            log_line(f"[SKIP] oracle report not found: {report_path}")
            global_counts["skipped_missing_report"] += 1
            print_progress(problem_done, len(program_dirs), f"problems skipped={pid}")
            continue

        oracle_by_test = parse_oracle_report(report_path)
        tests = sorted(tests_dir.glob("test_*.in"))
        program_out_dir = out_root / pid
        actual_dir = program_out_dir / "actual_outputs"
        actual_dir.mkdir(parents=True, exist_ok=True)

        counts: Counter = Counter()
        rows: list[dict[str, str]] = []

        print_progress(0, len(tests), f"tests problem={pid}")
        for test_done, test_file in enumerate(tests, 1):
            counts["total_inputs"] += 1
            test_name = test_file.name
            oracle_info = oracle_by_test.get(test_name)
            actual = ""
            error = ""

            try:
                actual = run_program(put, read_text(test_file), args.lang, build_dir, args.timeout)
                actual_path = actual_dir / test_file.with_suffix(".out").name
                actual_path.write_text(actual + "\n", encoding="utf-8")
            except Exception as exc:
                error = str(exc).splitlines()[0]
                counts["run_fail"] += 1
                rows.append({
                    "test": test_name,
                    "result": "RUN_FAIL",
                    "oracle_status": oracle_info["status"] if oracle_info else "",
                    "oracle_votes": oracle_info["votes"] if oracle_info else "",
                    "oracle_total": oracle_info["variant_total"] if oracle_info else "",
                    "oracle": oracle_info["oracle"] if oracle_info else "",
                    "actual": "",
                    "error": error,
                })
                if should_report_progress(test_done, len(tests)):
                    print_progress(test_done, len(tests), f"tests problem={pid} latest={test_name}")
                continue

            if oracle_info is None or oracle_info["oracle"] == "":
                counts["missing_oracle"] += 1
                rows.append({
                    "test": test_name,
                    "result": "MISSING_ORACLE",
                    "oracle_status": oracle_info["status"] if oracle_info else "",
                    "oracle_votes": oracle_info["votes"] if oracle_info else "",
                    "oracle_total": oracle_info["variant_total"] if oracle_info else "",
                    "oracle": oracle_info["oracle"] if oracle_info else "",
                    "actual": actual,
                    "error": "",
                })
                if should_report_progress(test_done, len(tests)):
                    print_progress(test_done, len(tests), f"tests problem={pid} latest={test_name}")
                continue

            counts["compared"] += 1
            if actual == oracle_info["oracle"]:
                counts["match"] += 1
                result = "MATCH"
            else:
                counts["mismatch"] += 1
                result = "MISMATCH"

            rows.append({
                "test": test_name,
                "result": result,
                "oracle_status": oracle_info["status"],
                "oracle_votes": oracle_info["votes"],
                "oracle_total": oracle_info["variant_total"],
                "oracle": oracle_info["oracle"],
                "actual": actual,
                "error": "",
            })
            if should_report_progress(test_done, len(tests)):
                print_progress(test_done, len(tests), f"tests problem={pid} latest={test_name}")

        write_problem_report(program_out_dir / "report.txt", rows, counts)

        with (program_out_dir / "compare.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=[
                    "test",
                    "result",
                    "oracle_status",
                    "oracle_votes",
                    "oracle_total",
                    "oracle",
                    "actual",
                    "error",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)

        summary_rows.append({
            "pid": pid,
            "total_inputs": counts["total_inputs"],
            "compared": counts["compared"],
            "match": counts["match"],
            "mismatch": counts["mismatch"],
            "run_fail": counts["run_fail"],
            "missing_oracle": counts["missing_oracle"],
        })
        global_counts.update(counts)
        log_line(
            f"[OK] {pid}: total={counts['total_inputs']} compared={counts['compared']} "
            f"match={counts['match']} mismatch={counts['mismatch']} "
            f"run_fail={counts['run_fail']} missing_oracle={counts['missing_oracle']}"
        )
        print_progress(problem_done, len(program_dirs), f"problems latest={pid}")

    summary_csv = out_root / "summary.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "pid",
                "total_inputs",
                "compared",
                "match",
                "mismatch",
                "run_fail",
                "missing_oracle",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    summary_txt = out_root / "summary.txt"
    lines = [
        "AC Solution vs Oracle Summary",
        "",
        f"problems={len(summary_rows)}",
        f"total_inputs={global_counts['total_inputs']}",
        f"compared={global_counts['compared']}",
        f"match={global_counts['match']}",
        f"mismatch={global_counts['mismatch']}",
        f"run_fail={global_counts['run_fail']}",
        f"missing_oracle={global_counts['missing_oracle']}",
        f"skipped_problem_dir={global_counts['skipped_problem_dir']}",
        f"skipped_missing_solution={global_counts['skipped_missing_solution']}",
        f"skipped_missing_inputs={global_counts['skipped_missing_inputs']}",
        f"skipped_missing_report={global_counts['skipped_missing_report']}",
    ]
    summary_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log_line(f"[DONE] summary -> {summary_txt}")


if __name__ == "__main__":
    main()
