from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.path_utils import ensure_dir, resolve_repo_path, safe_rel, write_csv, write_json, write_text


SUMMARY_FIELDS = [
    "baseline",
    "runner",
    "available",
    "processed_problems",
    "successful_runs",
    "failed_runs",
    "skipped_runs",
    "total_generated_inputs",
    "valid_inputs",
    "invalid_inputs",
    "bug_revealing_inputs",
    "candidate_patches",
    "compile_successes",
    "behavior_changes",
    "apparent_fixes",
    "tests_dir_size",
    "variants_used",
    "saved",
    "found",
    "agree",
    "no_majority",
    "tp_count",
    "fp_count",
    "precision",
    "summary_json",
    "summary_csv",
]


def parse_baselines(value: str) -> list[str]:
    raw_items = [part.strip().lower() for part in value.split(",") if part.strip()]
    if not raw_items:
        return ["chat", "apr", "dpp", "tc"]

    expanded: list[str] = []
    for item in raw_items:
        if item == "all":
            expanded.extend(["chat", "apr", "dpp", "tc"])
        else:
            expanded.append(item)

    normalized: list[str] = []
    seen: set[str] = set()
    aliases = {"trickcatcher": "tc"}
    for item in expanded:
        name = aliases.get(item, item)
        if name not in {"chat", "apr", "dpp", "tc"}:
            raise argparse.ArgumentTypeError(f"Unsupported baseline: {item}")
        if name not in seen:
            seen.add(name)
            normalized.append(name)
    return normalized


def choose_python(explicit: str | None) -> str:
    if explicit:
        return str(resolve_repo_path(explicit))
    venv_python = ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified launcher for chat, apr, dpp, and tc baselines."
    )
    parser.add_argument(
        "--baselines",
        default="chat,apr,dpp,tc",
        help="Comma-separated list from: chat, apr, dpp, tc, all",
    )
    parser.add_argument("--python", default=None, help="Interpreter used for all child runners.")
    parser.add_argument("--layout", choices=["dataset", "ac"], default="dataset")
    parser.add_argument("--pid", default=None)
    parser.add_argument("--lang", choices=["py", "cpp"], default="cpp")

    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--canonical-root", default="AC")
    parser.add_argument("--ac-root", default="AC")
    parser.add_argument("--tests-root", default="outputs/inputs")
    parser.add_argument("--variants-root", default="Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp")
    parser.add_argument("--tcases-root", default="outputs/tcases")
    parser.add_argument("--outputs-root", default="outputs")

    parser.add_argument("--model", default="deepseek-chat", help="Shared default model for chat/apr/tc stages.")
    parser.add_argument("--timeout", type=float, default=2.0)

    parser.add_argument("--chat-num-candidates", type=int, default=20)
    parser.add_argument("--chat-batch-size", type=int, default=5)
    parser.add_argument("--chat-checker-timeout", type=float, default=10.0)
    parser.add_argument("--chat-skip-checker", action="store_true")

    parser.add_argument("--apr-num-candidates", type=int, default=5)

    parser.add_argument("--dpp-variant-mode", choices=["my", "trickybugs"], default="trickybugs")
    parser.add_argument("--dpp-fixed-min-votes", type=int, default=6)
    parser.add_argument("--dpp-prefilter-variants", action="store_true")

    parser.add_argument("--tc-tool-model", default=None)
    parser.add_argument("--tc-input-model", default=None)
    parser.add_argument("--tc-variant-model", default=None)
    parser.add_argument("--tc-input-backend", choices=["generator", "llm", "mixed"], default="llm")
    parser.add_argument("--tc-input-num", type=int, default=100)
    parser.add_argument("--tc-input-llm-num", type=int, default=10)
    parser.add_argument("--tc-input-random-num", type=int, default=None)
    parser.add_argument("--tc-input-seed", type=int, default=2)
    parser.add_argument("--tc-input-jobs", type=int, default=1)
    parser.add_argument("--tc-check-timeout", type=float, default=10.0)
    parser.add_argument("--tc-check-jobs", type=int, default=8)
    parser.add_argument("--tc-diff-jobs", type=int, default=50)
    parser.add_argument("--tc-variant-k", type=int, default=10)
    parser.add_argument("--tc-variant-index-start", type=int, default=0)
    parser.add_argument("--tc-prefilter-variants", action="store_true")
    parser.add_argument("--tc-prefilter-sample-size", type=int, default=20)
    parser.add_argument("--tc-prefilter-max-fail-rate", type=float, default=0.2)
    parser.add_argument("--tc-prefilter-max-mismatch-rate", type=float, default=0.3)
    parser.add_argument("--tc-prefilter-min-keep", type=int, default=3)
    parser.add_argument("--tc-run-tool-gen", action="store_true")
    parser.add_argument("--tc-run-variant-gen", action="store_true")
    parser.add_argument("--tc-run-input-check", action="store_true")
    parser.add_argument("--tc-skip-tool-gen", action="store_true")
    parser.add_argument("--tc-skip-variant-gen", action="store_true")
    parser.add_argument("--tc-skip-input-gen", action="store_true")
    parser.add_argument("--tc-skip-input-check", action="store_true")
    parser.add_argument("--tc-skip-diff-test", action="store_true")
    parser.add_argument("--tc-skip-summary", action="store_true")
    return parser


