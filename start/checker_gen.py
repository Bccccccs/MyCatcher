import subprocess
import sys
from pathlib import Path


def main():
    # 项目根目录（start 的上一级）
    ROOT = Path(__file__).resolve().parent.parent

    python = sys.executable  # 当前虚拟环境的 python

    cmd = [
        python,
        str(ROOT / "LLM_Gen" / "checker_generator.py"),
        "--spec", str(ROOT / "data" / "spec.txt"),
        "--template", "geninput_inspector",
        "--out", str(ROOT / "outputs" / "checker" / "check_input.py"),
        "--model", "deepseek-chat",
    ]

    print("[INFO] Generating input checker via LLM...")
    subprocess.check_call(cmd)
    print("[DONE] Checker generated at outputs/checker/check_input.py")


if __name__ == "__main__":
    main()