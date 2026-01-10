import py
import sys
import subprocess


def run(cmd):
    print("\n>>>", " ".join(cmd))
    subprocess.check_call(cmd)
py = sys.executable  # 保证用当前 venv 的 python
lang="cpp"
run([
        py, "variant_generator.py",
         "--template", "PromptTemplates/genprog_dfp",
        "--lang","{}".format(lang),#py/cpp
        "--spec", "data/spec.txt",
        "--put", "data/puts_{}/put.{}".format(lang,lang),
        "--out", "outputs/variants/{}".format(lang),
        "--k", "10",#生成程序变体数量
          ])