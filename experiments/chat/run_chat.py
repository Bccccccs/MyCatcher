from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.checker_runner import validate_input_text
from common.llm_client import generate_text
from common.path_utils import ensure_dir, resolve_repo_path, safe_rel, write_text
from common.problem_loader import ProblemContext, discover_problems
from common.report_utils import write_baseline_overview, write_experiment_comparison, write_report_bundle, write_summary_table
from common.spec_loader import load_spec
from experiments.chat.evaluator import evaluate_test_case
from experiments.chat.prompt_templates import build_chat_prompt
from src.progress import print_progress


SUMMARY_FIELDS = [
    "pid",
    "status",
    "total_generated_inputs",
    "valid_inputs",
    "invalid_inputs",
    "bug_revealing_inputs",
    "detection_status",
    "report_json",
]


def split_cases_from_text(text: str) -> list[str]:
    delimiter = "<<<CASE>>>"
    raw = (text or "").strip()
    if not raw:
        return []
    if delimiter in raw:
        return [part.strip() + "\n" for part in raw.split(delimiter) if part.strip()]

    cases: list[str] = []
    buffer: list[str] = []
    for line in raw.splitlines():
        if not line.strip():
            if buffer:
                cases.append("\n".join(buffer).strip() + "\n")
                buffer = []
            continue
        buffer.append(line.rstrip("\n"))
    if buffer:
        cases.append("\n".join(buffer).strip() + "\n")
    return [case for case in cases if case.strip()]


