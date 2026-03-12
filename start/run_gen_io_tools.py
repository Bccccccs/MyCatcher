import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print("\n>>>", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True, cwd=str(cwd))


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    py = sys.executable

    # 1) generate input generator next to each spec.txt
    run([
        py, str(root / "start" / "run_gen_generator.py"),
        "--batch",
    ], cwd=root)

    # 2) generate checker (output validator) next to each spec.txt
    run([
        py, str(root / "start" / "run_checker_gen.py"),
    ], cwd=root)


if __name__ == "__main__":
    main()
