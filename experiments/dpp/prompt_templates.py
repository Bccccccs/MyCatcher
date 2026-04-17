from __future__ import annotations

from pathlib import Path

from common.path_utils import ROOT


def default_template_path() -> Path:
    return ROOT / "PromptTemplates" / "genprog_dfp"
