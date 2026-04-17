import argparse
import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

VOTE_STATUS_RE = re.compile(r"^\[VOTE\]\s+\S+\s+status=(?P<status>\S+)\b")
FINAL_LABEL_RE = re.compile(r"\bfinal_label=(?P<final_label>\S+)\b")
SUMMARY_VALUE_RE = re.compile(r"^(?P<key>[a-z_]+)=(?P<value>-?\d+(?:\.\d+)?)$")

SUMMARY_KEY_TO_STATUS = {
    "agree": "AGREE",
    "found": "FOUND",
    "no_majority": "NO_MAJORITY",
    "no_variant_output": "NO_VARIANT_OUTPUT",
    "put_fail": "PUT_FAIL",
}

DEFAULT_STATUS_ORDER = [
    "AGREE",
    "FOUND",
    "NO_MAJORITY",
    "NO_VARIANT_OUTPUT",
    "PUT_FAIL",
]

SUMMARY_METRIC_ORDER = [
    "saved",
    "tp_count",
    "fp_count",
    "oracle_wrong_count",
    "canonical_fail_count",
    "precision",
]

DEFAULT_FINAL_LABEL_ORDER = [
    "TP",
    "FP",
    "NOT_FOUND",
    "CANONICAL_FAIL",
    "INVALID_INPUT",
    "NO_ORACLE",
    "PUT_FAIL",
]


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (ROOT / path).resolve()


def find_report_dirs(report_root: Path) -> list[Path]:
    return sorted(
        path for path in report_root.iterdir()
        if path.is_dir() and (path / "report.txt").exists()
    )


def parse_report(report_path: Path) -> tuple[Counter, Counter, dict[str, object], int]:
    status_counts: Counter = Counter()
    final_label_counts: Counter = Counter()
    summary_counts: Counter = Counter()
    summary_metrics: dict[str, object] = {}
    tests = 0

    for raw_line in report_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        vote_match = VOTE_STATUS_RE.match(line)
        if vote_match:
            status = vote_match.group("status")
            status_counts[status] += 1
            final_label_match = FINAL_LABEL_RE.search(line)
            if final_label_match:
                final_label_counts[final_label_match.group("final_label")] += 1
            tests += 1
            continue

        summary_match = SUMMARY_VALUE_RE.match(line)
        if not summary_match:
            continue
        key = summary_match.group("key")
        raw_value = summary_match.group("value")
        value: object = float(raw_value) if "." in raw_value else int(raw_value)
        if key == "saved":
            summary_metrics["saved"] = value
            continue
        mapped_status = SUMMARY_KEY_TO_STATUS.get(key)
        if mapped_status:
            summary_counts[mapped_status] = int(value)
            continue
        summary_metrics[key] = value

    if status_counts:
        if "saved" not in summary_metrics:
            summary_metrics["saved"] = status_counts.get("FOUND", 0)
        return status_counts, final_label_counts, summary_metrics, tests

    fallback_tests = sum(summary_counts[status] for status in SUMMARY_KEY_TO_STATUS.values())
    if "saved" not in summary_metrics:
        summary_metrics["saved"] = summary_counts.get("FOUND", 0)
    return summary_counts, final_label_counts, summary_metrics, fallback_tests


def ordered_columns(
    rows: list[dict[str, object]],
    skip_keys: set[str],
    preferred_order: list[str],
    prefix: str | None = None,
) -> list[str]:
    seen = set()
    for row in rows:
        for key, value in row.items():
            if key in skip_keys:
                continue
            if isinstance(value, (int, float)):
                if prefix is not None and not key.startswith(prefix):
                    continue
                if prefix is None and key.startswith("status_"):
                    continue
                if prefix is None and key.startswith("label_"):
                    continue
                seen.add(key)

    extra = sorted(seen - set(preferred_order))
    return [key for key in preferred_order if key in seen] + extra


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Count per-report statuses from differential-testing report.txt files and save them as CSV."
    )
    ap.add_argument("--report-root", default="outputs/tcases/cpp", help="Directory containing <pid>/report.txt")
    ap.add_argument(
        "--out",
        default="outputs/tcases/cpp/report_status_summary.csv",
        help="CSV file to write",
    )
    args = ap.parse_args()

    report_root = resolve_path(args.report_root)
    out_path = resolve_path(args.out)

    if not report_root.exists():
        raise FileNotFoundError(f"Report root not found: {report_root}")

    rows: list[dict[str, object]] = []
    totals: Counter = Counter()

    for report_dir in find_report_dirs(report_root):
        pid = report_dir.name
        report_path = report_dir / "report.txt"
        status_counts, final_label_counts, summary_metrics, tests = parse_report(report_path)

        row: dict[str, object] = {
            "pid": pid,
            "tests": tests,
            "saved": summary_metrics.get("saved", status_counts.get("FOUND", 0)),
            "report": str(report_path),
        }
        for status, count in sorted(status_counts.items()):
            key = f"status_{status}"
            row[key] = count
            totals[key] += count
        for final_label, count in sorted(final_label_counts.items()):
            key = f"label_{final_label}"
            row[key] = count
            totals[key] += count
        for metric_name, value in summary_metrics.items():
            row[metric_name] = value
            if isinstance(value, int):
                totals[metric_name] += value
        totals["tests"] += tests
        rows.append(row)

    status_columns = ordered_columns(
        rows,
        skip_keys={"pid", "tests", "saved", "report"},
        preferred_order=[f"status_{name}" for name in DEFAULT_STATUS_ORDER],
        prefix="status_",
    )
    final_label_columns = ordered_columns(
        rows,
        skip_keys={"pid", "tests", "saved", "report", *status_columns},
        preferred_order=[f"label_{name}" for name in DEFAULT_FINAL_LABEL_ORDER],
        prefix="label_",
    )
    metric_columns = ordered_columns(
        rows,
        skip_keys={"pid", "tests", "saved", "report", *status_columns, *final_label_columns},
        preferred_order=SUMMARY_METRIC_ORDER,
    )
    fieldnames = ["pid", "tests", "saved", *status_columns, *final_label_columns, *metric_columns, "report"]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            normalized = {name: row.get(name, 0) for name in fieldnames}
            normalized["pid"] = row["pid"]
            normalized["tests"] = row["tests"]
            normalized["saved"] = row["saved"]
            normalized["report"] = row["report"]
            writer.writerow(normalized)

        total_row = {name: 0 for name in fieldnames}
        total_row["pid"] = "TOTAL"
        total_row["tests"] = totals["tests"]
        total_row["saved"] = totals.get("saved", 0)
        total_row["report"] = ""
        for column in [*status_columns, *final_label_columns, *metric_columns]:
            if column == "precision":
                tp = totals.get("tp_count", 0)
                fp = totals.get("fp_count", 0)
                total_row[column] = (tp / (tp + fp)) if tp + fp > 0 else ""
                continue
            total_row[column] = totals.get(column, 0)
        writer.writerow(total_row)

    print(f"[DONE] wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
