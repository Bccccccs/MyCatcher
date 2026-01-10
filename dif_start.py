import py
import sys
import subprocess


def run(cmd):
    print("\n>>>", " ".join(cmd))
    subprocess.check_call(cmd)
py = sys.executable  # 保证用当前 venv 的 python
lang="cpp"
run([
    py, "differential_testing.py",
    "--lang", "{}".format(lang),
    "--put", "data/puts_{}/put.{}".format(lang, lang),
    "--variants", "outputs/variants/{}".format(lang) ,
    "--tests", "outputs/inputs",
    "--out", "outputs/tcases/{}".format(lang),
])