from __future__ import annotations

import re
from pathlib import Path

from common.execution import compile_candidate
from common.path_utils import write_text


def normalize_patch_response(*, raw_response: str, lang: str) -> str:
    code = raw_response.strip()
    fence = re.search(r"```(?:[a-zA-Z0-9_+\-#.]*)?\s*([\s\S]*?)```", code, re.IGNORECASE)
    if fence:
        code = fence.group(1).strip()
    lines = code.splitlines()
    if lines:
        first = lines[0].strip().lower()
        if first in {"cpp", "c++", "python", "py"}:
            code = "\n".join(lines[1:]).lstrip()
    if lang == "cpp":
        start_markers = ("#include", "using namespace", "int main", "template<", "template <")
    else:
        start_markers = ("import ", "from ", "def ", "class ", "if __name__")
    split_lines = code.splitlines()
    start_index = 0
    for idx, line in enumerate(split_lines):
        if any(line.lstrip().startswith(marker) for marker in start_markers):
            start_index = idx
            break
    return "\n".join(split_lines[start_index:]).strip()


def save_candidate(*, path: Path, content: str) -> None:
    write_text(path, content.rstrip() + "\n")


def compile_candidate_with_log(*, candidate_path: Path, lang: str, log_path: Path) -> tuple[bool, str]:
    ok, message = compile_candidate(candidate_path=candidate_path, lang=lang)
    write_text(log_path, (message or "compile_ok") + "\n")
    return ok, message
