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
        py, ROOT_DIR+"/LLM_Gen/variant_generator.py",
         "--template", ROOT_DIR+"/PromptTemplates/genprog_dfp",
        "--lang","{}".format(lang),#py/cpp
        "--spec", ROOT_DIR+"/data/spec.txt",
        "--put", ROOT_DIR+"/data/puts_{}/put.{}".format(lang,lang),
        "--out", ROOT_DIR+"/outputs/variants/{}".format(lang),
        "--k", "50",#生成程序变体数量
          ])