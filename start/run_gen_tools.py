import argparse
import subprocess
import sys
from pathlib import Path


HELP_TEXT = """
How to use:
  1. Generate only input generators:
     python3 start/run_gen_tools.py --tool generator

  2. Generate only checkers:
     python3 start/run_gen_tools.py --tool checker

  3. Generate both generator and checker:
     python3 start/run_gen_tools.py --tool both

  4. Generate tools for one problem only by pid:
     python3 start/run_gen_tools.py --tool both --pid p02547

  5. Generate tools for one problem only by spec:
     python3 start/run_gen_tools.py --tool both --spec Datasets/TrickyBugs/PUT_cpp/p02547/spec.txt

Tool meanings:
  - generator: generate input_gen.py using LLM_Gen.generator_generator
  - checker: generate check_input.py using LLM_Gen.checker_generator
  - both: generate both files for the same problem(s)
""".strip()


def run(cmd: list[str], cwd: Path) -> None:
    print("\n>>>", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True, cwd=str(cwd))


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def resolve_out_for_spec(root: Path, spec: Path, out_arg: str) -> Path:
    path = Path(out_arg)
    if path.is_absolute():
        return path
    if path.parent == Path("."):
        return spec.parent / path.name
    return (root / path).resolve()


def find_program_dirs(dataset_root: Path) -> list[Path]:
    return sorted(program_dir for program_dir in dataset_root.iterdir() if program_dir.is_dir())


def build_single_tool_cmd(
    py: str,
    tool: str,
    spec: Path,
    template: str,
    out: Path,
    model: str,
) -> list[str]:
    module = "LLM_Gen.generator_generator" if tool == "generator" else "LLM_Gen.checker_generator"
    return [
        py, "-m", module,
        "--spec", str(spec),
        "--template", str(template),
        "--out", str(out),
        "--model", str(model),
    ]


def generate_for_spec(
    root: Path,
    py: str,
    spec: Path,
    tools: list[str],
    generator_template: str,
    checker_template: str,
    generator_out_arg: str,
    checker_out_arg: str,
    model: str,
) -> tuple[int, int]:
    generated = 0
    skipped = 0

    for tool in tools:
        if tool == "generator":
            template = generator_template
            out = resolve_out_for_spec(root, spec, generator_out_arg)
            label = "generator"
        else:
            template = checker_template
            out = resolve_out_for_spec(root, spec, checker_out_arg)
            label = "checker"

        if out.exists():
            print(f"[SKIP] {label} exists: {out}")
            skipped += 1
            continue

        cmd = build_single_tool_cmd(
            py=py,
            tool=tool,
            spec=spec,
            template=template,
            out=out,
            model=model,
        )
        run(cmd, cwd=root)
        generated += 1

    return generated, skipped


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate input generators and checkers from spec.txt files.",
        epilog=HELP_TEXT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--tool",
        choices=["generator", "checker", "both"],
        default="both",
        help="Choose which tool(s) to generate. Default: both",
    )
    parser.add_argument("--pid", default=None, help="Single problem id, e.g. p02547")
    parser.add_argument("--spec", default=None, help="Single spec.txt path. If omitted, run for all <dataset-root>/*/spec.txt")
    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--generator-template", default="geninput_generator")
    parser.add_argument("--checker-template", default="geninput_inspector")
    parser.add_argument("--generator-out", default="input_gen.py", help="Default writes next to spec.txt")
    parser.add_argument("--checker-out", default="check_input.py", help="Default writes next to spec.txt")
    parser.add_argument("--model", default="deepseek-chat")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable
    tools = ["generator", "checker"] if args.tool == "both" else [args.tool]

    if args.pid and args.spec:
        raise ValueError("--pid and --spec cannot be used together")

    if args.pid:
        spec = resolve_path(root, args.dataset_root) / args.pid / "spec.txt"
        generated, skipped = generate_for_spec(
            root=root,
            py=py,
            spec=spec,
            tools=tools,
            generator_template=args.generator_template,
            checker_template=args.checker_template,
            generator_out_arg=args.generator_out,
            checker_out_arg=args.checker_out,
            model=args.model,
        )
        print(f"[DONE] generated={generated}, skipped={skipped}, pid={args.pid}, spec={spec}")
        return

    if args.spec:
        spec = resolve_path(root, args.spec)
        generated, skipped = generate_for_spec(
            root=root,
            py=py,
            spec=spec,
            tools=tools,
            generator_template=args.generator_template,
            checker_template=args.checker_template,
            generator_out_arg=args.generator_out,
            checker_out_arg=args.checker_out,
            model=args.model,
        )
        print(f"[DONE] generated={generated}, skipped={skipped}, spec={spec}")
        return

    dataset_root = resolve_path(root, args.dataset_root)
    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    program_dirs = find_program_dirs(dataset_root)
    if not program_dirs:
        raise RuntimeError(f"No program folders found under: {dataset_root}")

    generated = 0
    skipped = 0
    missing_spec = 0
    for program_dir in program_dirs:
        spec = program_dir / "spec.txt"
        if not spec.exists():
            missing_spec += 1
            continue

        gen_count, skip_count = generate_for_spec(
            root=root,
            py=py,
            spec=spec,
            tools=tools,
            generator_template=args.generator_template,
            checker_template=args.checker_template,
            generator_out_arg=args.generator_out,
            checker_out_arg=args.checker_out,
            model=args.model,
        )
        generated += gen_count
        skipped += skip_count

    print(
        f"[DONE] generated={generated}, skipped={skipped}, missing_spec={missing_spec}, dataset={dataset_root}"
    )


if __name__ == "__main__":
    main()
