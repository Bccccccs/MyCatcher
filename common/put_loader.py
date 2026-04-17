from __future__ import annotations

from pathlib import Path


def is_probably_text_file(path: Path) -> bool:
    try:
        raw = path.read_bytes()
    except OSError:
        return False
    if b"\x00" in raw:
        return False
    try:
        raw.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def find_dataset_put(problem_dir: Path, lang: str) -> Path | None:
    if lang == "cpp":
        candidates = [problem_dir / "put.cpp"]
        candidates.extend(sorted(problem_dir.glob("sol_*.cpp")))
        put_no_ext = problem_dir / "put"
        if put_no_ext.exists() and is_probably_text_file(put_no_ext):
            candidates.append(put_no_ext)
    else:
        candidates = [problem_dir / "put.py", problem_dir / "put"]
        candidates.extend(sorted(problem_dir.glob("sol_*.py")))

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_ac_put(problem_dir: Path, lang: str, put_name: str | None = None) -> Path | None:
    if put_name:
        candidate = problem_dir / put_name
        return candidate if candidate.exists() else None

    if lang == "cpp":
        candidates = [problem_dir / "ac_sol.cpp", problem_dir / "put.cpp", problem_dir / "ac_sol"]
    else:
        candidates = [problem_dir / "ac_sol.py", problem_dir / "put.py", problem_dir / "ac_sol"]

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_canonical(ac_root: Path, pid: str, lang: str, canonical_name: str | None = None) -> Path | None:
    return find_ac_put(ac_root / pid, lang, canonical_name)
