from __future__ import annotations

from pathlib import Path

from common.execution import execute_program, list_test_inputs


def evaluate_patch_candidate(
    *,
    candidate_path: Path,
    put_path: Path,
    canonical_path: Path | None,
    tests_dir: Path | None,
    lang: str,
    timeout: float,
) -> dict[str, object]:
    test_files = list_test_inputs(tests_dir)
    if canonical_path is None:
        return {
            "tests_available": len(test_files),
            "tests_executed": 0,
            "behavior_changed": False,
            "mismatch_count": 0,
            "original_mismatch_count": 0,
            "appears_fixed": False,
            "evaluation_status": "missing_canonical",
            "per_test": [],
        }
    if not test_files:
        return {
            "tests_available": 0,
            "tests_executed": 0,
            "behavior_changed": False,
            "mismatch_count": 0,
            "original_mismatch_count": 0,
            "appears_fixed": False,
            "evaluation_status": "no_tests",
            "per_test": [],
        }

    per_test: list[dict[str, object]] = []
    behavior_changed = False
    mismatch_count = 0
    original_mismatch_count = 0
    executed = 0

    for test_file in test_files:
        input_text = test_file.read_text(encoding="utf-8")
        candidate_out, candidate_error = execute_program(
            program_path=candidate_path,
            input_text=input_text,
            lang=lang,
            timeout=timeout,
        )
        put_out, put_error = execute_program(
            program_path=put_path,
            input_text=input_text,
            lang=lang,
            timeout=timeout,
        )
        canonical_out, canonical_error = execute_program(
            program_path=canonical_path,
            input_text=input_text,
            lang=lang,
            timeout=timeout,
        )

        if not candidate_error and not canonical_error:
            executed += 1
        if not candidate_error and not put_error:
            behavior_changed = behavior_changed or (candidate_out != put_out)
        if not candidate_error and not canonical_error:
            mismatch_count += int(candidate_out != canonical_out)
        if not put_error and not canonical_error:
            original_mismatch_count += int(put_out != canonical_out)

        per_test.append(
            {
                "test_name": test_file.name,
                "candidate_output": candidate_out,
                "candidate_error": candidate_error,
                "put_output": put_out,
                "put_error": put_error,
                "canonical_output": canonical_out,
                "canonical_error": canonical_error,
            }
        )

    appears_fixed = executed > 0 and mismatch_count == 0 and original_mismatch_count > 0
    return {
        "tests_available": len(test_files),
        "tests_executed": executed,
        "behavior_changed": behavior_changed,
        "mismatch_count": mismatch_count,
        "original_mismatch_count": original_mismatch_count,
        "appears_fixed": appears_fixed,
        "evaluation_status": "evaluated",
        "per_test": per_test,
    }
