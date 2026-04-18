from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare shared inputs by running input generation and input checking."
    )
    parser.add_argument("--python", default=None)
    parser.add_argument("--pid", default=None)
    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--inputs-root", default="outputs/inputs")
    parser.add_argument("--prep-root", default="outputs/input_prep")
    parser.add_argument("--input-backend", choices=["generator", "llm", "mixed"], default="generator")
    parser.add_argument("--input-model", default="deepseek-chat")
    parser.add_argument("--input-template", default="PromptTemplates/geninput_direct")
    parser.add_argument("--input-num", type=int, default=100)
    parser.add_argument("--input-random-num", type=int, default=None)
    parser.add_argument("--input-llm-num", type=int, default=0)
    parser.add_argument("--input-seed", type=int, default=2)
    parser.add_argument("--input-jobs", type=int, default=1)
    parser.add_argument("--check-timeout", type=float, default=10.0)
    parser.add_argument("--check-jobs", type=int, default=8)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    python_executable = choose_python(args.python)
    dataset_root = resolve_repo_path(args.dataset_root)
    inputs_root = resolve_repo_path(args.inputs_root)
    prep_root = resolve_repo_path(args.prep_root)
    logs_dir = prep_root / "stage_logs"

    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

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
        stage_name="01_input_generation",
        argv=input_cmd,
        logs_dir=logs_dir,
    )

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
    run_stage(
        python_executable=python_executable,
        stage_name="02_input_checking",
        argv=check_cmd,
        logs_dir=logs_dir,
    )

    prep_root.mkdir(parents=True, exist_ok=True)
    (prep_root / "summary.txt").write_text(
        "\n".join(
            [
                "Input Prep Summary",
                f"dataset_root={dataset_root}",
                f"inputs_root={inputs_root}",
                f"pid={args.pid or 'ALL'}",
                f"input_backend={args.input_backend}",
                f"input_num={args.input_num}",
                f"input_jobs={args.input_jobs}",
                f"check_jobs={args.check_jobs}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"[DONE] input prep logs: {logs_dir}")


if __name__ == "__main__":
    main()