def baseline_roots(outputs_root: Path) -> dict[str, Path]:
    return {
        "chat": outputs_root / "chat",
        "apr": outputs_root / "apr",
        "dpp": outputs_root / "dpp",
        "tc": outputs_root / "trickcatcher",
    }


def run_with_log(*, python_executable: str, name: str, argv: list[str], logs_dir: Path) -> None:
    ensure_dir(logs_dir)
    log_path = logs_dir / f"{name}.log"
    cmd = [python_executable, *argv]
    header = f"$ {' '.join(shlex.quote(part) for part in cmd)}\n\n"
    print(f"[RUN] {name}")
    print(header.rstrip(), flush=True)

    with log_path.open("w", encoding="utf-8") as fh:
        fh.write(header)
        fh.flush()
        process = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            fh.write(line)
            fh.flush()
        return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(f"Baseline {name} failed. See log: {log_path}")


def build_chat_args(args: argparse.Namespace, out_root: Path) -> list[str]:
    cmd = [
        "experiments/chat/run_chat.py",
        "--layout",
        args.layout,
        "--lang",
        args.lang,
        "--dataset-root",
        args.dataset_root,
        "--canonical-root",
        args.canonical_root,
        "--ac-root",
        args.ac_root,
        "--tests-root",
        args.tests_root,
        "--out-root",
        str(out_root),
        "--model",
        args.model,
        "--num-candidates",
        str(args.chat_num_candidates),
        "--batch-size",
        str(args.chat_batch_size),
        "--timeout",
        str(args.timeout),
        "--checker-timeout",
        str(args.chat_checker_timeout),
    ]
    if args.pid:
        cmd.extend(["--pid", args.pid])
    if args.chat_skip_checker:
        cmd.append("--skip-checker")
    return cmd


def build_apr_args(args: argparse.Namespace, out_root: Path) -> list[str]:
    cmd = [
        "experiments/apr/run_apr.py",
        "--layout",
        args.layout,
        "--lang",
        args.lang,
        "--dataset-root",
        args.dataset_root,
        "--canonical-root",
        args.canonical_root,
        "--ac-root",
        args.ac_root,
        "--tests-root",
        args.tests_root,
        "--out-root",
        str(out_root),
        "--model",
        args.model,
        "--num-candidates",
        str(args.apr_num_candidates),
        "--timeout",
        str(args.timeout),
    ]
    if args.pid:
        cmd.extend(["--pid", args.pid])
    return cmd


