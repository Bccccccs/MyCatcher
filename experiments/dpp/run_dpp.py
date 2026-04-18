from __future__ import annotations

import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.path_utils import ensure_dir, resolve_repo_path, write_text
from common.problem_loader import discover_problems
from common.report_utils import write_baseline_overview, write_experiment_comparison
from experiments.dpp.evaluator import build_summary_rows, write_dpp_summary


def run_problem(
    *,
    problem,
    python_executable: str,
    lang: str,
    variant_mode: str,
    out_root: Path,
    timeout: float,
    fixed_min_votes: int,
    prefilter_variants: bool,
) -> None:
    out_dir = ensure_dir(out_root / problem.pid)
    raw_log_path = out_dir / "raw.log"

    missing = []
    if problem.put_path is None:
        missing.append("put")
    if problem.canonical_path is None:
        missing.append("canonical")
    if problem.variants_dir is None:
        missing.append("variants")
    if problem.tests_dir is None:
        missing.append("tests")
    if missing:
        write_text(raw_log_path, f"[SKIP] missing={','.join(missing)}\n")
        return

    cmd = [
        python_executable,
        str(ROOT / "LLM_Gen" / "differential_testing.py"),
        "--lang",
        lang,
        "--variant_mode",
        variant_mode,
        "--put",
        str(problem.put_path),
        "--variants",
        str(problem.variants_dir),
        "--tests",
        str(problem.tests_dir),
        "--out",
        str(out_dir),
        "--canonical",
        str(problem.canonical_path),
        "--timeout",
        str(timeout),
        "--fixed-min-votes",
        str(fixed_min_votes),
    ]
    if prefilter_variants:
        cmd.append("--prefilter-variants")

    completed = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    write_text(raw_log_path, completed.stdout or "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Legacy DPP differential-testing-only runner")
    parser.add_argument("--layout", choices=["dataset", "ac"], default="dataset")
    parser.add_argument("--pid", default=None)
    parser.add_argument("--lang", choices=["py", "cpp"], default="cpp")
    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--canonical-root", default="AC")
    parser.add_argument("--variants-root", default="Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp")
    parser.add_argument("--ac-root", default="AC")
    parser.add_argument("--tests-root", default="outputs/inputs")
    parser.add_argument("--bundle-dir", default="gen_bundle")
    parser.add_argument("--variants-dirname", default="variants")
    parser.add_argument("--variant-mode", choices=["my", "trickybugs"], default="trickybugs")
    parser.add_argument("--canonical-name", default=None)
    parser.add_argument("--put-name", default=None)
    parser.add_argument("--spec-name", default="spec.txt")
    parser.add_argument("--out-root", default="outputs/dpp")
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--fixed-min-votes", type=int, default=6)
    parser.add_argument("--prefilter-variants", action="store_true")
    parser.add_argument("--jobs", type=int, default=8, help="Number of problems to process in parallel")
    args = parser.parse_args()

    out_root = resolve_repo_path(args.out_root)
    problem_root = resolve_repo_path(args.dataset_root if args.layout == "dataset" else args.ac_root)
    canonical_root = resolve_repo_path(args.canonical_root) if args.layout == "dataset" else None
    variants_root = resolve_repo_path(args.variants_root) if args.layout == "dataset" else None
    tests_root = resolve_repo_path(args.tests_root)

    problems = discover_problems(
        layout=args.layout,
        problem_root=problem_root,
        lang=args.lang,
        pid=args.pid,
        canonical_root=canonical_root,
        tests_root=tests_root,
        variants_root=variants_root,
        spec_name=args.spec_name,
        put_name=args.put_name,
        canonical_name=args.canonical_name,
        bundle_dir=args.bundle_dir,
        variants_dirname=args.variants_dirname,
    )

    jobs = max(1, args.jobs)
    if jobs == 1:
        for problem in problems:
            run_problem(
                problem=problem,
                python_executable=sys.executable,
                lang=args.lang,
                variant_mode=args.variant_mode,
                out_root=out_root,
                timeout=args.timeout,
                fixed_min_votes=args.fixed_min_votes,
                prefilter_variants=args.prefilter_variants,
            )
    else:
        with ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = [
                executor.submit(
                    run_problem,
                    problem=problem,
                    python_executable=sys.executable,
                    lang=args.lang,
                    variant_mode=args.variant_mode,
                    out_root=out_root,
                    timeout=args.timeout,
                    fixed_min_votes=args.fixed_min_votes,
                    prefilter_variants=args.prefilter_variants,
                )
                for problem in problems
            ]
            for future in as_completed(futures):
                future.result()

    write_dpp_summary(out_root)
    summary_rows = build_summary_rows(out_root)
    write_baseline_overview(
        out_dir=out_root,
        baseline="dpp",
        summary_rows=summary_rows,
        metric_keys=["tests_dir_size", "variants_used", "saved", "found", "tp_count", "fp_count"],
    )
    write_experiment_comparison(out_root.parent)


if __name__ == "__main__":
    main()
