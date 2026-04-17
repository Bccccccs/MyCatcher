from __future__ import annotations

import csv
from pathlib import Path

from common.path_utils import write_csv, write_json, write_text


def write_report_bundle(
    *,
    out_dir: Path,
    report_json: dict[str, object],
    report_lines: list[str],
) -> None:
    write_json(out_dir / "report.json", report_json)
    write_text(out_dir / "report.txt", "\n".join(report_lines).rstrip() + "\n")


def write_summary_table(out_path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    write_csv(out_path, rows, fieldnames)


def write_baseline_overview(
    *,
    out_dir: Path,
    baseline: str,
    summary_rows: list[dict[str, object]],
    metric_keys: list[str],
) -> None:
    processed = len(summary_rows)
    succeeded = sum(1 for row in summary_rows if row.get("status") == "ok")
    failed = sum(1 for row in summary_rows if row.get("status") not in {"ok", "skipped"})
    skipped = sum(1 for row in summary_rows if row.get("status") == "skipped")
    payload: dict[str, object] = {
        "baseline": baseline,
        "processed_problems": processed,
        "successful_runs": succeeded,
        "failed_runs": failed,
        "skipped_runs": skipped,
    }
    for key in metric_keys:
        payload[key] = sum(int(row.get(key, 0) or 0) for row in summary_rows)

    write_json(out_dir / "summary.json", payload)
    lines = [
        f"{baseline.upper()} Summary",
        f"processed_problems={processed}",
        f"successful_runs={succeeded}",
        f"failed_runs={failed}",
        f"skipped_runs={skipped}",
    ]
    for key in metric_keys:
        lines.append(f"{key}={payload[key]}")
    write_text(out_dir / "summary.txt", "\n".join(lines) + "\n")


def write_experiment_comparison(outputs_root: Path) -> Path:
    rows: list[dict[str, object]] = []
    for baseline in ("trickcatcher", "chat", "dpp", "apr"):
        summary_path = outputs_root / baseline / "summary.csv"
        if not summary_path.exists():
            continue
        processed = 0
        ok = 0
        skipped = 0
        failed = 0
        with summary_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                processed += 1
                status = row.get("status", "")
                if status == "ok":
                    ok += 1
                elif status == "skipped":
                    skipped += 1
                else:
                    failed += 1
        rows.append(
            {
                "baseline": baseline,
                "processed_problems": processed,
                "successful_runs": ok,
                "failed_runs": failed,
                "skipped_runs": skipped,
                "summary_csv": str(summary_path),
            }
        )
    out_path = outputs_root / "experiment_comparison.csv"
    write_summary_table(
        out_path,
        rows,
        ["baseline", "processed_problems", "successful_runs", "failed_runs", "skipped_runs", "summary_csv"],
    )
    return out_path
