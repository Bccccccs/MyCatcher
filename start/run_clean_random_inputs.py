import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def resolve_path(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (root / p).resolve()


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


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Clean only generated random input files under outputs/inputs."
    )
    ap.add_argument("--inputs-root", default="outputs/inputs")
    args = ap.parse_args()

    inputs_root = resolve_path(ROOT, args.inputs_root)

    print(f">>> Cleaning random inputs under {inputs_root}")

    if not inputs_root.exists():
        print(f"[SKIP] inputs root not found: {inputs_root}")
        return

    removed_files, removed_dirs = clean_dir_contents(inputs_root)
    print(
        f">>> Clean finished. Removed directories: {removed_dirs}, removed files: {removed_files}"
    )


if __name__ == "__main__":
    main()
