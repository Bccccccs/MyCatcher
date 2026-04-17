from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass


def format_progress(done: int, total: int, label: str = "") -> str:
    if total <= 0:
        base = f"[PROGRESS] {done}/0"
    else:
        pct = min(100.0, max(0.0, done * 100.0 / total))
        base = f"[PROGRESS] {done}/{total} ({pct:5.1f}%)"
    return f"{base} {label}".rstrip()


def _format_live_progress(done: int, total: int, label: str, frame_index: int) -> str:
    spinner = "|/-\\"[frame_index % 4]
    if total <= 0:
        bar = "-" * 24
        pct = "  --.-%"
    else:
        width = 24
        ratio = min(1.0, max(0.0, done / total))
        filled = min(width, max(0, int(round(ratio * width))))
        bar = "#" * filled + "-" * (width - filled)
        pct = f"{ratio * 100:6.1f}%"
    base = f"[{spinner}] [{bar}] {done}/{total} {pct}"
    return f"{base} {label}".rstrip()


def _should_use_live_progress() -> bool:
    stream = sys.stdout
    return bool(getattr(stream, "isatty", lambda: False)()) and os.environ.get("TERM") != "dumb"


@dataclass
class _ProgressState:
    active: bool = False
    text: str = ""
    frame_index: int = 0


_STATE = _ProgressState()


def _clear_active_line() -> None:
    if not _STATE.active or not _should_use_live_progress():
        return
    sys.stdout.write("\r\033[2K")
    sys.stdout.flush()


def _render_active_line() -> None:
    if not _STATE.active or not _should_use_live_progress():
        return
    sys.stdout.write(f"\r\033[2K{_STATE.text}")
    sys.stdout.flush()


def should_report_progress(done: int, total: int, step_percent: int = 5) -> bool:
    if total <= 0:
        return False
    if done <= 1 or done >= total:
        return True
    interval = max(1, math.ceil(total * step_percent / 100))
    return done % interval == 0


def print_progress(done: int, total: int, label: str = "") -> None:
    if not _should_use_live_progress():
        print(format_progress(done, total, label), flush=True)
        return

    _STATE.frame_index += 1
    _STATE.text = _format_live_progress(done, total, label, _STATE.frame_index)
    _STATE.active = True
    _render_active_line()
    if done >= total:
        sys.stdout.write("\n")
        sys.stdout.flush()
        _STATE.active = False
        _STATE.text = ""


def log_line(message: str = "") -> None:
    if not _should_use_live_progress():
        print(message, flush=True)
        return

    was_active = _STATE.active
    saved_text = _STATE.text
    _clear_active_line()
    print(message, flush=True)
    if was_active:
        _STATE.text = saved_text
        _STATE.active = True
        _render_active_line()


def suspend_progress() -> None:
    _clear_active_line()
    _STATE.active = False
