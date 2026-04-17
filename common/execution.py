from __future__ import annotations

import py_compile
from pathlib import Path

from LLM_Gen.differential_testing import compile_cpp, run_program
from common.path_utils import ROOT


def default_build_dir() -> Path:
    return ROOT / "build" / "experiment_bins"


def execute_program(
    *,
    program_path: Path,
    input_text: str,
    lang: str,
    timeout: float,
    build_dir: Path | None = None,
) -> tuple[str, str]:
    try:
        output = run_program(program_path, input_text, lang, build_dir or default_build_dir(), timeout)
        return output, ""
    except Exception as exc:  # noqa: BLE001
        return "", str(exc)


def compile_candidate(
    *,
    candidate_path: Path,
    lang: str,
    build_dir: Path | None = None,
) -> tuple[bool, str]:
    try:
        if lang == "cpp":
            compile_cpp(candidate_path, build_dir or default_build_dir())
        else:
            py_compile.compile(str(candidate_path), doraise=True)
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def list_test_inputs(tests_dir: Path | None) -> list[Path]:
    if tests_dir is None or not tests_dir.exists():
        return []
    return sorted(path for path in tests_dir.glob("*.in") if path.is_file())
