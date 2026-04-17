import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.progress import log_line, print_progress, suspend_progress


HELP_TEXT = """
How to use:
  1. Generate variants for TrickyBugs-style datasets:
     python3 start/run_varProgs_gen.py --layout dataset

  2. Generate variants for a single dataset problem:
     python start/run_varProgs_gen.py --layout dataset --pid p02547

  3. Generate variants for AC problems:
     python3 start/run_varProgs_gen.py --layout ac

  4. Generate variants for a single AC problem:
     python3 start/run_varProgs_gen.py --layout ac --pid p02730

Layout meanings:
  - dataset: use dataset-root and write variants to a shared output root
  - ac: use AC/<pid>/ and write variants into AC/<pid>/gen_bundle/variants
""".strip()


def run(cmd: list[str], cwd: Path) -> None:
    suspend_progress()
    log_line(f">>> {' '.join(map(str, cmd))}")
    subprocess.run(list(map(str, cmd)), check=True, cwd=str(cwd))


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def find_program_dirs(root_dir: Path) -> list[Path]:
    return sorted(program_dir for program_dir in root_dir.iterdir() if program_dir.is_dir())


def find_dataset_put_file(program_dir: Path, lang: str) -> Path | None:
    if lang == "cpp":
        candidates = [program_dir / "put.cpp"]
        candidates.extend(sorted(program_dir.glob("sol_*.cpp")))
        candidates.append(program_dir / "put")
    else:
        candidates = [program_dir / "put.py"]
        candidates.extend(sorted(program_dir.glob("sol_*.py")))
        candidates.append(program_dir / "put")

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_ac_put_file(program_dir: Path, lang: str, put_name: str | None) -> Path | None:
    if put_name:
        candidate = program_dir / put_name
        return candidate if candidate.exists() else None

    if lang == "cpp":
        candidates = [program_dir / "ac_sol.cpp", program_dir / "put.cpp", program_dir / "ac_sol"]
    else:
        candidates = [program_dir / "ac_sol.py", program_dir / "put.py", program_dir / "ac_sol"]

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_dataset_spec_file(program_dir: Path) -> Path | None:
    for candidate in (program_dir / "spec.txt", program_dir / "spec.txt.txt"):
        if candidate.exists():
            return candidate
    return None


def find_ac_spec_file(program_dir: Path, spec_name: str) -> Path | None:
    candidate = program_dir / spec_name
    return candidate if candidate.exists() else None


def resolve_mode_template(root: Path, mode: str, explicit_template: str | None) -> Path:
    if explicit_template:
        return resolve_path(root, explicit_template)
    if mode == "dpp":
        return resolve_path(root, "PromptTemplates/genprog_dfp")
    return resolve_path(root, "PromptTemplates/genprog_tc")


def infer_dataset_out_root(root: Path, dataset_root: Path, mode: str, lang: str, explicit_out_root: str | None) -> Path:
    if explicit_out_root:
        return resolve_path(root, explicit_out_root)

    dataset_root_str = str(dataset_root)
    if "TrickyBugs" not in dataset_root_str:
        return resolve_path(root, "outputs/variants") / lang

    lang_name = "python" if lang == "py" else "cpp"
    return resolve_path(root, f"Datasets/TrickyBugs/GenProgs/{mode}_generated_progs_{lang_name}")


def infer_dataset_naming(dataset_root: Path, explicit_naming: str | None) -> str:
    if explicit_naming:
        return explicit_naming
    return "trickybugs" if "TrickyBugs" in str(dataset_root) else "default"


def infer_name_prefix(program_dir: Path, naming: str) -> str | None:
    if naming != "trickybugs":
        return None
    pid = program_dir.name
    if re.fullmatch(r"p\d+", pid):
        return f"{pid}_num"
    return f"{pid}_variant_"


