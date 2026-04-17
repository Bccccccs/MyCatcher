import argparse
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_ROOT = ROOT / "problems"
ORIGIN_PUT_ROOT = ROOT / "orgrin_Datasets" / "TrickyBugs" / "PUT_cpp"
ORIGIN_VARIANT_ROOT = ROOT / "orgrin_Datasets" / "TrickyBugs" / "GenProgs" / "dpp_generated_progs_cpp"
TARGET_PUT_ROOT = ROOT / "Datasets" / "TrickyBugs" / "PUT_cpp"
TARGET_VARIANT_ROOT = ROOT / "Datasets" / "TrickyBugs" / "GenProgs" / "dpp_generated_progs_cpp"
TARGET_AC_ROOT = ROOT / "AC"
MANIFEST_PATH = ROOT / "outputs" / "manifests" / "problem_pool_sync.json"


def pid_dirs(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {path.name for path in root.iterdir() if path.is_dir()}


def sol_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"sol_(\d+)\.cpp$", path.name)
    if match:
        return int(match.group(1)), path.name
    return 10**9, path.name


def pick_canonical_source(problem_dir: Path) -> Path | None:
    ref_dir = problem_dir / "reference_programs"
    ref_candidates = sorted(ref_dir.glob("sol_*.cpp"), key=sol_sort_key)
    if ref_candidates:
        return ref_candidates[0]

    fixed_dir = problem_dir / "fixed_programs" / "cpp"
    fixed_candidates = sorted(fixed_dir.glob("sol_*.cpp"), key=sol_sort_key)
    if fixed_candidates:
        return fixed_candidates[0]
    return None


def ensure_copytree(src: Path, dst: Path) -> str:
    if dst.exists():
        return "skipped"
    shutil.copytree(src, dst)
    return "copied"


def ensure_copyfile(src: Path, dst: Path) -> str:
    if dst.exists():
        return "skipped"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return "copied"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync problems that exist in both problems/ and orgrin_Datasets/ into Datasets/ and AC/."
    )
    parser.add_argument("--limit", type=int, default=None, help="Only sync the first N matching problems.")
    parser.add_argument("--pid", action="append", default=None, help="Only sync specific pid(s). Can be used multiple times.")
    parser.add_argument("--manifest", default=str(MANIFEST_PATH), help="Output manifest JSON path.")
    args = parser.parse_args()

    problem_ids = pid_dirs(PROBLEMS_ROOT)
    origin_put_ids = pid_dirs(ORIGIN_PUT_ROOT)
    origin_variant_ids = pid_dirs(ORIGIN_VARIANT_ROOT)

    matched = sorted(problem_ids & origin_put_ids & origin_variant_ids)
    if args.pid:
        wanted = set(args.pid)
        matched = [pid for pid in matched if pid in wanted]
    if args.limit is not None:
        matched = matched[:args.limit]

    manifest_rows: list[dict[str, object]] = []
    summary = {
        "matched_total": len(matched),
        "put_copied": 0,
        "put_skipped": 0,
        "variants_copied": 0,
        "variants_skipped": 0,
        "ac_copied": 0,
        "ac_skipped": 0,
        "ac_missing_source": 0,
    }

    for pid in matched:
        problem_dir = PROBLEMS_ROOT / pid
        put_src = ORIGIN_PUT_ROOT / pid
        variant_src = ORIGIN_VARIANT_ROOT / pid
        canonical_src = pick_canonical_source(problem_dir)

        put_status = ensure_copytree(put_src, TARGET_PUT_ROOT / pid)
        variant_status = ensure_copytree(variant_src, TARGET_VARIANT_ROOT / pid)
        if canonical_src is None:
            ac_status = "missing_source"
        else:
            ac_status = ensure_copyfile(canonical_src, TARGET_AC_ROOT / pid / "ac_sol.cpp")

        summary[f"put_{put_status}"] += 1
        summary[f"variants_{variant_status}"] += 1
        if ac_status == "missing_source":
            summary["ac_missing_source"] += 1
        else:
            summary[f"ac_{ac_status}"] += 1

        manifest_rows.append({
            "pid": pid,
            "problem_description": str(problem_dir / "problem_description.txt"),
            "put_src": str(put_src),
            "put_dst": str(TARGET_PUT_ROOT / pid),
            "variants_src": str(variant_src),
            "variants_dst": str(TARGET_VARIANT_ROOT / pid),
            "canonical_src": str(canonical_src) if canonical_src else "",
            "canonical_dst": str(TARGET_AC_ROOT / pid / "ac_sol.cpp"),
            "put_status": put_status,
            "variants_status": variant_status,
            "ac_status": ac_status,
        })

    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"summary": summary, "rows": manifest_rows}, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"summary": summary, "manifest": str(manifest_path)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
