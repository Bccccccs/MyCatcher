import argparse
import csv
import json
import sys
import subprocess
import io
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def ensure_csv_field_limit() -> None:
    limit = sys.maxsize
    while limit > 0:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 10

PER_PROBLEM_FIELDS = [
    "pid",
    "tests",
    "found",
    "agree",
    "no_majority",
    "no_variant_output",
    "put_fail",
    "tp_count",
    "fp_count",
    "oracle_wrong_count",
    "canonical_fail_count",
    "precision",
    "category",
    "report",
    "detail_csv",
]

TEST_CASE_FIELDS = [
    "pid",
    "test_name",
    "is_valid",
    "predicted_bug",
    "status",
    "oracle_output",
    "canonical_output",
    "put_output",
    "oracle_correct",
    "put_wrong",
    "final_label",
]


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (ROOT / path).resolve()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_int(value: object) -> int:
    if value in (None, ""):
        return 0
    return int(value)


def parse_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return None
    lowered = str(value).strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return None


def read_detail_rows(detail_path: Path, pid: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not detail_path.exists():
        return rows
    raw_text = detail_path.read_text(encoding="utf-8", errors="ignore")
    if "\x00" in raw_text:
        raw_text = raw_text.replace("\x00", "")
    reader = csv.DictReader(io.StringIO(raw_text))
    for raw in reader:
        rows.append(normalize_detail_row(raw, pid))
    return rows


def normalize_detail_row(raw: dict[str, str], pid: str) -> dict[str, object]:
    # These names are the stable test-case level contract used by DPP now and TC later.
    return {
        "pid": raw.get("pid") or pid,
        "test_name": raw.get("test_name") or raw.get("test") or "",
        "is_valid": parse_bool(raw.get("is_valid")),
        "predicted_bug": parse_bool(raw.get("predicted_bug")),
        "status": raw.get("status", ""),
        "oracle_output": raw.get("oracle_output") or raw.get("oracle") or "",
        "canonical_output": raw.get("canonical_output") or raw.get("canonical_out") or "",
        "put_output": raw.get("put_output") or raw.get("put_out") or "",
        "oracle_correct": parse_bool(raw.get("oracle_correct")),
        "put_wrong": parse_bool(raw.get("put_wrong")),
        "final_label": raw.get("final_label", ""),
        "votes": raw.get("votes", ""),
        "variant_total": raw.get("variant_total", ""),
        "canonical_error": raw.get("canonical_error", ""),
        "saved_case": raw.get("saved_case", ""),
    }


def parse_batch_counts(batch_report: Path) -> dict[str, int]:
    counts = {"total_problems": 0, "ok_problems": 0, "skipped_problems": 0, "failed_problems": 0}
    if not batch_report.exists():
        return counts
    key_map = {
        "total": "total_problems",
        "ok": "ok_problems",
        "skipped": "skipped_problems",
        "failed": "failed_problems",
    }
    for line in batch_report.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        mapped = key_map.get(key.strip())
        if mapped and str(value).strip().isdigit():
            counts[mapped] = int(value)
    return counts


def classify_problem_category(row: dict[str, object]) -> str:
    fp_count = to_int(row["fp_count"])
    tp_count = to_int(row["tp_count"])
    canonical_fail_count = to_int(row["canonical_fail_count"])
    found = to_int(row["found"])
    agree = to_int(row["agree"])
    tests = to_int(row["tests"])
    if fp_count == 0 and canonical_fail_count == 0 and tp_count > 0:
        return "high_quality_tp"
    if fp_count >= tp_count and fp_count > 0:
        return "high_fp"
    if canonical_fail_count >= 50:
        return "canonical_fail_heavy"
    if found == 0 and tests > 0 and agree >= tests * 0.95:
        return "all_agree"
    if tp_count == 0 and fp_count == 0 and found == 0:
        return "no_detection"
    return "mixed"


def summarize_baseline_results(report_root: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    per_problem: list[dict[str, object]] = []
    test_cases: list[dict[str, object]] = []
    for summary_path in sorted(report_root.glob("*/summary.json")):
        pid = summary_path.parent.name
        summary = read_json(summary_path)
        detail_path = summary_path.parent / "detail.csv"
        tp_count = to_int(summary.get("tp_count"))
        fp_count = to_int(summary.get("fp_count"))
        denominator = tp_count + fp_count
        row: dict[str, object] = {
            "pid": pid,
            "tests": to_int(summary.get("tests_dir_size")),
            "found": to_int(summary.get("found")),
            "agree": to_int(summary.get("agree")),
            "no_majority": to_int(summary.get("no_majority")),
            "no_variant_output": to_int(summary.get("no_variant_output")),
            "put_fail": to_int(summary.get("put_fail")),
            "tp_count": tp_count,
            "fp_count": fp_count,
            "oracle_wrong_count": to_int(summary.get("oracle_wrong_count")),
            "canonical_fail_count": to_int(summary.get("canonical_fail_count")),
            "precision": (tp_count / denominator) if denominator else "",
            "report": summary.get("report", str(summary_path.parent / "report.txt")),
            "detail_csv": str(detail_path),
        }
        row["category"] = classify_problem_category(row)
        per_problem.append(row)
        test_cases.extend(read_detail_rows(detail_path, pid))
    return per_problem, test_cases


def explain_unclassified_found(row: dict[str, object]) -> str:
    if row["canonical_error"]:
        return "canonical_run_failed"
    if row["canonical_output"] == "":
        return "canonical_output_missing_or_empty"
    if row["oracle_output"] == "":
        return "oracle_missing"
    if row["put_output"] == "":
        return "put_output_missing"
    if row["predicted_bug"] is not True:
        return "status_found_but_predicted_bug_not_true"
    if row["final_label"] in ("", None):
        return "final_label_missing"
    return f"final_label_{row['final_label']}_not_counted_as_tp_or_fp"


def find_unclassified_found_cases(test_cases: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in test_cases:
        if row["status"] != "FOUND":
            continue
        if row["final_label"] in ("TP", "FP"):
            continue
        rows.append({
            "pid": row["pid"],
            "test_name": row["test_name"],
            "status": row["status"],
            "predicted_bug": row["predicted_bug"],
            "oracle_output": row["oracle_output"],
            "canonical_output": row["canonical_output"],
            "put_output": row["put_output"],
            "final_label": row["final_label"],
            "failure_reason": explain_unclassified_found(row),
        })
    return rows


def canonical_error_kind(message: str) -> str:
    lowered = message.lower()
    if "compile failed" in lowered:
        return "compile"
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout"
    if "program failed" in lowered:
        return "runtime"
    if message:
        return "runtime"
    return ""


def compare_normalize(value: str) -> str:
    lines = str(value).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized = [line.rstrip() for line in lines]
    while normalized and normalized[-1] == "":
        normalized.pop()
    return "\n".join(normalized)


def check_canonical_compile(canonical_path: str, build_root: Path, compiler: str) -> tuple[bool, str]:
    if not canonical_path:
        return False, "canonical path missing"
    src = Path(canonical_path)
    if not src.exists():
        return False, "canonical file missing"
    if src.suffix != ".cpp":
        return True, "non-cpp compile check skipped"
    build_root.mkdir(parents=True, exist_ok=True)
    exe = build_root / src.parent.name
    cmd = [compiler, "-std=c++17", "-O2", "-pipe", str(src), "-o", str(exe)]
    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if completed.returncode == 0:
        return True, ""
    note = completed.stderr.splitlines()[0] if completed.stderr.splitlines() else "compile failed without stderr"
    return False, note


def analyze_canonical_failures(
    per_problem: list[dict[str, object]],
    test_cases: list[dict[str, object]],
    report_root: Path,
    out_dir: Path,
    compiler: str,
    check_compile: bool,
) -> list[dict[str, object]]:
    by_pid: dict[str, list[dict[str, object]]] = {}
    for row in test_cases:
        by_pid.setdefault(str(row["pid"]), []).append(row)

    compile_build_root = out_dir / "canonical_build"
    rows: list[dict[str, object]] = []
    for problem in per_problem:
        pid = str(problem["pid"])
        summary = read_json(report_root / pid / "summary.json")
        problem_rows = by_pid.get(pid, [])
        errors = [str(row["canonical_error"]) for row in problem_rows if row["canonical_error"]]
        error_counts = Counter(canonical_error_kind(message) for message in errors)
        empty_output_count = sum(
            1 for row in problem_rows
            if not row["canonical_error"] and row["canonical_output"] == ""
        )
        compile_ok = ""
        compile_note = ""
        if check_compile:
            compile_ok_bool, compile_note = check_canonical_compile(
                str(summary.get("canonical", "")),
                compile_build_root,
                compiler,
            )
            compile_ok = str(compile_ok_bool)
        compare_issue_suspected = any(
            (
                not row["canonical_error"]
                and row["oracle_output"] != ""
                and row["oracle_correct"] is False
                and compare_normalize(str(row["oracle_output"])) == compare_normalize(str(row["canonical_output"]))
            )
            or (
                not row["canonical_error"]
                and row["put_output"] != ""
                and row["put_wrong"] is True
                and compare_normalize(str(row["put_output"])) == compare_normalize(str(row["canonical_output"]))
            )
            for row in problem_rows
        )
        notes = []
        if errors:
            notes.append(f"top_error={Counter(errors).most_common(1)[0][0]}")
        if compile_note:
            notes.append(f"compile_note={compile_note}")
        if to_int(problem["canonical_fail_count"]) >= 50 and not errors:
            notes.append("high canonical_fail_count without captured canonical_error")
        rows.append({
            "pid": pid,
            "canonical_fail_count": problem["canonical_fail_count"],
            "compile_ok": compile_ok,
            "runtime_fail_count": error_counts.get("runtime", 0),
            "timeout_count": error_counts.get("timeout", 0),
            "empty_output_count": empty_output_count,
            "compare_issue_suspected": compare_issue_suspected,
            "notes": "; ".join(notes),
        })
    return rows


def analyze_high_fp(per_problem: list[dict[str, object]], test_cases: list[dict[str, object]]) -> list[dict[str, object]]:
    found_rows_by_pid: dict[str, list[dict[str, object]]] = {}
    for row in test_cases:
        found_rows_by_pid.setdefault(str(row["pid"]), []).append(row)
    rows: list[dict[str, object]] = []
    for problem in per_problem:
        fp_count = to_int(problem["fp_count"])
        tp_count = to_int(problem["tp_count"])
        if not (fp_count >= tp_count and fp_count > 0):
            continue
        pid = str(problem["pid"])
        problem_rows = found_rows_by_pid.get(pid, [])
        oracle_wrong_and_found_count = sum(
            1 for row in problem_rows
            if row["status"] == "FOUND" and row["oracle_correct"] is False
        )
        oracle_wrong_and_no_majority_count = sum(
            1 for row in problem_rows
            if row["status"] == "NO_MAJORITY" and row["oracle_correct"] is False
        )
        rows.append({
            "pid": pid,
            "fp_count": fp_count,
            "tp_count": tp_count,
            "oracle_wrong_count": problem["oracle_wrong_count"],
            "found": problem["found"],
            "no_majority": problem["no_majority"],
            "canonical_fail_count": problem["canonical_fail_count"],
            "oracle_wrong_and_found_count": oracle_wrong_and_found_count,
            "oracle_wrong_and_no_majority_count": oracle_wrong_and_no_majority_count,
        })
    return sorted(rows, key=lambda row: (-to_int(row["fp_count"]), row["pid"]))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def write_global_summary(
    path: Path,
    csv_path: Path,
    batch_counts: dict[str, int],
    per_problem: list[dict[str, object]],
) -> dict[str, object]:
    totals = Counter()
    for row in per_problem:
        totals["tests"] += to_int(row["tests"])
        totals["found"] += to_int(row["found"])
        totals["tp"] += to_int(row["tp_count"])
        totals["fp"] += to_int(row["fp_count"])
        totals["oracle_wrong"] += to_int(row["oracle_wrong_count"])
        totals["canonical_fail"] += to_int(row["canonical_fail_count"])
    precision_denominator = totals["tp"] + totals["fp"]
    global_row: dict[str, object] = {
        "total_problems": batch_counts["total_problems"] or len(per_problem),
        "ok_problems": batch_counts["ok_problems"] or len(per_problem),
        "skipped_problems": batch_counts["skipped_problems"],
        "total_tests": totals["tests"],
        "total_found": totals["found"],
        "total_tp": totals["tp"],
        "total_fp": totals["fp"],
        "total_oracle_wrong": totals["oracle_wrong"],
        "total_canonical_fail": totals["canonical_fail"],
        "global_precision": (totals["tp"] / precision_denominator) if precision_denominator else "",
    }
    lines = [f"{key}={value}" for key, value in global_row.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_csv(csv_path, [global_row], list(global_row.keys()))
    return global_row


def main() -> None:
    parser = argparse.ArgumentParser(description="Build stable DPP baseline summary artifacts from existing results.")
    parser.add_argument("--report-root", default="outputs/tcases/cpp", help="Directory containing <pid>/summary.json and detail.csv")
    parser.add_argument("--out-dir", default="outputs/summary", help="Directory for baseline summary artifacts")
    parser.add_argument("--compiler", default="g++-15", help="Compiler used for optional canonical compile checks")
    parser.add_argument("--skip-compile-check", action="store_true", help="Do not compile canonical solutions for the anomaly report")
    args = parser.parse_args()
    ensure_csv_field_limit()

    report_root = resolve_path(args.report_root)
    out_dir = resolve_path(args.out_dir)
    if not report_root.exists():
        raise FileNotFoundError(f"Report root not found: {report_root}")

    per_problem, test_cases = summarize_baseline_results(report_root)
    batch_counts = parse_batch_counts(report_root / "batch_report.txt")

    per_problem_path = out_dir / "baseline_dpp_per_problem.csv"
    global_txt_path = out_dir / "baseline_dpp_global.txt"
    global_csv_path = out_dir / "baseline_dpp_global.csv"
    test_case_path = out_dir / "baseline_dpp_test_cases.csv"
    unclassified_path = out_dir / "baseline_dpp_unclassified_found.csv"
    canonical_path = out_dir / "baseline_dpp_canonical_anomalies.csv"
    high_fp_path = out_dir / "baseline_dpp_high_fp_analysis.csv"

    write_csv(per_problem_path, per_problem, PER_PROBLEM_FIELDS)
    global_row = write_global_summary(global_txt_path, global_csv_path, batch_counts, per_problem)
    write_csv(test_case_path, test_cases, [*TEST_CASE_FIELDS, "votes", "variant_total", "canonical_error", "saved_case"])
    write_csv(
        unclassified_path,
        find_unclassified_found_cases(test_cases),
        [
            "pid",
            "test_name",
            "status",
            "predicted_bug",
            "oracle_output",
            "canonical_output",
            "put_output",
            "final_label",
            "failure_reason",
        ],
    )
    write_csv(
        canonical_path,
        analyze_canonical_failures(
            per_problem,
            test_cases,
            report_root,
            out_dir,
            args.compiler,
            not args.skip_compile_check,
        ),
        [
            "pid",
            "canonical_fail_count",
            "compile_ok",
            "runtime_fail_count",
            "timeout_count",
            "empty_output_count",
            "compare_issue_suspected",
            "notes",
        ],
    )
    write_csv(
        high_fp_path,
        analyze_high_fp(per_problem, test_cases),
        [
            "pid",
            "fp_count",
            "tp_count",
            "oracle_wrong_count",
            "found",
            "no_majority",
            "canonical_fail_count",
            "oracle_wrong_and_found_count",
            "oracle_wrong_and_no_majority_count",
        ],
    )

    print(f"[DONE] per_problem={per_problem_path}")
    print(f"[DONE] global={global_txt_path}")
    print(f"[DONE] global_csv={global_csv_path}")
    print(f"[DONE] test_cases={test_case_path}")
    print(f"[DONE] unclassified_found={unclassified_path}")
    print(f"[DONE] canonical_anomalies={canonical_path}")
    print(f"[DONE] high_fp={high_fp_path}")
    print(f"[STATS] global_precision={global_row['global_precision']}")


if __name__ == "__main__":
    main()
