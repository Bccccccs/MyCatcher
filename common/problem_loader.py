from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from common.path_utils import list_problem_dirs
from common.put_loader import find_ac_put, find_canonical, find_dataset_put
from common.spec_loader import find_ac_spec, find_dataset_spec


@dataclass
class ProblemContext:
    pid: str
    layout: str
    problem_dir: Path
    spec_path: Path | None
    put_path: Path | None
    canonical_path: Path | None
    checker_path: Path | None
    tests_dir: Path | None
    variants_dir: Path | None


def discover_problems(
    *,
    layout: str,
    problem_root: Path,
    lang: str,
    pid: str | None = None,
    canonical_root: Path | None = None,
    tests_root: Path | None = None,
    variants_root: Path | None = None,
    checker_name: str = "check_input.py",
    spec_name: str = "spec.txt",
    put_name: str | None = None,
    canonical_name: str | None = None,
    bundle_dir: str = "gen_bundle",
    variants_dirname: str = "variants",
) -> list[ProblemContext]:
    contexts: list[ProblemContext] = []
    for problem_dir in list_problem_dirs(problem_root, pid):
        if layout == "dataset":
            spec_path = find_dataset_spec(problem_dir)
            put_path = find_dataset_put(problem_dir, lang)
            canonical_path = None
            if canonical_root is not None:
                canonical_path = find_canonical(canonical_root, problem_dir.name, lang, canonical_name)
            checker_path = problem_dir / checker_name
            tests_dir = tests_root / problem_dir.name if tests_root is not None else None
            variants_dir = variants_root / problem_dir.name if variants_root is not None else None
        else:
            spec_path = find_ac_spec(problem_dir, spec_name)
            put_path = find_ac_put(problem_dir, lang, put_name)
            canonical_path = find_ac_put(problem_dir, lang, canonical_name)
            checker_path = problem_dir / checker_name
            tests_dir = tests_root / problem_dir.name if tests_root is not None else None
            variants_dir = problem_dir / bundle_dir / variants_dirname if variants_root is None else variants_root / problem_dir.name

        contexts.append(
            ProblemContext(
                pid=problem_dir.name,
                layout=layout,
                problem_dir=problem_dir,
                spec_path=spec_path if spec_path and spec_path.exists() else None,
                put_path=put_path if put_path and put_path.exists() else None,
                canonical_path=canonical_path if canonical_path and canonical_path.exists() else None,
                checker_path=checker_path if checker_path.exists() else None,
                tests_dir=tests_dir if tests_dir and tests_dir.exists() else None,
                variants_dir=variants_dir if variants_dir and variants_dir.exists() else None,
            )
        )
    return contexts
