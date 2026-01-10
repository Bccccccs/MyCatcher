import subprocess
import sys


def run(cmd):
    print("\n>>>", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    py = sys.executable  # 保证用当前 venv 的 python

    # 1. 生成程序变体
    run([
        py, "variant_generator.py",
        "--template", "PromptTemplates/genprog_tc",
        "--spec", "data/spec.txt",
        "--put", "data/puts_py/put.py",
        "--out", "outputs/variants",
        "--k", "5",#生成程序变体数量
           ])

    # 2. 生成测试输入
    run([
        py, "input_generator.py",
        "--spec", "data/spec.txt",
        "--put", "data/puts_py/put.py",
        "--out", "outputs/inputs",
        "--num", "20",
        "--template", "PromptTemplates/geninput_direct",
    ])

    # 3. 差分测试
    run([
        py, "differential_testing.py",
        "--put", "data/puts_py/put.py",
        "--variants", "outputs/variants",
        "--tests", "outputs/inputs",
        "--out", "outputs/tcases",
    ])

    print("\n=== PIPELINE DONE ===")


if __name__ == "__main__":
    main()