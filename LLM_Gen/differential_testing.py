import argparse
import hashlib
import subprocess
import sys
from collections import Counter
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# -------------------------
# Running programs
# -------------------------

def run_python(py_file: Path, stdin_text: str, timeout: float) -> str:
    p = subprocess.run(
        [sys.executable, str(py_file)],
        input=stdin_text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if p.returncode != 0:
        raise RuntimeError(
            f"Program failed: {py_file}\n"
            f"{p.stderr.decode('utf-8', errors='ignore')}"
        )
    return p.stdout.decode("utf-8", errors="ignore").strip()


def compile_cpp(src: Path, build_dir: Path) -> Path:
    """
    Compile C++ source with caching by content hash.
    """
    build_dir.mkdir(parents=True, exist_ok=True)

    h = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
    exe = build_dir / f"{src.stem}_{h}"

    if exe.exists():
        return exe

    cmd = ["g++", "-std=c++17", "-O2", "-pipe", str(src), "-o", str(exe)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.returncode != 0:
        raise RuntimeError(
            f"C++ compile failed: {src}\n"
            f"{p.stderr.decode('utf-8', errors='ignore')}"
        )
    return exe


def run_cpp(src: Path, stdin_text: str, build_dir: Path, timeout: float) -> str:
    exe = compile_cpp(src, build_dir)
    p = subprocess.run(
        [str(exe)],
        input=stdin_text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if p.returncode != 0:
        raise RuntimeError(
            f"Program failed: {src}\n"
            f"{p.stderr.decode('utf-8', errors='ignore')}"
        )
    return p.stdout.decode("utf-8", errors="ignore").strip()


def run_program(path: Path, stdin_text: str, lang: str, build_dir: Path, timeout: float) -> str:
    if lang == "py":
        return run_python(path, stdin_text, timeout)
    if lang == "cpp":
        return run_cpp(path, stdin_text, build_dir, timeout)
    raise ValueError(f"Unsupported lang: {lang}")


# -------------------------
# Main
# -------------------------

def main():
    parser = argparse.ArgumentParser(description="Differential testing (Python / C++)")
    parser.add_argument("--lang", choices=["py", "cpp"], default="py", help="Language of PUT/variants")
    parser.add_argument("--put", required=True, help="Path to PUT (.py or .cpp)")
    parser.add_argument("--variants", required=True, help="Directory of variants")
    parser.add_argument("--tests", required=True, help="Directory of test inputs (*.in)")
    parser.add_argument("--out", required=True, help="Output directory for bug-triggering cases")
    parser.add_argument("--timeout", type=float, default=2.0, help="Execution timeout (seconds)")
    parser.add_argument(
        "--min_votes",
        type=int,
        default=None,
        help="Minimum votes for oracle acceptance. Default: majority (n//2+1).",
    )

    args = parser.parse_args()

    put = Path(args.put)
    variants_dir = Path(args.variants)
    tests_dir = Path(args.tests)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    build_dir = Path("../build") / "cpp_bin"

    ext = ".cpp" if args.lang == "cpp" else ".py"
    variants = sorted(variants_dir.glob(f"variant_*{ext}"))
    tests = sorted(tests_dir.glob("*.in"))

    if not variants:
        raise RuntimeError(f"No variants found: {variants_dir} (expected variant_*{ext})")
    if not tests:
        raise RuntimeError(f"No tests found: {tests_dir} (expected *.in)")

    min_votes = args.min_votes or (len(variants) // 2 + 1)
    saved = 0

    for idx, test_file in enumerate(tests):
        inp = read_text(test_file)

        # 1) run variants to get oracle (majority vote)
        outs = []
        for v in variants:
            try:
                o = run_program(v, inp, args.lang, build_dir, args.timeout)
                outs.append(o)
            except Exception as e:
                print(f"[DBG] variant failed: {v.name} -> {e}")
                # Variant crash/timeout -> ignore for voting
                continue

        if not outs:
            continue

        counter = Counter(outs)
        oracle, votes = counter.most_common(1)[0]
        if votes < min_votes:
            continue

        # 2) run PUT
        try:
            put_out = run_program(put, inp, args.lang, build_dir, args.timeout)
        except Exception:
            print(f"[SKIP] PUT crash on {test_file.name}")
            continue

        # 3) compare
        if put_out != oracle:
            case_prefix = out_dir / f"case_{idx:04d}"
            case_prefix.with_suffix(".in").write_text(inp, encoding="utf-8")
            case_prefix.with_suffix(".oracle").write_text(oracle, encoding="utf-8")
            case_prefix.with_suffix(".put").write_text(put_out, encoding="utf-8")
            print(
                f"[FOUND] {case_prefix.name}: oracle='{oracle}' votes={votes}/{len(variants)} PUT='{put_out}'"
            )
            saved += 1

    print(f"[DONE] saved {saved} bug-triggering cases into {out_dir}")


if __name__ == "__main__":
    main()