from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.trickcatcher.reporting import write_canonical_summary, write_comparison_scaffold


def resolve_repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (ROOT / path).resolve()


def choose_python(explicit: str | None) -> str:
    if explicit:
        return str(resolve_repo_path(explicit))
    venv_python = ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def iter_problem_dirs(dataset_root: Path, pid: str | None) -> list[Path]:
    if pid:
        return [dataset_root / pid]
    return sorted(path for path in dataset_root.iterdir() if path.is_dir())


def has_missing_checker(dataset_root: Path, pid: str | None, checker_name: str = "check_input.py") -> bool:
    for problem_dir in iter_problem_dirs(dataset_root, pid):
        spec_path = problem_dir / "spec.txt"
        checker_path = problem_dir / checker_name
        if spec_path.exists() and not checker_path.exists():
            return True
    return False


def run_stage(*, python_executable: str, stage_name: str, argv: list[str], logs_dir: Path) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{stage_name}.log"
    cmd = [python_executable, *argv]
    header = f"$ {' '.join(shlex.quote(part) for part in cmd)}\n\n"
    print(f"[STAGE] {stage_name}")
    print(header.rstrip(), flush=True)

    with log_path.open("w", encoding="utf-8") as log_fh:
        log_fh.write(header)
        log_fh.flush()
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
            log_fh.write(line)
            log_fh.flush()
        returncode = process.wait()

    if returncode != 0:
        raise RuntimeError(f"Stage {stage_name} failed. See {log_path}")
    return log_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Canonical TrickCatcher-style reproduction pipeline wrapper."
    )
    parser.add_argument("--python", default=None, help="Interpreter for all wrapped stage scripts. Defaults to .venv/bin/python if available.")
    parser.add_argument("--pid", default=None)
    parser.add_argument("--lang", choices=["py", "cpp"], default="cpp")
    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--canonical-root", default="AC")
    parser.add_argument("--variants-root", default="Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp")
    parser.add_argument("--inputs-root", default="outputs/inputs")
    parser.add_argument("--tcases-root", default="outputs/tcases")
    parser.add_argument("--summary-root", default="outputs/trickcatcher")

    parser.add_argument("--tool-model", default="deepseek-chat")
    parser.add_argument("--generator-template", default="geninput_generator")
    parser.add_argument("--checker-template", default="geninput_inspector")
    parser.add_argument(
        "--run-tool-gen",
        action="store_true",
        help="Generate input_gen.py and check_input.py instead of reusing existing tools.",
    )

    parser.add_argument("--variant-k", type=int, default=10)
    parser.add_argument("--variant-model", default="deepseek-chat")
    parser.add_argument("--variant-template", default=None)
    parser.add_argument("--variant-mode", choices=["my", "trickybugs"], default="trickybugs")
    parser.add_argument("--variant-index-start", type=int, default=0)
    parser.add_argument(
        "--run-variant-gen",
        action="store_true",
        help="Regenerate variants instead of reusing the existing variants dataset.",
    )

    parser.add_argument("--input-backend", choices=["generator", "llm", "mixed"], default="llm")
    parser.add_argument("--input-model", default="deepseek-chat")
    parser.add_argument("--input-template", default="PromptTemplates/geninput_direct")
    parser.add_argument("--input-num", type=int, default=100)
    parser.add_argument("--input-random-num", type=int, default=None)
    parser.add_argument("--input-llm-num", type=int, default=10)
    parser.add_argument("--input-seed", type=int, default=2)
    parser.add_argument("--input-jobs", type=int, default=1)

    parser.add_argument("--check-timeout", type=float, default=10.0)
    parser.add_argument("--check-jobs", type=int, default=8)
    parser.add_argument(
        "--run-input-check",
        action="store_true",
        help="Run input validity checking instead of reusing existing imported/generated inputs as-is.",
    )

    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--fixed-min-votes", type=int, default=6)
    parser.add_argument("--prefilter-variants", action="store_true")
    parser.add_argument("--prefilter-sample-size", type=int, default=20)
    parser.add_argument("--prefilter-max-fail-rate", type=float, default=0.2)
    parser.add_argument("--prefilter-max-mismatch-rate", type=float, default=0.3)
    parser.add_argument("--prefilter-min-keep", type=int, default=3)
    parser.add_argument("--diff-jobs", type=int, default=50)

    parser.add_argument("--skip-tool-gen", action="store_true")
    parser.add_argument("--skip-variant-gen", action="store_true")
    parser.add_argument("--skip-input-gen", action="store_true")
    parser.add_argument("--skip-input-check", action="store_true")
    parser.add_argument("--skip-diff-test", action="store_true")
    parser.add_argument("--skip-summary", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    python_executable = choose_python(args.python)
    dataset_root = resolve_repo_path(args.dataset_root)
    inputs_root = resolve_repo_path(args.inputs_root)
    tcases_root = resolve_repo_path(args.tcases_root)
    summary_root = resolve_repo_path(args.summary_root)
    logs_dir = summary_root / "stage_logs"

    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    should_run_tool_gen = args.run_tool_gen and not args.skip_tool_gen
    should_ensure_checker = (not args.run_tool_gen) and (not args.skip_tool_gen) and has_missing_checker(dataset_root, args.pid)

    if should_run_tool_gen or should_ensure_checker:
        tool_cmd = [
            "start/run_gen_tools.py",
            "--tool",
            "both" if should_run_tool_gen else "checker",
            "--dataset-root",
            str(dataset_root),
            "--generator-template",
            args.generator_template,
            "--checker-template",
            args.checker_template,
            "--model",
            args.tool_model,
        ]
        if args.pid:
            tool_cmd.extend(["--pid", args.pid])
        run_stage(
            python_executable=python_executable,
            stage_name="01_tool_generation" if should_run_tool_gen else "01_checker_generation",
            argv=tool_cmd,
            logs_dir=logs_dir,
        )

    should_run_variant_gen = args.run_variant_gen and not args.skip_variant_gen

    if should_run_variant_gen:
        variant_cmd = [
            "start/run_varProgs_gen.py",
            "--layout",
            "dataset",
            "--dataset-root",
            str(dataset_root),
            "--out-root",
            str(resolve_repo_path(args.variants_root)),
            "--lang",
            args.lang,
            "--mode",
            "dpp",
        ]
        variant_cmd.extend(
            [
                "--template",
                args.variant_template,
            ]
            if args.variant_template
            else []
        )
        variant_cmd.extend(
            [
                "--k",
                str(args.variant_k),
                "--index-start",
                str(args.variant_index_start),
                "--model",
                args.variant_model,
            ]
        )
        if args.pid:
            variant_cmd.extend(["--pid", args.pid])
        run_stage(python_executable=python_executable, stage_name="02_variant_generation", argv=variant_cmd, logs_dir=logs_dir)

    if not args.skip_input_gen:
        input_cmd = [
            "start/run_input_gen.py",
            "--backend",
            args.input_backend,
            "--dataset-root",
            str(dataset_root),
            "--out-root",
            str(inputs_root),
            "--template",
            args.input_template,
            "--model",
            args.input_model,
            "--num",
            str(args.input_num),
            "--llm-num",
            str(args.input_llm_num),
            "--seed",
            str(args.input_seed),
            "--jobs",
            str(args.input_jobs),
        ]
        if args.input_random_num is not None:
            input_cmd.extend(["--random-num", str(args.input_random_num)])
        if args.pid:
            input_cmd.extend(["--pid", args.pid])
        run_stage(python_executable=python_executable, stage_name="03_input_generation", argv=input_cmd, logs_dir=logs_dir)

    should_run_input_check = args.run_input_check and not args.skip_input_check

    if should_run_input_check:
        check_cmd = [
            "start/run_check_inputs.py",
            "--dataset-root",
            str(dataset_root),
            "--timeout",
            str(args.check_timeout),
            "--jobs",
            str(args.check_jobs),
        ]
        if args.pid:
            check_cmd.extend(
                [
                    "--spec",
                    str(dataset_root / args.pid / "spec.txt"),
                    "--inputs-root",
                    str(inputs_root / args.pid),
                ]
            )
        else:
            check_cmd.extend(["--inputs-root", str(inputs_root)])
        run_stage(python_executable=python_executable, stage_name="04_input_checking", argv=check_cmd, logs_dir=logs_dir)

    if not args.skip_diff_test:
        diff_cmd = [
            "start/run_dif_test.py",
            "--layout",
            "dataset",
            "--lang",
            args.lang,
            "--variant-mode",
            args.variant_mode,
            "--dataset-root",
            str(dataset_root),
            "--variants-root",
            str(resolve_repo_path(args.variants_root)),
            "--tests-root",
            str(inputs_root),
            "--out-root",
            str(tcases_root),
            "--canonical-root",
            str(resolve_repo_path(args.canonical_root)),
            "--timeout",
            str(args.timeout),
            "--fixed-min-votes",
            str(args.fixed_min_votes),
            "--jobs",
            str(args.diff_jobs),
        ]
        if args.prefilter_variants:
            diff_cmd.extend(
                [
                    "--prefilter-variants",
                    "--prefilter-sample-size",
                    str(args.prefilter_sample_size),
                    "--prefilter-max-fail-rate",
                    str(args.prefilter_max_fail_rate),
                    "--prefilter-max-mismatch-rate",
                    str(args.prefilter_max_mismatch_rate),
                    "--prefilter-min-keep",
                    str(args.prefilter_min_keep),
                ]
            )
        if args.pid:
            diff_cmd.extend(["--pid", args.pid])
        run_stage(python_executable=python_executable, stage_name="05_differential_testing", argv=diff_cmd, logs_dir=logs_dir)

    if args.skip_summary:
        return

    report_root = tcases_root / args.lang
    run_stage(
        python_executable=python_executable,
        stage_name="06_report_summary",
        argv=[
            "start/report_summary.py",
            "--report-root",
            str(report_root),
            "--out",
            str(summary_root / "report_status_summary.csv"),
        ],
        logs_dir=logs_dir,
    )
    run_stage(
        python_executable=python_executable,
        stage_name="07_baseline_summary",
        argv=[
            "start/baseline_summary.py",
            "--report-root",
            str(report_root),
            "--out-dir",
            str(summary_root / "analysis"),
            "--skip-compile-check",
        ],
        logs_dir=logs_dir,
    )

    write_canonical_summary(report_root, summary_root)
    write_comparison_scaffold(summary_root.parent, summary_root / "comparison_scaffold.csv")


if __name__ == "__main__":
    main()
