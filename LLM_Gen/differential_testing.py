import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
import csv
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

COMPILE_CACHE = {}
CPP_COMPILER = None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def format_report_line(rec: dict[str, object]) -> str:
    line = (
        f"[VOTE] {rec['test']} status={rec['status']} "
        f"votes={rec['votes']}/{rec['variant_total']}"
    )
    if rec.get("variant_outputs") is not None:
        line += f" variant_outputs={rec['variant_outputs']}"
    if rec.get("required_votes") is not None:
        line += f" required_votes={rec['required_votes']}"
    if rec["oracle"] != "":
        line += f" oracle='{rec['oracle']}'"
    if rec["put_out"] != "":
        line += f" put='{rec['put_out']}'"
    if rec["saved_case"] != "":
        line += f" case={rec['saved_case']}"
    line += f" predicted_bug={str(rec['predicted_bug']).lower()}"
    line += f" is_valid={str(rec['is_valid']).lower()}"
    if rec["canonical_out"] != "":
        line += f" canonical='{rec['canonical_out']}'"
    if rec["canonical_error"] != "":
        line += f" canonical_error='{rec['canonical_error']}'"
    if rec["oracle_correct"] is not None:
        line += f" oracle_correct={str(rec['oracle_correct']).lower()}"
    if rec["put_wrong"] is not None:
        line += f" put_wrong={str(rec['put_wrong']).lower()}"
    line += f" final_label={rec['final_label']}"
    return line


def write_txt_report(
    report_path: Path,
    put: Path,
    canonical: Path | None,
    variants: list[Path],
    tests: list[Path],
    fixed_min_votes: int,
    saved: int,
    vote_records: list[dict[str, object]],
    variant_fail_counts: Counter,
    variant_prefilter_stats: list[dict[str, object]],
    variant_prefilter_messages: list[str],
) -> None:
    status_counts = Counter(rec["status"] for rec in vote_records)
    tp_count = sum(1 for rec in vote_records if rec["final_label"] == "TP")
    fp_count = sum(1 for rec in vote_records if rec["final_label"] == "FP")
    precision = ""
    if tp_count + fp_count > 0:
        precision = f"{tp_count / (tp_count + fp_count):.6f}"
    lines = [
        "Differential Testing Report",
        f"PUT: {put}",
        f"Canonical: {canonical if canonical else ''}",
        f"Variants dir size: {len(variants)}",
        f"Tests dir size: {len(tests)}",
        "Vote mode: fixed",
        f"Min votes: {fixed_min_votes}",
        "",
        "Summary",
        f"saved={saved}",
        f"agree={status_counts.get('AGREE', 0)}",
        f"found={status_counts.get('FOUND', 0)}",
        f"no_majority={status_counts.get('NO_MAJORITY', 0)}",
        f"no_variant_output={status_counts.get('NO_VARIANT_OUTPUT', 0)}",
        f"put_fail={status_counts.get('PUT_FAIL', 0)}",
        f"tp_count={tp_count}",
        f"fp_count={fp_count}",
        f"oracle_wrong_count={sum(1 for rec in vote_records if rec['oracle_correct'] is False)}",
        f"canonical_fail_count={sum(1 for rec in vote_records if rec['final_label'] == 'CANONICAL_FAIL')}",
        f"precision={precision}",
        "",
        "Details",
    ]

    for rec in vote_records:
        lines.append(format_report_line(rec))

    if variant_fail_counts:
        lines.extend(["", "Variant Fail Summary"])
        for name, cnt in sorted(variant_fail_counts.items()):
            lines.append(f"{name}: {cnt}")

    if variant_prefilter_messages or variant_prefilter_stats:
        lines.extend(["", "Variant Prefilter"])
        for message in variant_prefilter_messages:
            lines.append(message)
        for row in variant_prefilter_stats:
            lines.append(
                f"{row['name']}: kept={str(row['kept']).lower()} "
                f"sample_total={row['sample_total']} run_count={row['run_count']} "
                f"fail_count={row['fail_count']} mismatch_count={row['mismatch_count']} "
                f"fail_rate={row['fail_rate']:.6f} mismatch_rate={row['mismatch_rate']:.6f}"
            )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_summary(
    put: Path,
    canonical: Path | None,
    variants: list[Path],
    tests: list[Path],
    fixed_min_votes: int,
    saved: int,
    vote_records: list[dict[str, object]],
    variant_fail_counts: Counter,
    report_path: Path,
    original_variant_count: int,
    variant_prefilter_stats: list[dict[str, object]],
    variant_prefilter_messages: list[str],
) -> dict[str, object]:
    status_counts = Counter(rec["status"] for rec in vote_records)
    tp_count = sum(1 for rec in vote_records if rec["final_label"] == "TP")
    fp_count = sum(1 for rec in vote_records if rec["final_label"] == "FP")
    oracle_wrong_count = sum(1 for rec in vote_records if rec["oracle_correct"] is False)
    canonical_fail_count = sum(1 for rec in vote_records if rec["final_label"] == "CANONICAL_FAIL")
    predicted_bug_count = sum(1 for rec in vote_records if rec["predicted_bug"])
    precision = None
    if tp_count + fp_count > 0:
        precision = tp_count / (tp_count + fp_count)
    return {
        "put": str(put),
        "canonical": str(canonical) if canonical else "",
        "variants_dir_size": original_variant_count,
        "variants_used": len(variants),
        "tests_dir_size": len(tests),
        "vote_mode": "fixed",
        "min_votes": fixed_min_votes,
        "fixed_min_votes": fixed_min_votes,
        "saved": saved,
        "agree": status_counts.get("AGREE", 0),
        "found": status_counts.get("FOUND", 0),
        "no_majority": status_counts.get("NO_MAJORITY", 0),
        "no_variant_output": status_counts.get("NO_VARIANT_OUTPUT", 0),
        "put_fail": status_counts.get("PUT_FAIL", 0),
        "predicted_bug_count": predicted_bug_count,
        "tp_count": tp_count,
        "fp_count": fp_count,
        "oracle_wrong_count": oracle_wrong_count,
        "canonical_fail_count": canonical_fail_count,
        "precision": precision,
        "report": str(report_path),
        "variant_fail_summary": dict(sorted(variant_fail_counts.items())),
        "variant_prefilter": {
            "enabled": bool(variant_prefilter_stats or variant_prefilter_messages),
            "messages": variant_prefilter_messages,
            "stats": [
                {
                    key: value
                    for key, value in row.items()
                    if key != "variant"
                }
                for row in variant_prefilter_stats
            ],
        },
    }


