from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckerResult:
    valid: bool
    status: str
    message: str


def validate_input_text(
    *,
    checker_path: Path | None,
    input_text: str,
    timeout: float = 10.0,
    python_executable: str = sys.executable,
) -> CheckerResult:
    if checker_path is None:
        return CheckerResult(valid=True, status="not_checked", message="checker not provided")

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
        tmp.write(input_text)
        tmp_path = Path(tmp.name)

    try:
        with tmp_path.open("r", encoding="utf-8", errors="ignore") as fh:
            result = subprocess.run(
                [python_executable, str(checker_path)],
                stdin=fh,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
    except subprocess.TimeoutExpired:
        return CheckerResult(valid=False, status="checker_timeout", message="checker timed out")
    finally:
        tmp_path.unlink(missing_ok=True)

    if result.returncode == 0:
        return CheckerResult(valid=True, status="valid", message=(result.stdout.strip() or "ok"))

    message = (result.stdout.strip() or result.stderr.strip() or "invalid input").strip()
    return CheckerResult(valid=False, status="invalid", message=message)