def process_problem(
    *,
    problem: ProblemContext,
    out_root: Path,
    lang: str,
    model: str,
    num_candidates: int,
    batch_size: int,
    timeout: float,
    checker_timeout: float,
    use_checker: bool,
) -> dict[str, object]:
    out_dir = ensure_dir(out_root / problem.pid)
    raw_dir = ensure_dir(out_dir / "raw_llm_output")
    normalized_dir = ensure_dir(out_dir / "normalized_tests")
    invalid_dir = ensure_dir(out_dir / "invalid_tests")
    executions_dir = ensure_dir(out_dir / "executions")

    missing = []
    if problem.spec_path is None:
        missing.append("spec")
    if problem.put_path is None:
        missing.append("put")
    if problem.canonical_path is None:
        missing.append("canonical")

    if missing:
        report_json = {
            "pid": problem.pid,
            "status": "skipped",
            "missing": missing,
        }
        write_report_bundle(
            out_dir=out_dir,
            report_json=report_json,
            report_lines=[
                "CHAT Baseline Report",
                f"pid={problem.pid}",
                "status=skipped",
                f"missing={','.join(missing)}",
            ],
        )
        return {
            "pid": problem.pid,
            "status": "skipped",
            "total_generated_inputs": 0,
            "valid_inputs": 0,
            "invalid_inputs": 0,
            "bug_revealing_inputs": 0,
            "detection_status": "skipped",
            "report_json": safe_rel(out_dir / "report.json"),
        }

    spec = load_spec(problem.spec_path)
    put_code = problem.put_path.read_text(encoding="utf-8")

    total_generated = 0
    valid_count = 0
    invalid_count = 0
    bug_count = 0
    execution_records: list[dict[str, object]] = []

    next_index = 0
    response_index = 0
    while next_index < num_candidates:
        requested = min(batch_size, num_candidates - next_index)
        prompt = build_chat_prompt(spec=spec, put_code=put_code, num_candidates=requested)
        raw_response = generate_text(prompt=prompt, model=model)
        write_text(raw_dir / f"response_{response_index:03d}.txt", raw_response.rstrip() + "\n")
        response_index += 1

        generated_this_round = 0
        for case in split_cases_from_text(raw_response):
            if next_index >= num_candidates:
                break
            test_name = f"test_{next_index:03d}"
            normalized_path = normalized_dir / f"{test_name}.in"
            write_text(normalized_path, case.rstrip() + "\n")
            total_generated += 1
            generated_this_round += 1

            checker_result = validate_input_text(
                checker_path=problem.checker_path if use_checker else None,
                input_text=case,
                timeout=checker_timeout,
            )
            if not checker_result.valid:
                invalid_count += 1
                write_text(invalid_dir / f"{test_name}.in", case.rstrip() + "\n")
                write_text(invalid_dir / f"{test_name}.reason.txt", checker_result.message + "\n")
                execution_records.append(
                    {
                        "pid": problem.pid,
                        "test_name": test_name,
                        "valid": False,
                        "checker_status": checker_result.status,
                        "checker_message": checker_result.message,
                        "bug_revealing": False,
                    }
                )
                next_index += 1
                continue

            valid_count += 1
            evaluation = evaluate_test_case(
                pid=problem.pid,
                test_name=test_name,
                input_text=case,
                put_path=problem.put_path,
                canonical_path=problem.canonical_path,
                lang=lang,
                timeout=timeout,
            )
            evaluation["valid"] = True
            evaluation["checker_status"] = checker_result.status
            evaluation["checker_message"] = checker_result.message
            if evaluation["bug_revealing"]:
                bug_count += 1
            execution_records.append(evaluation)
            write_text(executions_dir / f"{test_name}.json", json.dumps(evaluation, ensure_ascii=True, indent=2) + "\n")
            next_index += 1

        if generated_this_round == 0:
            break

    detection_status = "detected" if bug_count > 0 else "not_detected"
    report_json = {
        "pid": problem.pid,
        "status": "ok",
        "layout": problem.layout,
        "spec_path": safe_rel(problem.spec_path),
        "put_path": safe_rel(problem.put_path),
        "canonical_path": safe_rel(problem.canonical_path) if problem.canonical_path else "",
        "checker_path": safe_rel(problem.checker_path) if problem.checker_path else "",
        "total_generated_inputs": total_generated,
        "valid_inputs": valid_count,
        "invalid_inputs": invalid_count,
        "bug_revealing_inputs": bug_count,
        "detection_status": detection_status,
        "execution_records": execution_records,
    }
    write_report_bundle(
        out_dir=out_dir,
        report_json=report_json,
        report_lines=[
            "CHAT Baseline Report",
            f"pid={problem.pid}",
            "status=ok",
            f"total_generated_inputs={total_generated}",
            f"valid_inputs={valid_count}",
            f"invalid_inputs={invalid_count}",
            f"bug_revealing_inputs={bug_count}",
            f"detection_status={detection_status}",
        ],
    )
    return {
        "pid": problem.pid,
        "status": "ok",
        "total_generated_inputs": total_generated,
        "valid_inputs": valid_count,
        "invalid_inputs": invalid_count,
        "bug_revealing_inputs": bug_count,
        "detection_status": detection_status,
        "report_json": safe_rel(out_dir / "report.json"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="CHAT / DirectChat baseline runner")
    parser.add_argument("--layout", choices=["dataset", "ac"], default="dataset")
    parser.add_argument("--pid", default=None)
    parser.add_argument("--lang", choices=["py", "cpp"], default="cpp")
    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--canonical-root", default="AC")
    parser.add_argument("--ac-root", default="AC")
    parser.add_argument("--tests-root", default="outputs/inputs")
    parser.add_argument("--checker-name", default="check_input.py")
    parser.add_argument("--canonical-name", default=None)
    parser.add_argument("--put-name", default=None)
    parser.add_argument("--spec-name", default="spec.txt")
    parser.add_argument("--out-root", default="outputs/chat")
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--num-candidates", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--checker-timeout", type=float, default=10.0)
    parser.add_argument("--skip-checker", action="store_true")
    parser.add_argument("--jobs", type=int, default=8, help="Number of problems to process in parallel")
    args = parser.parse_args()

    out_root = resolve_repo_path(args.out_root)
    problem_root = resolve_repo_path(args.dataset_root if args.layout == "dataset" else args.ac_root)
    canonical_root = resolve_repo_path(args.canonical_root) if args.layout == "dataset" else None
    tests_root = resolve_repo_path(args.tests_root)

    problems = discover_problems(
        layout=args.layout,
        problem_root=problem_root,
        lang=args.lang,
        pid=args.pid,
        canonical_root=canonical_root,
        tests_root=tests_root,
        checker_name=args.checker_name,
        spec_name=args.spec_name,
        put_name=args.put_name,
        canonical_name=args.canonical_name,
    )

    jobs = max(1, args.jobs)
    print_progress(0, len(problems), f"chat problems root={problem_root}")
    if jobs == 1:
        summary_rows = []
        for done, problem in enumerate(problems, 1):
            summary_rows.append(
                process_problem(
                    problem=problem,
                    out_root=out_root,
                    lang=args.lang,
                    model=args.model,
                    num_candidates=args.num_candidates,
                    batch_size=args.batch_size,
                    timeout=args.timeout,
                    checker_timeout=args.checker_timeout,
                    use_checker=not args.skip_checker,
                )
            )
            print_progress(done, len(problems), f"chat latest={problem.pid}")
    else:
        summary_rows = []
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = {
                executor.submit(
                    process_problem,
                    problem=problem,
                    out_root=out_root,
                    lang=args.lang,
                    model=args.model,
                    num_candidates=args.num_candidates,
                    batch_size=args.batch_size,
                    timeout=args.timeout,
                    checker_timeout=args.checker_timeout,
                    use_checker=not args.skip_checker,
                ): problem
                for problem in problems
            }
            for done, future in enumerate(as_completed(futures), 1):
                summary_rows.append(future.result())
                print_progress(done, len(problems), f"chat latest={futures[future].pid}")
    summary_rows.sort(key=lambda row: str(row["pid"]))
    write_summary_table(out_root / "summary.csv", summary_rows, SUMMARY_FIELDS)
    write_baseline_overview(
        out_dir=out_root,
        baseline="chat",
        summary_rows=summary_rows,
        metric_keys=["total_generated_inputs", "valid_inputs", "invalid_inputs", "bug_revealing_inputs"],
    )
    write_experiment_comparison(out_root.parent)


if __name__ == "__main__":
    main()
