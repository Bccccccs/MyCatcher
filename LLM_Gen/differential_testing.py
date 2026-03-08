import argparse
import hashlib
import subprocess
import sys
from collections import Counter
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def normalize_output(s: str) -> str:
    lines = [line.strip() for line in s.splitlines() if line.strip()]
    return lines[-1] if lines else ""
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
    return normalize_output(p.stdout.decode("utf-8", errors="ignore"))

def compile_cpp(src: Path, build_dir: Path) -> Path:
    build_dir.mkdir(parents=True, exist_ok=True)

    h = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
    exe = build_dir / f"{src.stem}_{h}"

    if exe.exists():
        return exe

    cmd = ["g++-15", "-std=c++17", "-O2", "-pipe", str(src), "-o", str(exe)]
    print("Compile:", " ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.returncode != 0:
        print("Compile error:", p.stderr.decode())
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
    return normalize_output(p.stdout.decode("utf-8", errors="ignore"))

def run_program(path: Path, stdin_text: str, lang: str, build_dir: Path, timeout: float) -> str:
    if lang == "py":
        return run_python(path, stdin_text, timeout)
    if lang == "cpp":
        return run_cpp(path, stdin_text, build_dir, timeout)
    raise ValueError(f"Unsupported lang: {lang}")


def main():
    parser = argparse.ArgumentParser(description="Differential testing (Python / C++)")
    parser.add_argument("--lang", choices=["py", "cpp"], default="py")
    parser.add_argument("--put", required=True)
    parser.add_argument("--variants", required=True)
    parser.add_argument("--tests", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--min_votes", type=int, default=None)
    parser.add_argument("--variant_mode", choices=["my", "trickybugs"], default="my")
    args = parser.parse_args()

    put = Path(args.put)
    variants_dir = Path(args.variants)
    tests_dir = Path(args.tests)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    build_dir = Path(__file__).resolve().parent.parent / "build" / "cpp_bin"
    ext = ".cpp" if args.lang == "cpp" else ".py"

    if args.variant_mode == "my":
        variants = sorted(variants_dir.glob(f"variant_*{ext}"))
    else:
        variants = sorted(variants_dir.glob(f"*_parsed{ext}"))

    tests = sorted(tests_dir.glob("*.in"))

    if not variants:
        raise RuntimeError(f"No variants found: {variants_dir}")
    if not tests:
        raise RuntimeError(f"No tests found: {tests_dir}")

    min_votes = args.min_votes or (len(variants) // 2 + 1)
    saved = 0
    variant_fail_counts = Counter()
    vote_records = []

    for idx, test_file in enumerate(tests, 1):
        inp = read_text(test_file)

        outs = []
        for vidx, v in enumerate(variants):
            try:
                o = run_program(v, inp, args.lang, build_dir, args.timeout)
                outs.append(o)
            except Exception as e:
                variant_fail_counts[v.name] += 1
                continue

        if not outs:
            vote_records.append({
                "test": test_file.name,
                "status": "NO_VARIANT_OUTPUT",
                "oracle": "",
                "votes": 0,
                "variant_total": len(variants),
                "put_out": "",
                "saved_case": "",
            })
            continue

        counter = Counter(outs)
        oracle, votes = counter.most_common(1)[0]
        if votes < min_votes:
            vote_records.append({
                "test": test_file.name,
                "status": "NO_MAJORITY",
                "oracle": oracle,
                "votes": votes,
                "variant_total": len(variants),
                "put_out": "",
                "saved_case": "",
            })
            continue

        try:
            put_out = run_program(put, inp, args.lang, build_dir, args.timeout)
        except Exception as e:
            vote_records.append({
                "test": test_file.name,
                "status": "PUT_FAIL",
                "oracle": oracle,
                "votes": votes,
                "variant_total": len(variants),
                "put_out": "",
                "saved_case": "",
            })
            continue

        if put_out != oracle:
            case_prefix = out_dir / f"case_{idx:04d}"
            case_prefix.with_suffix(".in").write_text(inp, encoding="utf-8")
            case_prefix.with_suffix(".oracle").write_text(oracle, encoding="utf-8")
            case_prefix.with_suffix(".put").write_text(put_out, encoding="utf-8")
            saved += 1
            vote_records.append({
                "test": test_file.name,
                "status": "FOUND",
                "oracle": oracle,
                "votes": votes,
                "variant_total": len(variants),
                "put_out": put_out,
                "saved_case": case_prefix.name,
            })
            continue

        vote_records.append({
            "test": test_file.name,
            "status": "AGREE",
            "oracle": oracle,
            "votes": votes,
            "variant_total": len(variants),
            "put_out": put_out,
            "saved_case": "",
        })

    for rec in vote_records:
        line = (
            f"[VOTE] {rec['test']} status={rec['status']} "
            f"votes={rec['votes']}/{rec['variant_total']}"
        )
        if rec["oracle"] != "":
            line += f" oracle='{rec['oracle']}'"
        if rec["put_out"] != "":
            line += f" put='{rec['put_out']}'"
        if rec["saved_case"] != "":
            line += f" case={rec['saved_case']}"
        print(line)

    if variant_fail_counts:
        print("[VARIANT_FAIL_SUMMARY]")
        for name, cnt in sorted(variant_fail_counts.items()):
            print(f"  {name}: {cnt}")

    print(f"[DONE] saved {saved} bug-triggering cases into {out_dir}")


if __name__ == "__main__":
    main()
