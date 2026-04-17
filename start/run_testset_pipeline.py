from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


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


def iter_problem_dirs(dataset_root: Path, pid: str | None) -> list[Path]:
    if pid:
        return [dataset_root / pid]
    return sorted(path for path in dataset_root.iterdir() if path.is_dir())


def find_put_file(problem_dir: Path, lang: str) -> Path | None:
    if lang == "cpp":
        candidates = [problem_dir / "put.cpp", problem_dir / "put"]
        candidates.extend(sorted(problem_dir.glob("sol_*.cpp")))
    else:
        candidates = [problem_dir / "put.py", problem_dir / "put"]
        candidates.extend(sorted(problem_dir.glob("sol_*.py")))

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def validate_testset(dataset_root: Path, pid: str | None, lang: str) -> None:
    if not dataset_root.exists():
        raise FileNotFoundError(f"Testset root not found: {dataset_root}")

    problem_dirs = iter_problem_dirs(dataset_root, pid)
    if not problem_dirs:
        raise RuntimeError(f"No problem directories found under: {dataset_root}")

    missing: list[str] = []
    for problem_dir in problem_dirs:
        if not problem_dir.exists():
            missing.append(f"{problem_dir.name}: missing directory")
            continue
        if not (problem_dir / "spec.txt").exists():
            missing.append(f"{problem_dir.name}: missing spec.txt")
        if find_put_file(problem_dir, lang) is None:
            expected = "put.cpp / sol_*.cpp" if lang == "cpp" else "put.py / sol_*.py"
            missing.append(f"{problem_dir.name}: missing PUT ({expected})")

    if missing:
        details = "\n".join(f" - {item}" for item in missing)
        raise RuntimeError(f"Invalid Testset layout:\n{details}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="One-shot pipeline for Testset/<pid>/ {spec.txt, PUT} problems."
    )
    parser.add_argument("--python", default=None, help="Interpreter for wrapped stage scripts. Defaults to .venv/bin/python if available.")
    parser.add_argument("--dataset-root", default="Testset", help="Problem root containing pxxxxx directories.")
    parser.add_argument("--pid", default=None, help="Run only one problem id, e.g. p02547")
    parser.add_argument("--lang", choices=["cpp", "py"], default="cpp")

    parser.add_argument("--variants-root", default="outputs/testset/variants")
    parser.add_argument("--inputs-root", default="outputs/testset/inputs")
    parser.add_argument("--reports-root", default="outputs/testset/tcases")
    parser.add_argument("--logs-root", default="outputs/testset/logs")

    parser.add_argument("--tool-model", default="deepseek-chat")
    parser.add_argument("--generator-template", default="geninput_generator")
    parser.add_argument("--checker-template", default="geninput_inspector")

    parser.add_argument("--variant-k", type=int, default=10)
    parser.add_argument("--variant-model", default="deepseek-chat")
    parser.add_argument("--variant-template", default=None)
    parser.add_argument("--variant-index-start", type=int, default=0)
    parser.add_argument("--variant-sleep", type=float, default=0.2)

    parser.add_argument("--input-backend", choices=["generator", "llm", "mixed"], default="generator")
    parser.add_argument("--input-model", default="deepseek-chat")
    parser.add_argument("--input-template", default="PromptTemplates/geninput_direct")
    parser.add_argument("--input-num", type=int, default=100)
    parser.add_argument("--input-random-num", type=int, default=None)
    parser.add_argument("--input-llm-num", type=int, default=10)
    parser.add_argument("--input-seed", type=int, default=2)
    parser.add_argument("--input-jobs", type=int, default=1)

    parser.add_argument("--canonical-root", default=None, help="Optional canonical root like AC. If omitted, diff testing runs without canonical.")
    parser.add_argument("--canonical-name", default=None, help="Optional canonical filename inside canonical root/<pid>/")
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--fixed-min-votes", type=int, default=6)
    parser.add_argument("--diff-jobs", type=int, default=8)

    parser.add_argument("--skip-variant-gen", action="store_true")
    parser.add_argument("--skip-tool-gen", action="store_true")
    parser.add_argument("--skip-input-gen", action="store_true")
    parser.add_argument("--skip-diff-test", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    python_executable = choose_python(args.python)
    dataset_root = resolve_repo_path(args.dataset_root)
    variants_root = resolve_repo_path(args.variants_root)
    inputs_root = resolve_repo_path(args.inputs_root)
    reports_root = resolve_repo_path(args.reports_root)
    logs_root = resolve_repo_path(args.logs_root)

    validate_testset(dataset_root, args.pid, args.lang)

    if not args.skip_variant_gen:
        variant_cmd = [
            "start/run_varProgs_gen.py",
            "--layout",
            "dataset",
            "--dataset-root",
            str(dataset_root),
            "--out-root",
            str(variants_root),
            "--lang",
            args.lang,
            "--mode",
            "dpp",
            "--naming",
            "default",
            "--k",
            str(args.variant_k),
            "--index-start",
            str(args.variant_index_start),
            "--model",
            args.variant_model,
            "--sleep",
            str(args.variant_sleep),
        ]
        if args.variant_template:
            variant_cmd.extend(["--template", args.variant_template])
        if args.pid:
            variant_cmd.extend(["--pid", args.pid])
        run_stage(
            python_executable=python_executable,
            stage_name="01_variant_generation",
            argv=variant_cmd,
            logs_dir=logs_root,
        )

    if not args.skip_tool_gen:
        tool_cmd = [
            "start/run_gen_tools.py",
            "--tool",
            "both",
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
            stage_name="02_tool_generation",
            argv=tool_cmd,
            logs_dir=logs_root,
        )

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
        run_stage(
            python_executable=python_executable,
            stage_name="03_input_generation",
            argv=input_cmd,
            logs_dir=logs_root,
        )

    if not args.skip_diff_test:
        diff_cmd = [
            "start/run_dif_test.py",
            "--layout",
            "dataset",
            "--lang",
            args.lang,
            "--variant-mode",
            "my",
            "--dataset-root",
            str(dataset_root),
            "--variants-root",
            str(variants_root),
            "--tests-root",
            str(inputs_root),
            "--out-root",
            str(reports_root),
            "--timeout",
            str(args.timeout),
            "--fixed-min-votes",
            str(args.fixed_min_votes),
            "--jobs",
            str(args.diff_jobs),
        ]
        if args.canonical_root:
            diff_cmd.extend(["--canonical-root", str(resolve_repo_path(args.canonical_root))])
        else:
            diff_cmd.append("--allow-missing-canonical")
        if args.canonical_name:
            diff_cmd.extend(["--canonical-name", args.canonical_name])
        if args.pid:
            diff_cmd.extend(["--pid", args.pid])
        run_stage(
            python_executable=python_executable,
            stage_name="04_differential_testing",
            argv=diff_cmd,
            logs_dir=logs_root,
        )


if __name__ == "__main__":
    main()
