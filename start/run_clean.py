import shutil
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent

# 需要清理的目录（只清理内容，不删目录本身）
DIRS_TO_CLEAN = [
    ROOT / "outputs" / "inputs",
    ROOT / "outputs" / "tcases",
]

# 题目目录中由脚本生成的工具文件（可安全重建）
GENERATED_TOOL_FILES = {"input_gen.py", "check_input.py"}

# 每题 PUT 根目录（清理工具文件，但不动 PUT/sol/变体程序）
PUT_DATASET_ROOTS = [
    ROOT / "Datasets" / "TrickyBugs" / "PUT_cpp",
    ROOT / "Datasets" / "TrickyBugs" / "PUT_python",
]

# 需要整目录删除的缓存
CACHE_DIRS = [
    ROOT / "__pycache__",
    ROOT / ".pytest_cache",
    ROOT / ".ipynb_checkpoints",
    ROOT / "Analysis" / ".ipynb_checkpoints",

]

def clean_dir_contents(path: Path):
    if not path.exists():
        return
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        else:
            item.unlink(missing_ok=True)

def clean_all():
    print(">>> Cleaning inputs + per-problem generator/checker files (keeping PUTs/variants)...")

    # 清理 outputs 下内容
    for d in DIRS_TO_CLEAN:
        if d.exists():
            print(f" - Cleaning {d}")
            clean_dir_contents(d)

    # 清理每个题目目录下生成的 input generator / checker
    for dataset_root in PUT_DATASET_ROOTS:
        if not dataset_root.exists():
            continue
        for program_dir in dataset_root.iterdir():
            if not program_dir.is_dir():
                continue
            for name in GENERATED_TOOL_FILES:
                p = program_dir / name
                if p.exists():
                    print(f" - Removing generated tool {p}")
                    p.unlink(missing_ok=True)

    # 清理缓存目录
    for d in CACHE_DIRS:
        if d.exists():
            print(f" - Removing cache {d}")
            shutil.rmtree(d, ignore_errors=True)

    # 清理所有 __pycache__
    for d in ROOT.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)

    print(">>> Clean finished.")

if __name__ == "__main__":
    clean_all()