def build_dpp_args(args: argparse.Namespace, out_root: Path) -> list[str]:
    cmd = [
        "experiments/dpp/run_dpp.py",
        "--layout",
        args.layout,
        "--lang",
        args.lang,
        "--dataset-root",
        args.dataset_root,
        "--canonical-root",
        args.canonical_root,
        "--ac-root",
        args.ac_root,
        "--tests-root",
        args.tests_root,
        "--variants-root",
        args.variants_root,
        "--out-root",
        str(out_root),
        "--variant-mode",
        args.dpp_variant_mode,
        "--timeout",
        str(args.timeout),
        "--fixed-min-votes",
        str(args.dpp_fixed_min_votes),
    ]
    if args.pid:
        cmd.extend(["--pid", args.pid])
    if args.dpp_prefilter_variants:
        cmd.append("--prefilter-variants")
    return cmd


def build_tc_args(args: argparse.Namespace, out_root: Path) -> list[str]:
    if args.layout != "dataset":
        raise ValueError("TC currently supports only --layout dataset in the unified runner.")

    cmd = [
        "experiments/trickcatcher/run_trickcatcher.py",
        "--lang",
        args.lang,
        "--dataset-root",
        args.dataset_root,
        "--canonical-root",
        args.canonical_root,
        "--variants-root",
        args.variants_root,
        "--inputs-root",
        args.tests_root,
        "--tcases-root",
        args.tcases_root,
        "--summary-root",
        str(out_root),
        "--tool-model",
        args.tc_tool_model or args.model,
        "--input-backend",
        args.tc_input_backend,
        "--input-model",
        args.tc_input_model or args.model,
        "--input-num",
        str(args.tc_input_num),
        "--input-llm-num",
        str(args.tc_input_llm_num),
        "--input-seed",
        str(args.tc_input_seed),
        "--input-jobs",
        str(args.tc_input_jobs),
        "--check-timeout",
        str(args.tc_check_timeout),
        "--check-jobs",
        str(args.tc_check_jobs),
        "--timeout",
        str(args.timeout),
        "--variant-k",
        str(args.tc_variant_k),
        "--variant-model",
        args.tc_variant_model or args.model,
        "--variant-index-start",
        str(args.tc_variant_index_start),
        "--variant-mode",
        args.dpp_variant_mode,
        "--fixed-min-votes",
        str(args.dpp_fixed_min_votes),
        "--diff-jobs",
        str(args.tc_diff_jobs),
    ]
    if args.pid:
        cmd.extend(["--pid", args.pid])
    if args.tc_input_random_num is not None:
        cmd.extend(["--input-random-num", str(args.tc_input_random_num)])
    if args.tc_prefilter_variants:
        cmd.extend(
            [
                "--prefilter-variants",
                "--prefilter-sample-size",
                str(args.tc_prefilter_sample_size),
                "--prefilter-max-fail-rate",
                str(args.tc_prefilter_max_fail_rate),
                "--prefilter-max-mismatch-rate",
                str(args.tc_prefilter_max_mismatch_rate),
                "--prefilter-min-keep",
                str(args.tc_prefilter_min_keep),
            ]
        )
    if args.tc_run_tool_gen:
        cmd.append("--run-tool-gen")
    if args.tc_run_variant_gen:
        cmd.append("--run-variant-gen")
    if args.tc_run_input_check:
        cmd.append("--run-input-check")
    if args.tc_skip_tool_gen:
        cmd.append("--skip-tool-gen")
    if args.tc_skip_variant_gen:
        cmd.append("--skip-variant-gen")
    if args.tc_skip_input_gen:
        cmd.append("--skip-input-gen")
    if args.tc_skip_input_check:
        cmd.append("--skip-input-check")
    if args.tc_skip_diff_test:
        cmd.append("--skip-diff-test")
    if args.tc_skip_summary:
        cmd.append("--skip-summary")
    return cmd


