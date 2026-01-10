import py
import sys
import subprocess


def run(cmd):
    print("\n>>>", " ".join(cmd))
    subprocess.check_call(cmd)
py = sys.executable  # 保证用当前 venv 的 python
lang="cpp"
run([
    py, "input_generator.py",
    "--spec", "data/spec.txt",
    "--put", "data/puts_py/put.py",
    "--out", "outputs/inputs",
    "--num", "5",
    "--template", "PromptTemplates/geninput_direct",
])