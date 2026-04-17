import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIRS = [
    ROOT / "outputs" / "inputs",
    ROOT / "outputs" / "tcases",
]

GENERATED_TOOL_FILES = {"input_gen.py", "check_input.py"}

PUT_DATASET_ROOTS = [
    ROOT / "Datasets" / "TrickyBugs" / "PUT_cpp",
    ROOT / "Datasets" / "TrickyBugs" / "PUT_python",
]

CACHE_DIRS = [
    ROOT / "__pycache__",
    ROOT / ".pytest_cache",
    ROOT / ".ipynb_checkpoints",
    ROOT / "Analysis" / ".ipynb_checkpoints",
]

SCOPE_HELP = """
How to use:
  1. Only clean generated inputs:
     python3 start/run_clean.py --scope inputs

  2. Clean generated inputs + differential-testing outputs:
     python3 start/run_clean.py --scope outputs

  3. Full cleanup for a fresh experiment run:
     python3 start/run_clean.py --scope all

Scope meanings:
  - inputs: clean outputs/inputs only
  - outputs: clean outputs/inputs and outputs/tcases
  - all: outputs + generated tool files + cache directories
""".strip()


def clean_dir_contents(path: Path) -> tuple[int, int]:
    removed_files = 0
    removed_dirs = 0
    if not path.exists():
        return removed_files, removed_dirs
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
            removed_dirs += 1
        else:
            item.unlink(missing_ok=True)
            removed_files += 1
    return removed_files, removed_dirs


def clean_outputs(inputs_only: bool) -> tuple[int, int]:
    removed_files = 0
    removed_dirs = 0
    dirs_to_clean = [ROOT / "outputs" / "inputs"] if inputs_only else OUTPUT_DIRS
    for target in dirs_to_clean:
        if not target.exists():
            continue
        print(f" - Cleaning {target}")
        files, dirs = clean_dir_contents(target)
        removed_files += files
        removed_dirs += dirs
    return removed_files, removed_dirs


def clean_generated_tools() -> int:
    removed = 0
    for dataset_root in PUT_DATASET_ROOTS:
        if not dataset_root.exists():
            continue
        for program_dir in dataset_root.iterdir():
            if not program_dir.is_dir():
                continue
            for name in GENERATED_TOOL_FILES:
                p = program_dir / name
                if p.exists():
                    print(f" - Removing generated tool {p}")
                    p.unlink(missing_ok=True)
                    removed += 1
    return removed


def clean_caches() -> int:
    removed = 0
    for target in CACHE_DIRS:
        if target.exists():
            print(f" - Removing cache {target}")
            shutil.rmtree(target, ignore_errors=True)
            removed += 1

    for target in ROOT.rglob("__pycache__"):
        shutil.rmtree(target, ignore_errors=True)
        removed += 1
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean generated experiment outputs and caches.",
        epilog=SCOPE_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--scope",
        choices=["inputs", "outputs", "all"],
        default="all",
        help="Choose how much to clean. Default: all",
    )
    args = parser.parse_args()

    print(f">>> Cleaning scope={args.scope}")

    removed_files = 0
    removed_dirs = 0
    removed_tools = 0
    removed_caches = 0

    if args.scope == "inputs":
        removed_files, removed_dirs = clean_outputs(inputs_only=True)
    elif args.scope == "outputs":
        removed_files, removed_dirs = clean_outputs(inputs_only=False)
    else:
        removed_files, removed_dirs = clean_outputs(inputs_only=False)
        removed_tools = clean_generated_tools()
        removed_caches = clean_caches()

    print(
        f">>> Clean finished. Removed files: {removed_files}, removed directories: {removed_dirs}, "
        f"removed generated tools: {removed_tools}, removed cache dirs: {removed_caches}"
    )


if __name__ == "__main__":
    main()