def load_optional_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def collect_summary_rows(outputs_root: Path, baselines: list[str]) -> list[dict[str, object]]:
    roots = baseline_roots(outputs_root)
    rows: list[dict[str, object]] = []
    runner_names = {"chat": "chat", "apr": "apr", "dpp": "dpp", "tc": "trickcatcher"}
    for baseline in baselines:
        baseline_root = roots[baseline]
        summary_json_path = baseline_root / "summary.json"
        summary_csv_path = baseline_root / "summary.csv"
        payload = load_optional_json(summary_json_path)
        row: dict[str, object] = {
            "baseline": baseline,
            "runner": runner_names[baseline],
            "available": payload is not None,
            "processed_problems": "",
            "successful_runs": "",
            "failed_runs": "",
            "skipped_runs": "",
            "total_generated_inputs": "",
            "valid_inputs": "",
            "invalid_inputs": "",
            "bug_revealing_inputs": "",
            "candidate_patches": "",
            "compile_successes": "",
            "behavior_changes": "",
            "apparent_fixes": "",
            "tests_dir_size": "",
            "variants_used": "",
            "saved": "",
            "found": "",
            "agree": "",
            "no_majority": "",
            "tp_count": "",
            "fp_count": "",
            "precision": "",
            "summary_json": safe_rel(summary_json_path) if summary_json_path.exists() else "",
            "summary_csv": safe_rel(summary_csv_path) if summary_csv_path.exists() else "",
        }
        if payload:
            for key in (
                "processed_problems",
                "successful_runs",
                "failed_runs",
                "skipped_runs",
                "total_generated_inputs",
                "valid_inputs",
                "invalid_inputs",
                "bug_revealing_inputs",
                "candidate_patches",
                "compile_successes",
                "behavior_changes",
                "apparent_fixes",
                "tests_dir_size",
                "variants_used",
                "saved",
                "found",
                "agree",
                "no_majority",
                "tp_count",
                "fp_count",
                "precision",
            ):
                row[key] = payload.get(key, "")
        rows.append(row)
    return rows


def write_launcher_summary(outputs_root: Path, baselines: list[str]) -> Path:
    rows = collect_summary_rows(outputs_root, baselines)
    launcher_root = ensure_dir(outputs_root / "baseline_runs")
    csv_path = launcher_root / "summary.csv"
    json_path = launcher_root / "summary.json"
    txt_path = launcher_root / "summary.txt"

    write_csv(csv_path, rows, SUMMARY_FIELDS)
    payload = {
        "baselines": baselines,
        "rows": rows,
    }
    write_json(json_path, payload)

    lines = ["Unified Baseline Summary"]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    f"baseline={row['baseline']}",
                    f"runner={row['runner']}",
                    f"available={row['available']}",
                    f"processed={row['processed_problems']}",
                    f"ok={row['successful_runs']}",
                    f"failed={row['failed_runs']}",
                    f"skipped={row['skipped_runs']}",
                ]
            )
        )
    write_text(txt_path, "\n".join(lines) + "\n")
    return csv_path


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    baselines = parse_baselines(args.baselines)
    python_executable = choose_python(args.python)
    outputs_root = resolve_repo_path(args.outputs_root)
    logs_dir = ensure_dir(outputs_root / "baseline_runs" / "logs")
    roots = baseline_roots(outputs_root)

    commands = {
        "chat": build_chat_args(args, roots["chat"]),
        "apr": build_apr_args(args, roots["apr"]),
        "dpp": build_dpp_args(args, roots["dpp"]),
        "tc": build_tc_args(args, roots["tc"]) if "tc" in baselines else None,
    }

    for baseline in baselines:
        argv = commands[baseline]
        assert argv is not None
        run_with_log(
            python_executable=python_executable,
            name=baseline,
            argv=argv,
            logs_dir=logs_dir,
        )

    summary_path = write_launcher_summary(outputs_root, baselines)
    print(f"[DONE] launcher summary: {summary_path}")


if __name__ == "__main__":
    main()
