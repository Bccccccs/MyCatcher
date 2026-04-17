import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print("\n>>>", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True, cwd=str(cwd))


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    py = sys.executable

    # Compatibility wrapper:
    # keep this script as a short alias for generating both tools in batch.
    run([
        py, str(root / "start" / "run_gen_tools.py"),
        "--tool", "both",
    ], cwd=root)


if __name__ == "__main__":
    main()
