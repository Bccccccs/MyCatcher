import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


HELP_TEXT = """
How to use:
  1. Clean all shared generated inputs:
     python3 start/run_clean_inputs.py

  2. Clean shared inputs for one problem only:
     python3 start/run_clean_inputs.py --pid p02577

  3. Clean CHAT input artifacts too:
     python3 start/run_clean_inputs.py --target all

  4. Preview what would be removed:
     python3 start/run_clean_inputs.py --target all --dry-run

Target meanings:
  - shared: clean outputs/inputs and optional checker logs only
  - chat: clean CHAT input-generation artifacts only
  - all: clean both shared and CHAT input artifacts
""".strip()


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (ROOT / path).resolve()


def remove_path(path: Path, dry_run: bool) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    if path.is_dir():
        if dry_run:
            print(f"[DRY] remove dir {path}")
        else:
            shutil.rmtree(path, ignore_errors=True)
            print(f"[DEL] dir {path}")
        return 0, 1
    if dry_run:
        print(f"[DRY] remove file {path}")
    else:
        path.unlink(missing_ok=True)
        print(f"[DEL] file {path}")
    return 1, 0


def clean_shared_inputs(
    *,
    inputs_root: Path,
    pid: str | None,
    checker_log_root: Path | None,
    dry_run: bool,
) -> tuple[int, int]:
    removed_files = 0
    removed_dirs = 0

    targets = [inputs_root / pid] if pid else [path for path in sorted(inputs_root.iterdir())] if inputs_root.exists() else []
    for target in targets:
        files, dirs = remove_path(target, dry_run)
        removed_files += files
        removed_dirs += dirs

    if checker_log_root is not None:
        if pid:
            patterns = [
                checker_log_root / f"{pid}.txt",
                checker_log_root / f"{pid}.log",
                checker_log_root / pid,
            ]
            for target in patterns:
                files, dirs = remove_path(target, dry_run)
                removed_files += files
                removed_dirs += dirs
        else:
            files, dirs = remove_path(checker_log_root, dry_run)
            removed_files += files
            removed_dirs += dirs

    return removed_files, removed_dirs


def clean_chat_inputs(
    *,
    chat_root: Path,
    pid: str | None,
    dry_run: bool,
) -> tuple[int, int]:
    removed_files = 0
    removed_dirs = 0

    artifact_names = ["raw_llm_output", "normalized_tests", "invalid_tests", "executions"]
    problem_dirs = [chat_root / pid] if pid else [path for path in sorted(chat_root.iterdir()) if path.is_dir()] if chat_root.exists() else []

    for problem_dir in problem_dirs:
        for name in artifact_names:
            files, dirs = remove_path(problem_dir / name, dry_run)
            removed_files += files
            removed_dirs += dirs

    if not pid:
        for name in ("summary.csv", "summary.json", "summary.txt"):
            files, dirs = remove_path(chat_root / name, dry_run)
            removed_files += files
            removed_dirs += dirs

    return removed_files, removed_dirs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean generated input artifacts without touching non-input experiment assets.",
        epilog=HELP_TEXT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--target", choices=["shared", "chat", "all"], default="shared")
    parser.add_argument("--pid", default=None, help="Only clean one problem id, e.g. p02577")
    parser.add_argument("--inputs-root", default="outputs/inputs", help="Shared generated input root")
    parser.add_argument("--chat-root", default="outputs/chat", help="CHAT baseline output root")
    parser.add_argument(
        "--checker-log-root",
        default="outputs/checker_logs",
        help="Checker log root to clean together with shared inputs",
    )
    parser.add_argument("--skip-checker-logs", action="store_true", help="Do not remove checker logs")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without deleting anything")
    args = parser.parse_args()

    inputs_root = resolve_path(args.inputs_root)
    chat_root = resolve_path(args.chat_root)
    checker_log_root = None if args.skip_checker_logs else resolve_path(args.checker_log_root)

    removed_files = 0
    removed_dirs = 0

    if args.target in {"shared", "all"}:
        files, dirs = clean_shared_inputs(
            inputs_root=inputs_root,
            pid=args.pid,
            checker_log_root=checker_log_root,
            dry_run=args.dry_run,
        )
        removed_files += files
        removed_dirs += dirs

    if args.target in {"chat", "all"}:
        files, dirs = clean_chat_inputs(
            chat_root=chat_root,
            pid=args.pid,
            dry_run=args.dry_run,
        )
        removed_files += files
        removed_dirs += dirs

    print(
        f"[DONE] target={args.target} pid={args.pid or 'ALL'} "
        f"removed_files={removed_files} removed_dirs={removed_dirs} dry_run={args.dry_run}"
    )


if __name__ == "__main__":
    main()
