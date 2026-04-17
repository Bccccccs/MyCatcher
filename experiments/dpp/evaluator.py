from __future__ import annotations

import json
from pathlib import Path

from common.path_utils import safe_rel
from common.report_utils import write_summary_table


SUMMARY_FIELDS = [
    "pid",
    "status",
    "tests_dir_size",
    "variants_used",
    "saved",
    "found",
    "agree",
    "no_majority",
    "tp_count",
    "fp_count",
    "precision",
    "report_json",
]


def build_summary_rows(report_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for problem_dir in sorted(path for path in report_root.iterdir() if path.is_dir()):
        summary_path = problem_dir / "summary.json"
        if not summary_path.exists():
            rows.append(
                {
                    "pid": problem_dir.name,
                    "status": "missing_summary",
                    "tests_dir_size": 0,
                    "variants_used": 0,
                    "saved": 0,
                    "found": 0,
                    "agree": 0,
                    "no_majority": 0,
                    "tp_count": 0,
                    "fp_count": 0,
                    "precision": "",
                    "report_json": "",
                }
            )
            continue
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        rows.append(
            {
                "pid": problem_dir.name,
                "status": "ok",
                "tests_dir_size": summary.get("tests_dir_size", 0),
                "variants_used": summary.get("variants_used", 0),
                "saved": summary.get("saved", 0),
                "found": summary.get("found", 0),
                "agree": summary.get("agree", 0),
                "no_majority": summary.get("no_majority", 0),
                "tp_count": summary.get("tp_count", 0),
                "fp_count": summary.get("fp_count", 0),
                "precision": summary.get("precision", ""),
                "report_json": safe_rel(summary_path),
            }
        )
    return rows


def write_dpp_summary(report_root: Path) -> Path:
    rows = build_summary_rows(report_root)
    out_path = report_root / "summary.csv"
    write_summary_table(out_path, rows, SUMMARY_FIELDS)
    return out_path