def build_variant_cmd(
    py: str,
    template_path: Path,
    lang: str,
    spec: Path,
    out_dir: Path,
    k: int,
    model: str,
    naming: str,
    index_start: int,
    sleep: float,
    put: Path | None,
    name_prefix: str | None,
) -> list[str]:
    return [
        py, "-m", "LLM_Gen.variant_generator",
        "--template", str(template_path),
        "--lang", lang,
        "--spec.txt", str(spec),
        "--out", str(out_dir),
        "--k", str(k),
        "--model", str(model),
        "--naming", naming,
        "--index-start", str(index_start),
        "--sleep", str(sleep),
        *(["--put", str(put)] if put is not None else []),
        *(["--name-prefix", name_prefix] if name_prefix else []),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate LLM-based variants for dataset-style or AC-style problem layouts.",
        epilog=HELP_TEXT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--layout",
        choices=["dataset", "ac"],
        default="dataset",
        help="Choose problem directory layout. Default: dataset",
    )
    parser.add_argument("--pid", default=None, help="Single problem id, e.g. p02547")
    parser.add_argument("--spec.txt", dest="spec_txt", default=None, help="Single spec.txt path for dataset layout")
    parser.add_argument("--put", default=None, help="PUT file path in single mode for dataset layout")
    parser.add_argument("--mode", choices=["dpp", "tc"], default="dpp", help="dpp uses spec only; tc uses spec + solution")
    parser.add_argument("--lang", choices=["py", "cpp"], default="cpp")
    parser.add_argument("--template", default=None, help="Optional prompt template path")
    parser.add_argument("--naming", choices=["default", "trickybugs"], default=None, help="Output naming scheme")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--index-start", type=int, default=0)
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--sleep", type=float, default=0.2, help="Sleep seconds between LLM calls")

    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--out-root", default=None, help="Dataset layout only. Shared variant output root")

    parser.add_argument("--ac-root", default="AC")
    parser.add_argument("--spec-name", default="spec.txt", help="AC layout only. Spec filename inside AC/<pid>/")
    parser.add_argument("--put-name", default=None, help="AC layout only. Solution filename inside AC/<pid>/")
    parser.add_argument("--bundle-dir", default="gen_bundle", help="AC layout only. Bundle directory inside AC/<pid>/")
    parser.add_argument("--variants-dirname", default="variants", help="AC layout only. Variants directory inside bundle dir")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable
    template_path = resolve_mode_template(root, args.mode, args.template)

    if args.layout == "dataset":
        dataset_root = resolve_path(root, args.dataset_root)
        if not dataset_root.exists():
            raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

        naming = infer_dataset_naming(dataset_root, args.naming)
        out_root = infer_dataset_out_root(root, dataset_root, args.mode, args.lang, args.out_root)

        if args.pid and args.spec_txt:
            raise ValueError("--pid and --spec.txt cannot be used together")

        if args.pid or args.spec_txt:
            if args.pid:
                program_dir = dataset_root / args.pid
                if not program_dir.exists():
                    raise FileNotFoundError(f"Problem dir not found: {program_dir}")
                spec = find_dataset_spec_file(program_dir)
                if spec is None:
                    raise FileNotFoundError(f"spec.txt not found in: {program_dir}")
            else:
                spec = resolve_path(root, args.spec_txt)
                program_dir = spec.parent

            put = None
            if args.mode == "tc":
                put = resolve_path(root, args.put) if args.put else find_dataset_put_file(program_dir, args.lang)
                if put is None:
                    raise FileNotFoundError(f"PUT file not found in: {program_dir}")

            out_dir = out_root / program_dir.name
            name_prefix = infer_name_prefix(program_dir, naming)
            cmd = build_variant_cmd(
                py=py,
                template_path=template_path,
                lang=args.lang,
                spec=spec,
                out_dir=out_dir,
                k=args.k,
                model=args.model,
                naming=naming,
                index_start=args.index_start,
                sleep=args.sleep,
                put=put,
                name_prefix=name_prefix,
            )
            run(cmd, cwd=root)
            log_line(f"[DONE] variants -> {out_dir}")
            return

        ok = 0
        skipped = 0
        program_dirs = find_program_dirs(dataset_root)
        for done, program_dir in enumerate(program_dirs, 1):
            spec = find_dataset_spec_file(program_dir)
            put = find_dataset_put_file(program_dir, args.lang) if args.mode == "tc" else None
            if spec is None or (args.mode == "tc" and put is None):
                skipped += 1
                print_progress(done, len(program_dirs), f"problems skipped={program_dir.name}")
                continue

            out_dir = out_root / program_dir.name
            name_prefix = infer_name_prefix(program_dir, naming)
            cmd = build_variant_cmd(
                py=py,
                template_path=template_path,
                lang=args.lang,
                spec=spec,
                out_dir=out_dir,
                k=args.k,
                model=args.model,
                naming=naming,
                index_start=args.index_start,
                sleep=args.sleep,
                put=put,
                name_prefix=name_prefix,
            )
            run(cmd, cwd=root)
            ok += 1
            print_progress(done, len(program_dirs), f"problems latest={program_dir.name}")

        log_line(f"[DONE] generated={ok}, skipped={skipped}, out_root={out_root}")
        return

    ac_root = resolve_path(root, args.ac_root)
    if not ac_root.exists():
        raise FileNotFoundError(f"AC root not found: {ac_root}")

    naming = args.naming or "trickybugs"
    if args.spec_txt:
        raise ValueError("--spec.txt is only supported for --layout dataset")
    if args.put:
        raise ValueError("--put is only supported for --layout dataset")
    if args.out_root:
        raise ValueError("--out-root is only supported for --layout dataset")

    if args.pid:
        program_dirs = [ac_root / args.pid]
    else:
        program_dirs = find_program_dirs(ac_root)

    ok = 0
    skipped = 0
    for done, program_dir in enumerate(program_dirs, 1):
        if not program_dir.exists():
            log_line(f"[SKIP] problem dir not found: {program_dir}")
            skipped += 1
            print_progress(done, len(program_dirs), f"problems skipped={program_dir.name}")
            continue

        spec = find_ac_spec_file(program_dir, args.spec_name)
        if spec is None:
            log_line(f"[SKIP] spec file not found: {program_dir / args.spec_name}")
            skipped += 1
            print_progress(done, len(program_dirs), f"problems skipped={program_dir.name}")
            continue

        put = None
        if args.mode == "tc":
            put = find_ac_put_file(program_dir, args.lang, args.put_name)
            if put is None:
                log_line(f"[SKIP] PUT file not found in: {program_dir}")
                skipped += 1
                print_progress(done, len(program_dirs), f"problems skipped={program_dir.name}")
                continue

        out_dir = program_dir / args.bundle_dir / args.variants_dirname
        name_prefix = infer_name_prefix(program_dir, naming)
        cmd = build_variant_cmd(
            py=py,
            template_path=template_path,
            lang=args.lang,
            spec=spec,
            out_dir=out_dir,
            k=args.k,
            model=args.model,
            naming=naming,
            index_start=args.index_start,
            sleep=args.sleep,
            put=put,
            name_prefix=name_prefix,
        )
        run(cmd, cwd=root)
        ok += 1
        log_line(f"[OK] variants -> {out_dir}")
        print_progress(done, len(program_dirs), f"problems latest={program_dir.name}")

    log_line(f"[DONE] total={len(program_dirs)} ok={ok} skipped={skipped}")


if __name__ == "__main__":
    main()
