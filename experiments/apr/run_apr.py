from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.llm_client import generate_text
from common.path_utils import ensure_dir, resolve_repo_path, safe_rel, write_text
from common.problem_loader import ProblemContext, discover_problems
from common.report_utils import write_baseline_overview, write_experiment_comparison, write_report_bundle, write_summary_table
from common.spec_loader import load_spec
from experiments.apr.evaluator import evaluate_patch_candidate
from experiments.apr.patch_executor import compile_candidate_with_log, normalize_patch_response, save_candidate
from experiments.apr.prompt_templates import build_apr_prompt


SUMMARY_FIELDS = [
    "pid",
    "status",
    "candidate_patches",
    "compile_successes",
    "behavior_changes",
    "apparent_fixes",
    "report_json",
]


def process_problem(
    *,
    problem: ProblemContext,
    out_root: Path,
    lang: str,
    model: str,
    num_candidates: int,
    timeout: float,
) -> dict[str, object]:
    out_dir = ensure_dir(out_root / problem.pid)
    raw_dir = ensure_dir(out_dir / "raw_llm_output")
    patches_dir = ensure_dir(out_dir / "candidate_patches")
    compile_dir = ensure_dir(out_dir / "compile_logs")
    executions_dir = ensure_dir(out_dir / "executions")

    missing = []
    if problem.spec_path is None:
        missing.append("spec")
    if problem.put_path is None:
        missing.append("put")
    if missing:
        report_json = {"pid": problem.pid, "status": "skipped", "missing": missing}
        write_report_bundle(
            out_dir=out_dir,
            report_json=report_json,
            report_lines=[
                "APR Baseline Report",
                f"pid={problem.pid}",
                "status=skipped",
                f"missing={','.join(missing)}",
            ],
        )
        return {
            "pid": problem.pid,
            "status": "skipped",
            "candidate_patches": 0,
            "compile_successes": 0,
            "behavior_changes": 0,
            "apparent_fixes": 0,
            "report_json": safe_rel(out_dir / "report.json"),
        }

    spec = load_spec(problem.spec_path)
    put_code = problem.put_path.read_text(encoding="utf-8")
    language_name = "Python" if lang == "py" else "C++"

    candidate_rows: list[dict[str, object]] = []
    compile_successes = 0
    behavior_changes = 0
    apparent_fixes = 0
    extension = ".py" if lang == "py" else ".cpp"

    for idx in range(num_candidates):
        prompt = build_apr_prompt(spec=spec, put_code=put_code, language_name=language_name)
        raw_response = generate_text(prompt=prompt, model=model)
        write_text(raw_dir / f"response_{idx:03d}.txt", raw_response.rstrip() + "\n")

        normalized = normalize_patch_response(raw_response=raw_response, lang=lang)
        if not normalized:
            candidate_rows.append(
                {
                    "candidate_index": idx,
                    "compile_ok": False,
                    "compile_message": "empty_candidate",
                    "evaluation_status": "empty_candidate",
                    "behavior_changed": False,
                    "appears_fixed": False,
                }
            )
            continue

        candidate_path = patches_dir / f"candidate_{idx:03d}{extension}"
        save_candidate(path=candidate_path, content=normalized)
        compile_log_path = compile_dir / f"candidate_{idx:03d}.log"
        compile_ok, compile_message = compile_candidate_with_log(
            candidate_path=candidate_path,
            lang=lang,
            log_path=compile_log_path,
        )
        if compile_ok:
            compile_successes += 1

        evaluation = {
            "tests_available": 0,
            "tests_executed": 0,
            "behavior_changed": False,
            "mismatch_count": 0,
            "original_mismatch_count": 0,
            "appears_fixed": False,
            "evaluation_status": "compile_failed" if not compile_ok else "not_evaluated",
            "per_test": [],
        }
        if compile_ok:
            evaluation = evaluate_patch_candidate(
                candidate_path=candidate_path,
                put_path=problem.put_path,
                canonical_path=problem.canonical_path,
                tests_dir=problem.tests_dir,
                lang=lang,
                timeout=timeout,
            )
            behavior_changes += int(bool(evaluation["behavior_changed"]))
            apparent_fixes += int(bool(evaluation["appears_fixed"]))

        record = {
            "candidate_index": idx,
            "candidate_path": safe_rel(candidate_path),
            "compile_ok": compile_ok,
            "compile_message": compile_message,
            **evaluation,
        }
        candidate_rows.append(record)
        write_text(executions_dir / f"candidate_{idx:03d}.json", json.dumps(record, ensure_ascii=True, indent=2) + "\n")

    report_json = {
        "pid": problem.pid,
        "status": "ok",
        "layout": problem.layout,
        "spec_path": safe_rel(problem.spec_path),
        "put_path": safe_rel(problem.put_path),
        "canonical_path": safe_rel(problem.canonical_path) if problem.canonical_path else "",
        "tests_dir": safe_rel(problem.tests_dir) if problem.tests_dir else "",
        "candidate_patches": num_candidates,
        "compile_successes": compile_successes,
        "behavior_changes": behavior_changes,
        "apparent_fixes": apparent_fixes,
        "candidates": candidate_rows,
    }
    write_report_bundle(
        out_dir=out_dir,
        report_json=report_json,
        report_lines=[
            "APR Baseline Report",
            f"pid={problem.pid}",
            "status=ok",
            f"candidate_patches={num_candidates}",
            f"compile_successes={compile_successes}",
            f"behavior_changes={behavior_changes}",
            f"apparent_fixes={apparent_fixes}",
        ],
    )
    return {
        "pid": problem.pid,
        "status": "ok",
        "candidate_patches": num_candidates,
        "compile_successes": compile_successes,
        "behavior_changes": behavior_changes,
        "apparent_fixes": apparent_fixes,
        "report_json": safe_rel(out_dir / "report.json"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="APR baseline runner")
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
    parser.add_argument("--out-root", default="outputs/apr")
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--num-candidates", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=2.0)
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
    if jobs == 1:
        summary_rows = [
            process_problem(
                problem=problem,
                out_root=out_root,
                lang=args.lang,
                model=args.model,
                num_candidates=args.num_candidates,
                timeout=args.timeout,
            )
            for problem in problems
        ]
    else:
        summary_rows = []
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = [
                executor.submit(
                    process_problem,
                    problem=problem,
                    out_root=out_root,
                    lang=args.lang,
                    model=args.model,
                    num_candidates=args.num_candidates,
                    timeout=args.timeout,
                )
                for problem in problems
            ]
            for future in as_completed(futures):
                summary_rows.append(future.result())
    write_summary_table(out_root / "summary.csv", summary_rows, SUMMARY_FIELDS)
    write_baseline_overview(
        out_dir=out_root,
        baseline="apr",
        summary_rows=summary_rows,
        metric_keys=["candidate_patches", "compile_successes", "behavior_changes", "apparent_fixes"],
    )
    write_experiment_comparison(out_root.parent)


if __name__ == "__main__":
    main()