def write_summary_json(summary_path: Path, summary: dict[str, object]) -> None:
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_output(s: str) -> str:
    # Keep the full program answer while removing line-ending and trailing-space noise.
    lines = s.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized = [line.rstrip() for line in lines]
    while normalized and normalized[-1] == "":
        normalized.pop()
    return "\n".join(normalized)


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

def resolve_cpp_compiler() -> str:
    env_cxx = os.environ.get("CXX", "").strip()
    candidates = []
    if env_cxx:
        candidates.append(env_cxx)
    candidates.extend(["g++-15", "g++", "g++-12", "g++-11", "clang++"])

    for candidate in candidates:
        if shutil.which(candidate):
            return candidate
    raise RuntimeError(
        "No C++ compiler found. Tried CXX and common compiler names: "
        + ", ".join(candidates)
    )

def compile_cpp(src: Path, build_dir: Path) -> Path:
    global CPP_COMPILER
    src_key = str(src.resolve())
    cached = COMPILE_CACHE.get(src_key)
    if cached is not None:
        ok, payload = cached
        if ok:
            return payload
        raise RuntimeError(payload)

    build_dir.mkdir(parents=True, exist_ok=True)

    h = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
    exe = build_dir / f"{src.stem}_{h}"

    if exe.exists():
        COMPILE_CACHE[src_key] = (True, exe)
        return exe

    if CPP_COMPILER is None:
        CPP_COMPILER = resolve_cpp_compiler()

    cmd = [CPP_COMPILER, "-std=c++17", "-O2", "-pipe", str(src), "-o", str(exe)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.returncode != 0:
        err = (
            f"C++ compile failed: {src}\n"
            f"compiler: {CPP_COMPILER}\n"
            f"{p.stderr.decode('utf-8', errors='ignore')}"
        )
        COMPILE_CACHE[src_key] = (False, err)
        raise RuntimeError(err)
    COMPILE_CACHE[src_key] = (True, exe)
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


def run_canonical_on_input(
    canonical: Path | None,
    stdin_text: str,
    lang: str,
    build_dir: Path,
    timeout: float,
) -> tuple[str, str]:
    if canonical is None:
        return "", "canonical program not configured"
    try:
        return run_program(canonical, stdin_text, lang, build_dir, timeout), ""
    except Exception as exc:
        return "", str(exc).splitlines()[0]


def prefilter_variants(
    variants: list[Path],
    tests: list[Path],
    canonical: Path | None,
    lang: str,
    build_dir: Path,
    timeout: float,
    sample_size: int,
    max_fail_rate: float,
    max_mismatch_rate: float,
    min_keep: int,
) -> tuple[list[Path], list[dict[str, object]], list[str]]:
    if sample_size <= 0:
        return variants, [], []

    sample_tests = tests[:sample_size]
    canonical_by_test: dict[Path, str] = {}
    canonical_errors = 0
    for test_file in sample_tests:
        canonical_out, canonical_error = run_canonical_on_input(
            canonical=canonical,
            stdin_text=read_text(test_file),
            lang=lang,
            build_dir=build_dir,
            timeout=timeout,
        )
        if canonical_error:
            canonical_errors += 1
            continue
        canonical_by_test[test_file] = canonical_out

    if not canonical_by_test:
        return variants, [], [
            f"variant prefilter skipped: no canonical outputs from {len(sample_tests)} sample tests"
        ]

    stats: list[dict[str, object]] = []
    kept: list[Path] = []
    for variant in variants:
        run_count = 0
        fail_count = 0
        mismatch_count = 0
        for test_file, canonical_out in canonical_by_test.items():
            inp = read_text(test_file)
            try:
                out = run_program(variant, inp, lang, build_dir, timeout)
            except Exception:
                fail_count += 1
                continue
            run_count += 1
            if out != canonical_out:
                mismatch_count += 1

        total = len(canonical_by_test)
        fail_rate = fail_count / total
        mismatch_rate = mismatch_count / run_count if run_count else 1.0
        keep = fail_rate <= max_fail_rate and mismatch_rate <= max_mismatch_rate
        row = {
            "variant": variant,
            "name": variant.name,
            "sample_total": total,
            "run_count": run_count,
            "fail_count": fail_count,
            "mismatch_count": mismatch_count,
            "fail_rate": fail_rate,
            "mismatch_rate": mismatch_rate,
            "kept": keep,
        }
        stats.append(row)
        if keep:
            kept.append(variant)

    messages = [
        (
            "variant prefilter: "
            f"sample_tests={len(sample_tests)} usable={len(canonical_by_test)} "
            f"canonical_errors={canonical_errors} kept={len(kept)}/{len(variants)} "
            f"max_fail_rate={max_fail_rate:.3f} max_mismatch_rate={max_mismatch_rate:.3f}"
        )
    ]

    if len(kept) < min_keep:
        messages.append(
            f"variant prefilter fallback: kept {len(kept)} < min_keep {min_keep}; using all variants"
        )
        for row in stats:
            row["kept"] = True
        return variants, stats, messages

    return kept, stats, messages


def judge_tp_fp(record: dict[str, object]) -> str:
    if not record["is_valid"]:
        return "INVALID_INPUT"
    if record["canonical_error"]:
        return "CANONICAL_FAIL"
    if record["status"] == "PUT_FAIL":
        return "PUT_FAIL"
    if record["oracle"] == "":
        return "NO_ORACLE"
    if record["predicted_bug"] and record["oracle_correct"] is True and record["put_wrong"] is True:
        return "TP"
    if record["predicted_bug"] and record["oracle_correct"] is False:
        return "FP"
    return "NOT_FOUND"


def label_for_status(record: dict[str, object], status: str) -> str:
    candidate = dict(record)
    candidate["status"] = status
    if status not in {"FOUND", "AGREE"}:
        candidate["predicted_bug"] = False
    return judge_tp_fp(candidate)


def write_detail_csv(detail_csv_path: Path, vote_records: list[dict[str, object]], pid: str) -> None:
    fieldnames = [
        "pid",
        "test_name",
        "is_valid",
        "predicted_bug",
        "status",
        "oracle_output",
        "canonical_output",
        "put_output",
        "oracle_correct",
        "put_wrong",
        "final_label",
        "test",
        "votes",
        "variant_total",
        "variant_outputs",
        "required_votes",
        "oracle",
        "put_out",
        "canonical_out",
        "canonical_error",
        "saved_case",
    ]
    with detail_csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL,
            escapechar="\\",
        )
        writer.writeheader()
        for record in vote_records:
            row = {name: record.get(name, "") for name in fieldnames}
            row.update({
                "pid": pid,
                "test_name": record.get("test", ""),
                "oracle_output": record.get("oracle", ""),
                "canonical_output": record.get("canonical_out", ""),
                "put_output": record.get("put_out", ""),
            })
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Differential testing (Python / C++)")
    parser.add_argument("--lang", choices=["py", "cpp"], default="py")
    parser.add_argument("--put", required=True)
    parser.add_argument("--variants", required=True)
    parser.add_argument("--tests", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--canonical", default=None)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--fixed-min-votes", type=int, default=6, help="Fixed-vote threshold")
    parser.add_argument("--variant_mode", choices=["my", "trickybugs"], default="my")
    parser.add_argument("--prefilter-variants", action="store_true", help="Drop variants that fail or disagree with canonical on sample tests")
    parser.add_argument("--prefilter-sample-size", type=int, default=20, help="Number of input tests used for variant prefiltering")
    parser.add_argument("--prefilter-max-fail-rate", type=float, default=0.2, help="Maximum allowed prefilter runtime/compile fail rate")
    parser.add_argument("--prefilter-max-mismatch-rate", type=float, default=0.3, help="Maximum allowed mismatch rate against canonical among successful sample runs")
    parser.add_argument("--prefilter-min-keep", type=int, default=3, help="Fallback to all variants if fewer than this many variants pass prefilter")
    args = parser.parse_args()

    put = Path(args.put)
    canonical = Path(args.canonical) if args.canonical else None
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

    original_variant_count = len(variants)
    variant_prefilter_stats: list[dict[str, object]] = []
    variant_prefilter_messages: list[str] = []
    if args.prefilter_variants:
        variants, variant_prefilter_stats, variant_prefilter_messages = prefilter_variants(
            variants=variants,
            tests=tests,
            canonical=canonical,
            lang=args.lang,
            build_dir=build_dir,
            timeout=args.timeout,
            sample_size=args.prefilter_sample_size,
            max_fail_rate=args.prefilter_max_fail_rate,
            max_mismatch_rate=args.prefilter_max_mismatch_rate,
            min_keep=args.prefilter_min_keep,
        )
        for message in variant_prefilter_messages:
            print(f"[PREFILTER] {message}")

    fixed_min_votes = args.fixed_min_votes
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
                "is_valid": True,
                "predicted_bug": False,
                "oracle": "",
                "votes": 0,
                "variant_total": len(variants),
                "variant_outputs": 0,
                "required_votes": fixed_min_votes,
                "put_out": "",
                "canonical_out": "",
                "canonical_error": "",
                "oracle_correct": None,
                "put_wrong": None,
                "saved_case": "",
                "final_label": "",
            })
        else:
            counter = Counter(outs)
            oracle, votes = counter.most_common(1)[0]
            status = "PENDING" if votes >= fixed_min_votes else "NO_MAJORITY"
            should_run_put = status == "PENDING"
            if not should_run_put:
                vote_records.append({
                    "test": test_file.name,
                    "status": status,
                    "is_valid": True,
                    "predicted_bug": False,
                    "oracle": oracle,
                    "votes": votes,
                    "variant_total": len(variants),
                    "variant_outputs": len(outs),
                    "required_votes": fixed_min_votes,
                    "put_out": "",
                    "canonical_out": "",
                    "canonical_error": "",
                    "oracle_correct": None,
                    "put_wrong": None,
                    "saved_case": "",
                    "final_label": "",
                })
            else:
                try:
                    put_out = run_program(put, inp, args.lang, build_dir, args.timeout)
                except Exception as e:
                    status = "PUT_FAIL"
                    vote_records.append({
                        "test": test_file.name,
                        "status": status,
                        "is_valid": True,
                        "predicted_bug": False,
                        "oracle": oracle,
                        "votes": votes,
                        "variant_total": len(variants),
                        "variant_outputs": len(outs),
                        "required_votes": fixed_min_votes,
                        "put_out": "",
                        "canonical_out": "",
                        "canonical_error": "",
                        "oracle_correct": None,
                        "put_wrong": None,
                        "saved_case": "",
                        "final_label": "",
                    })
                else:
                    predicted_bug = put_out != oracle
                    saved_case = ""
                    status = "FOUND" if predicted_bug else "AGREE"
                    if status == "FOUND":
                        case_prefix = out_dir / f"case_{idx:04d}"
                        case_prefix.with_suffix(".in").write_text(inp, encoding="utf-8")
                        case_prefix.with_suffix(".oracle").write_text(oracle, encoding="utf-8")
                        case_prefix.with_suffix(".put").write_text(put_out, encoding="utf-8")
                        saved += 1
                        saved_case = case_prefix.name

                    vote_records.append({
                        "test": test_file.name,
                        "status": status,
                        "is_valid": True,
                        "predicted_bug": predicted_bug,
                        "oracle": oracle,
                        "votes": votes,
                        "variant_total": len(variants),
                        "variant_outputs": len(outs),
                        "required_votes": fixed_min_votes,
                        "put_out": put_out,
                        "canonical_out": "",
                        "canonical_error": "",
                        "oracle_correct": None,
                        "put_wrong": None,
                        "saved_case": saved_case,
                        "final_label": "",
                    })

        current_record = vote_records[-1]
        canonical_out, canonical_error = run_canonical_on_input(
            canonical=canonical,
            stdin_text=inp,
            lang=args.lang,
            build_dir=build_dir,
            timeout=args.timeout,
        )
        current_record["canonical_out"] = canonical_out
        current_record["canonical_error"] = canonical_error
        if not canonical_error:
            if current_record["oracle"] != "":
                current_record["oracle_correct"] = current_record["oracle"] == canonical_out
            if current_record["put_out"] != "":
                current_record["put_wrong"] = current_record["put_out"] != canonical_out
        current_record["final_label"] = judge_tp_fp(current_record)

    report_path = out_dir / "report.txt"
    detail_csv_path = out_dir / "detail.csv"
    write_txt_report(
        report_path=report_path,
        put=put,
        canonical=canonical,
        variants=variants,
        tests=tests,
        fixed_min_votes=fixed_min_votes,
        saved=saved,
        vote_records=vote_records,
        variant_fail_counts=variant_fail_counts,
        variant_prefilter_stats=variant_prefilter_stats,
        variant_prefilter_messages=variant_prefilter_messages,
    )
    write_detail_csv(detail_csv_path, vote_records, out_dir.name)

    summary = build_summary(
        put=put,
        canonical=canonical,
        variants=variants,
        tests=tests,
        fixed_min_votes=fixed_min_votes,
        saved=saved,
        vote_records=vote_records,
        variant_fail_counts=variant_fail_counts,
        report_path=report_path,
        original_variant_count=original_variant_count,
        variant_prefilter_stats=variant_prefilter_stats,
        variant_prefilter_messages=variant_prefilter_messages,
    )
    summary_path = out_dir / "summary.json"
    write_summary_json(summary_path, summary)

    if variant_fail_counts:
        print("[VARIANT_FAIL_SUMMARY]")
        for name, cnt in sorted(variant_fail_counts.items()):
            print(f"  {name}: {cnt}")

    print(
        "[STATS] "
        f"tests={summary['tests_dir_size']} saved={summary['saved']} "
        f"agree={summary['agree']} "
        f"found={summary['found']} "
        f"no_majority={summary['no_majority']} "
        f"no_variant_output={summary['no_variant_output']} "
        f"put_fail={summary['put_fail']} "
        f"tp_count={summary['tp_count']} "
        f"fp_count={summary['fp_count']} "
        f"oracle_wrong_count={summary['oracle_wrong_count']} "
        f"canonical_fail_count={summary['canonical_fail_count']} "
        f"report={report_path} "
        f"summary_json={summary_path} "
        f"detail_csv={detail_csv_path}"
    )
    print(f"[DONE] saved {saved} bug-triggering cases into {out_dir}")


if __name__ == "__main__":
    main()
