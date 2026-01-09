import argparse
import subprocess
from collections import Counter
from pathlib import Path

def run_prog(py_file: Path, stdin_text: str, timeout_s: float = 2.0) -> str:
    p = subprocess.run(
        ["python", str(py_file)],
        input=stdin_text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_s,
    )
    if p.returncode != 0:
        raise RuntimeError(f"Program failed: {py_file}\n{p.stderr.decode('utf-8', errors='ignore')}")
    return p.stdout.decode("utf-8", errors="ignore").strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--put", required=True, help="Path to put.py")
    ap.add_argument("--variants", required=True, help="Dir contains variant_*.py")
    ap.add_argument("--tests", required=True, help="Dir contains test_*.in")
    ap.add_argument("--out", required=True, help="Output dir for bug-triggering tcases (.in/.out)")
    args = ap.parse_args()

    put = Path(args.put)
    variants_dir = Path(args.variants)
    tests_dir = Path(args.tests)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    variants = sorted(variants_dir.glob("variant_*.py"))
    tests = sorted(tests_dir.glob("test_*.in"))
    if not variants:
        raise RuntimeError("No variants found.")
    if not tests:
        raise RuntimeError("No tests found.")

    saved = 0
    for idx, tfile in enumerate(tests):
        inp = tfile.read_text(encoding="utf-8")
        try:
            put_out = run_prog(put, inp)
        except Exception as e:
            print(f"[SKIP] PUT crash on {tfile.name}: {e}")
            continue

        outs = []
        who = []
        for v in variants:
            try:
                v_out = run_prog(v, inp)
            except Exception:
                continue
            outs.append(v_out)
            who.append(v.name)

        if not outs:
            continue

        # 如果大家都和 PUT 一样，就没有“差异”
        if all(o == put_out for o in outs):
            continue

        # 多数投票 oracle（基于变体输出）
        oracle, occ = Counter(outs).most_common(1)[0]

        case_id = f"case_{idx:04d}"
        (out_dir / f"{case_id}.in").write_text(inp, encoding="utf-8")
        (out_dir / f"{case_id}.out").write_text(oracle + "\n", encoding="utf-8")
        saved += 1
        print(f"[FOUND] {case_id}: oracle={oracle!r} votes={occ}/{len(outs)} PUT={put_out!r}")

    print(f"[DONE] saved {saved} bug-triggering cases into {out_dir}")

if __name__ == "__main__":
    main()