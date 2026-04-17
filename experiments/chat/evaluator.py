from __future__ import annotations

from pathlib import Path

from common.execution import execute_program


def evaluate_test_case(
    *,
    pid: str,
    test_name: str,
    input_text: str,
    put_path: Path,
    canonical_path: Path | None,
    lang: str,
    timeout: float,
) -> dict[str, object]:
    put_out, put_error = execute_program(program_path=put_path, input_text=input_text, lang=lang, timeout=timeout)
    canonical_out = ""
    canonical_error = ""
    if canonical_path is not None:
        canonical_out, canonical_error = execute_program(
            program_path=canonical_path,
            input_text=input_text,
            lang=lang,
            timeout=timeout,
        )

    bug_revealing = False
    if canonical_path is not None and not put_error and not canonical_error:
        bug_revealing = put_out != canonical_out

    return {
        "pid": pid,
        "test_name": test_name,
        "put_output": put_out,
        "put_error": put_error,
        "canonical_output": canonical_out,
        "canonical_error": canonical_error,
        "bug_revealing": bug_revealing,
    }
