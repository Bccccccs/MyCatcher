from __future__ import annotations

import json
from pathlib import Path

from common.path_utils import safe_rel
from common.report_utils import write_summary_table


SUMMARY_FIELDS = [
    "pid",
    "status",
    "tests_dir_size",
    "variants_dir_size",
    "variants_used",
    "saved",
    "found",
    "agree",
    "no_majority",
    "tp_count",
    "fp_count",
    "precision",
    "oracle_wrong_count",
    "canonical_fail_count",
    "summary_json",
    "report_txt",
    "detail_csv",
]


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_problem_rows(report_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not report_root.exists():
        return rows

    for problem_dir in sorted(path for path in report_root.iterdir() if path.is_dir()):
        summary_path = problem_dir / "summary.json"
        report_path = problem_dir / "report.txt"
        detail_path = problem_dir / "detail.csv"
        if not summary_path.exists():
            rows.append(
                {
                    "pid": problem_dir.name,
                    "status": "missing_summary",
                    "tests_dir_size": 0,
                    "variants_dir_size": 0,
                    "variants_used": 0,
                    "saved": 0,
                    "found": 0,
                    "agree": 0,
                    "no_majority": 0,
                    "tp_count": 0,
                    "fp_count": 0,
                    "precision": "",
                    "oracle_wrong_count": 0,
                    "canonical_fail_count": 0,
                    "summary_json": "",
                    "report_txt": safe_rel(report_path) if report_path.exists() else "",
                    "detail_csv": safe_rel(detail_path) if detail_path.exists() else "",
                }
            )
            continue

        summary = _load_json(summary_path)
        rows.append(
            {
                "pid": problem_dir.name,
                "status": "ok",
                "tests_dir_size": summary.get("tests_dir_size", 0),
                "variants_dir_size": summary.get("variants_dir_size", 0),
                "variants_used": summary.get("variants_used", 0),
                "saved": summary.get("saved", 0),
                "found": summary.get("found", 0),
                "agree": summary.get("agree", 0),
                "no_majority": summary.get("no_majority", 0),
                "tp_count": summary.get("tp_count", 0),
                "fp_count": summary.get("fp_count", 0),
                "precision": summary.get("precision", ""),
                "oracle_wrong_count": summary.get("oracle_wrong_count", 0),
                "canonical_fail_count": summary.get("canonical_fail_count", 0),
                "summary_json": safe_rel(summary_path),
                "report_txt": safe_rel(report_path) if report_path.exists() else "",
                "detail_csv": safe_rel(detail_path) if detail_path.exists() else "",
            }
        )
    return rows


def _aggregate(rows: list[dict[str, object]], report_root: Path) -> dict[str, object]:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    tp_total = sum(int(row.get("tp_count", 0) or 0) for row in ok_rows)
    fp_total = sum(int(row.get("fp_count", 0) or 0) for row in ok_rows)
    precision = tp_total / (tp_total + fp_total) if (tp_total + fp_total) else None
    return {
        "experiment": "trickcatcher",
        "role": "canonical_paper_reproduction",
        "paper_alignment": "variant_generation + spec_based_input_generation + input_checking + differential_testing",
        "report_root": safe_rel(report_root),
        "processed_problems": len(rows),
        "successful_runs": len(ok_rows),
        "failed_runs": sum(1 for row in rows if row.get("status") not in {"ok", "skipped"}),
        "skipped_runs": sum(1 for row in rows if row.get("status") == "skipped"),
        "tests_dir_size": sum(int(row.get("tests_dir_size", 0) or 0) for row in ok_rows),
        "variants_used": sum(int(row.get("variants_used", 0) or 0) for row in ok_rows),
        "saved": sum(int(row.get("saved", 0) or 0) for row in ok_rows),
        "found": sum(int(row.get("found", 0) or 0) for row in ok_rows),
        "agree": sum(int(row.get("agree", 0) or 0) for row in ok_rows),
        "no_majority": sum(int(row.get("no_majority", 0) or 0) for row in ok_rows),
        "tp_count": tp_total,
        "fp_count": fp_total,
        "oracle_wrong_count": sum(int(row.get("oracle_wrong_count", 0) or 0) for row in ok_rows),
        "canonical_fail_count": sum(int(row.get("canonical_fail_count", 0) or 0) for row in ok_rows),
        "precision": precision,
    }


def write_canonical_summary(report_root: Path, out_dir: Path) -> dict[str, object]:
    rows = collect_problem_rows(report_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_summary_table(out_dir / "per_problem_summary.csv", rows, SUMMARY_FIELDS)

    summary = _aggregate(rows, report_root)
    write_summary_table(out_dir / "summary.csv", [summary], list(summary.keys()))
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    lines = [
        "TrickCatcher Summary",
        f"role={summary['role']}",
        f"paper_alignment={summary['paper_alignment']}",
        f"report_root={summary['report_root']}",
        f"processed_problems={summary['processed_problems']}",
        f"successful_runs={summary['successful_runs']}",
        f"failed_runs={summary['failed_runs']}",
        f"skipped_runs={summary['skipped_runs']}",
        f"tests_dir_size={summary['tests_dir_size']}",
        f"variants_used={summary['variants_used']}",
        f"saved={summary['saved']}",
        f"found={summary['found']}",
        f"agree={summary['agree']}",
        f"no_majority={summary['no_majority']}",
        f"tp_count={summary['tp_count']}",
        f"fp_count={summary['fp_count']}",
        f"oracle_wrong_count={summary['oracle_wrong_count']}",
        f"canonical_fail_count={summary['canonical_fail_count']}",
        f"precision={'' if summary['precision'] is None else summary['precision']}",
    ]
    (out_dir / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def _load_optional_summary(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return _load_json(path)


def write_comparison_scaffold(outputs_root: Path, out_path: Path) -> Path:
    entries = [
        ("trickcatcher", "canonical_paper_reproduction", outputs_root / "trickcatcher" / "summary.json"),
        ("chat", "direct_generation_baseline", outputs_root / "chat" / "summary.json"),
        ("apr", "repair_baseline", outputs_root / "apr" / "summary.json"),
        ("dpp", "legacy_differential_testing_only", outputs_root / "dpp" / "summary.json"),
    ]
    rows: list[dict[str, object]] = []
    for name, role, summary_path in entries:
        payload = _load_optional_summary(summary_path)
        rows.append(
            {
                "experiment": name,
                "role": role,
                "available": payload is not None,
                "processed_problems": "" if payload is None else payload.get("processed_problems", ""),
                "successful_runs": "" if payload is None else payload.get("successful_runs", ""),
                "summary_json": safe_rel(summary_path) if summary_path.exists() else "",
            }
        )
    write_summary_table(
        out_path,
        rows,
        ["experiment", "role", "available", "processed_problems", "successful_runs", "summary_json"],
    )
    return out_path
