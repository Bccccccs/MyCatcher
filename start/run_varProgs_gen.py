import argparse
import subprocess
import sys
import re
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print("\n>>>", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True, cwd=str(cwd))


def resolve_path(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (root / p).resolve()


def find_program_dirs(dataset_root: Path) -> list[Path]:
    return sorted([p for p in dataset_root.iterdir() if p.is_dir()])


def find_put_file(program_dir: Path, lang: str) -> Path | None:
    if lang == "cpp":
        candidates = [program_dir / "put.cpp"]
        candidates.extend(sorted(program_dir.glob("sol_*.cpp")))
        candidates.append(program_dir / "put")
    else:
        candidates = [program_dir / "put.py"]
        candidates.extend(sorted(program_dir.glob("sol_*.py")))
        candidates.append(program_dir / "put")
    for c in candidates:
        if c.exists():
            return c
    return None


def find_spec_file(program_dir: Path) -> Path | None:
    for candidate in (program_dir / "spec.txt", program_dir / "spec.txt.txt"):
        if candidate.exists():
            return candidate
    return None


def resolve_mode_template(root: Path, mode: str) -> Path:
    if mode == "dpp":
        return resolve_path(root, "PromptTemplates/genprog_dfp")
    return resolve_path(root, "PromptTemplates/genprog_tc")


def infer_out_root(dataset_root: Path, mode: str, lang: str, explicit_out_root: str | None) -> Path:
    if explicit_out_root:
        return resolve_path(Path(__file__).resolve().parent.parent, explicit_out_root)

    dataset_root_str = str(dataset_root)
    if "TrickyBugs" not in dataset_root_str:
        return resolve_path(Path(__file__).resolve().parent.parent, "outputs/variants") / lang

    lang_name = "python" if lang == "py" else "cpp"
    return resolve_path(
        Path(__file__).resolve().parent.parent,
        f"Datasets/TrickyBugs/GenProgs/{mode}_generated_progs_{lang_name}",
    )


def infer_naming(dataset_root: Path, explicit_naming: str | None) -> str:
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pid", default=None, help="Single problem id (e.g. p02547). If provided, resolve spec/put from <dataset-root>/<pid>/")
    ap.add_argument("--spec.txt", dest="spec_txt", default=None, help="Single spec.txt path. If omitted, run for all <dataset-root>/*/spec.txt")
    ap.add_argument("--put", default=None, help="PUT file path in single mode; used by tc mode, ignored by dpp mode")
    ap.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    ap.add_argument("--mode", choices=["dpp", "tc"], default="dpp", help="Variant generation mode: dpp uses spec only; tc uses spec + PUT")
    ap.add_argument("--lang", choices=["py", "cpp"], default="cpp")
    ap.add_argument("--out-root", default=None, help="Variant output root")
    ap.add_argument("--naming", choices=["default", "trickybugs"], default=None, help="Output naming scheme")
    ap.add_argument("--k", default="10")
    ap.add_argument("--model", default="deepseek-chat")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable
    dataset_root = resolve_path(root, args.dataset_root)
    naming = infer_naming(dataset_root, args.naming)
    template_path = resolve_mode_template(root, args.mode)
    out_root = infer_out_root(dataset_root, args.mode, args.lang, args.out_root)

    if args.pid and args.spec_txt:
        raise ValueError("--pid and --spec.txt cannot be used together")

    if args.pid or args.spec_txt:
        if args.pid:
            program_dir = dataset_root / args.pid
            if not program_dir.exists():
                raise FileNotFoundError(f"Problem dir not found: {program_dir}")
            spec = find_spec_file(program_dir)
            if spec is None:
                raise FileNotFoundError(f"spec.txt not found in: {program_dir}")
        else:
            spec = resolve_path(root, args.spec_txt)
            program_dir = spec.parent

        put = None
        if args.mode == "tc":
            put = resolve_path(root, args.put) if args.put else find_put_file(program_dir, args.lang)
            if put is None:
                raise FileNotFoundError(f"PUT file not found in: {program_dir}")

        name_prefix = infer_name_prefix(spec.parent, naming)
        run([
            py, "-m", "LLM_Gen.variant_generator",
            "--template", str(template_path),
            "--lang", args.lang,
            "--spec.txt", str(spec),
            "--out", str(out_root / spec.parent.name),
            "--k", str(args.k),
            "--model", str(args.model),
            "--naming", naming,
            "--index-start", "0",
            *(["--put", str(put)] if put is not None else []),
            *(["--name-prefix", name_prefix] if name_prefix else []),
        ], cwd=root)
        print(f"[DONE] variants -> {out_root / spec.parent.name}")
        return

    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    ok = 0
    skipped = 0
    for program_dir in find_program_dirs(dataset_root):
        spec = find_spec_file(program_dir)
        put = find_put_file(program_dir, args.lang) if args.mode == "tc" else None
        if spec is None or (args.mode == "tc" and put is None):
            skipped += 1
            continue

        out_dir = out_root / program_dir.name
        name_prefix = infer_name_prefix(program_dir, naming)
        run([
            py, "-m", "LLM_Gen.variant_generator",
            "--template", str(template_path),
            "--lang", args.lang,
            "--spec.txt", str(spec),
            "--out", str(out_dir),
            "--k", str(args.k),
            "--model", str(args.model),
            "--naming", naming,
            "--index-start", "0",
            *(["--put", str(put)] if put is not None else []),
            *(["--name-prefix", name_prefix] if name_prefix else []),
        ], cwd=root)
        ok += 1

    print(f"[DONE] generated={ok}, skipped={skipped}, out_root={out_root}")


if __name__ == "__main__":
    main()
