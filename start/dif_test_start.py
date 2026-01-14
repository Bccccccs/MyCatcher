import py
import sys
import subprocess

from pathlib import Path

CUR_DIR = Path(__file__).resolve().parent          # 当前脚本所在目录
ROOT_DIR = str(CUR_DIR.parent)# 上一级目录
def run(cmd):
    print("\n>>>", " ".join(cmd))
    subprocess.check_call(cmd)
py = sys.executable  # 保证用当前 venv 的 python
lang="py"
run([
    py, ROOT_DIR+"/LLM_Gen/differential_testing.py",
    "--lang", "{}".format(lang),
    "--put", ROOT_DIR+"/data/puts_{}/put.{}".format(lang, lang),
    "--variants",ROOT_DIR+ "/outputs/variants/{}".format(lang) ,
    "--tests", ROOT_DIR+"/outputs/inputs",
    "--out", ROOT_DIR+"/outputs/tcases/{}".format(lang),
])