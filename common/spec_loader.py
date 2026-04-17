from __future__ import annotations

from pathlib import Path


def find_dataset_spec(problem_dir: Path) -> Path | None:
    for candidate in (problem_dir / "spec.txt", problem_dir / "spec.txt.txt"):
        if candidate.exists():
            return candidate
    return None


def find_ac_spec(problem_dir: Path, spec_name: str = "spec.txt") -> Path | None:
    candidate = problem_dir / spec_name
    return candidate if candidate.exists() else None


def load_spec(spec_path: Path) -> str:
    return spec_path.read_text(encoding="utf-8").strip()
