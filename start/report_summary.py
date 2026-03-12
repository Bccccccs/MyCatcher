import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Dict, List, Union


PROJECT_ROOT = Path(__file__).resolve().parent.parent


SUMMARY_KEYS = [
    "saved",
    "agree",
    "found",
    "no_majority",
    "no_variant_output",
    "put_fail",
]

TABLE_HEADERS = [
    "pid",
    "status",
    "category",
    "saved",
    "agree",
    "found",
    "no_majority",
    "no_variant_output",
    "put_fail",
    "tests",
]


def empty_row(pid: str, report_path: Path) -> Dict[str, Union[int, str]]:
    row: Dict[str, Union[int, str]] = {
        "pid": pid,
        "report": str(report_path),
        "status": "missing_report",
        "category": "missing_report",
    }
    for key in SUMMARY_KEYS:
        row[key] = 0
    row["tests"] = 0
    return row


def classify_row(row: Dict[str, Union[int, str]]) -> str:
    if row["status"] != "ok":
        return str(row["status"])

    saved = int(row["saved"])
    agree = int(row["agree"])
    found = int(row["found"])
    no_majority = int(row["no_majority"])
    no_variant_output = int(row["no_variant_output"])
    put_fail = int(row["put_fail"])

    active = {
        "saved_cases": saved > 0,
        "agree_only": agree > 0,
        "found_votes": found > 0,
        "no_majority": no_majority > 0,
        "no_variant_output": no_variant_output > 0,
        "put_fail": put_fail > 0,
    }
    active_names = [name for name, enabled in active.items() if enabled]

    if saved > 0 and len(active_names) == 1:
        return "saved_only"
    if agree > 0 and len(active_names) == 1:
        return "agree_only"
    if no_majority > 0 and len(active_names) == 1:
        return "no_majority_only"
    if no_variant_output > 0 and len(active_names) == 1:
        return "no_variant_output_only"
    if put_fail > 0 and len(active_names) == 1:
        return "put_fail_only"
    if saved == 0 and found == 0 and agree > 0 and no_majority > 0 and no_variant_output == 0 and put_fail == 0:
        return "agree_and_no_majority"
    if saved > 0 and no_majority == 0 and no_variant_output == 0 and put_fail == 0:
        return "saved_and_agree" if agree > 0 else "saved_only"
    if saved == 0 and found == 0 and agree == 0 and no_majority == 0 and no_variant_output == 0 and put_fail == 0:
        return "empty_report"
    return "mixed"


def parse_report(report_path: Path) -> Dict[str, Union[int, str]]:
    row = empty_row(report_path.parent.name, report_path)
    row["status"] = "ok"

    lines = report_path.read_text(encoding="utf-8").splitlines()
    try:
        summary_index = lines.index("Summary")
    except ValueError as exc:
        raise ValueError(f"Missing 'Summary' section: {report_path}") from exc

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
            row[key] = int(value)

    missing = [key for key in SUMMARY_KEYS if key not in row]
    if missing:
        raise ValueError(f"Missing summary keys in {report_path}: {', '.join(missing)}")

    row["tests"] = sum(int(row[key]) for key in SUMMARY_KEYS[1:])
    row["category"] = classify_row(row)
    return row


def collect_rows(root: Path) -> List[Dict[str, Union[int, str]]]:
    problem_dirs = sorted([path for path in root.iterdir() if path.is_dir()])
    if not problem_dirs:
        raise FileNotFoundError(f"No problem directories found under {root}")

    rows: List[Dict[str, Union[int, str]]] = []
    for problem_dir in problem_dirs:
        report_path = problem_dir / "report.txt"
        if report_path.exists():
            rows.append(parse_report(report_path))
        else:
            rows.append(empty_row(problem_dir.name, report_path))
    return rows


def print_table(rows: List[Dict[str, Union[int, str]]]) -> None:
    widths = {
        header: max(len(header), *(len(str(row[header])) for row in rows))
        for header in TABLE_HEADERS
    }

    def render(row: Dict[str, Union[int, str]]) -> str:
        cells = []
        for header in TABLE_HEADERS:
            value = str(row[header])
            if header in {"pid", "status", "category"}:
                cells.append(value.ljust(widths[header]))
            else:
                cells.append(value.rjust(widths[header]))
        return "  ".join(cells)

    print(render({header: header for header in TABLE_HEADERS}))
    print("  ".join("-" * widths[header] for header in TABLE_HEADERS))
    for row in rows:
        print(render(row))


def print_totals(rows: List[Dict[str, Union[int, str]]]) -> None:
    counter = Counter(str(row["category"]) for row in rows)
    status_counter = Counter(str(row["status"]) for row in rows)
    totals = {key: sum(int(row[key]) for row in rows) for key in SUMMARY_KEYS + ["tests"]}

    print()
    print("Status Summary")
    for status in sorted(status_counter):
        print(f"{status}={status_counter[status]}")

    print()
    print("Category Summary")
    for category in sorted(counter):
        print(f"{category}={counter[category]}")

    print()
    print("Metric Totals")
    print(f"problems={len(rows)}")
    for key in ["saved", "agree", "found", "no_majority", "no_variant_output", "put_fail", "tests"]:
        print(f"{key}={totals[key]}")


def write_detail_csv(rows: List[Dict[str, Union[int, str]]], output_path: Path) -> None:
    fieldnames = TABLE_HEADERS + ["report"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_category_csv(rows: List[Dict[str, Union[int, str]]], output_path: Path) -> None:
    fieldnames = ["category", "problems", "saved", "agree", "found", "no_majority", "no_variant_output", "put_fail", "tests"]
    grouped: Dict[str, Dict[str, int]] = {}

    for row in rows:
        category = str(row["category"])
        if category not in grouped:
            grouped[category] = {key: 0 for key in fieldnames if key != "category"}
        grouped[category]["problems"] += 1
        for key in ["saved", "agree", "found", "no_majority", "no_variant_output", "put_fail", "tests"]:
            grouped[category][key] += int(row[key])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for category in sorted(grouped):
            data = {"category": category}
            data.update(grouped[category])
            writer.writerow(data)


def resolve_output_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize differential testing reports and export categorized CSV tables.")
    parser.add_argument("--root", default="outputs/tcases/cpp", help="Directory containing per-problem result folders.")
    parser.add_argument("--csv", default=None, help="Optional detailed CSV output path.")
    parser.add_argument("--category-csv", default=None, help="Optional categorized summary CSV output path.")
    parser.add_argument("--sort-by", choices=["pid", "status", "category", "saved", "found", "put_fail"], default="pid")
    parser.add_argument("--descending", action="store_true", help="Sort in descending order.")
    args = parser.parse_args()

    root = resolve_output_path(args.root)
    rows = collect_rows(root)
    rows.sort(key=lambda row: str(row[args.sort_by]) if args.sort_by in {"pid", "status", "category"} else int(row[args.sort_by]), reverse=args.descending)

    print_table(rows)
    print_totals(rows)

    if args.csv:
        detail_path = resolve_output_path(args.csv)
        write_detail_csv(rows, detail_path)
        print()
        print(f"detail_csv={detail_path}")

    if args.category_csv:
        category_path = resolve_output_path(args.category_csv)
        write_category_csv(rows, category_path)
        print(f"category_csv={category_path}")


if __name__ == "__main__":
    main()
