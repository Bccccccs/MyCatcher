import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.progress import log_line, print_progress, suspend_progress


HELP_TEXT = """
How to use:
  1. Generate inputs using an existing input_gen.py:
     python3 start/run_input_gen.py --backend generator

  2. Generate inputs directly with the LLM:
     python3 start/run_input_gen.py --backend llm

  3. Generate 100 inputs using input_gen.py (default):
     python3 start/run_input_gen.py

  4. Generate inputs for one problem only:
     python3 start/run_input_gen.py --pid p02547

  5. Generate inputs for one spec.txt directly:
     python3 start/run_input_gen.py --backend llm --spec Datasets/TrickyBugs/PUT_cpp/p02547/spec.txt

Backend meanings:
  - generator: run the generated input_gen.py next to each problem
  - llm: call LLM_Gen.input_generator directly
  - mixed: run the generated input_gen.py first, then append direct LLM boundary inputs
""".strip()


def run(cmd: list[str], cwd: Path) -> None:
    suspend_progress()
    subprocess.run(list(map(str, cmd)), check=True, cwd=str(cwd))


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def find_program_dirs(dataset_root: Path) -> list[Path]:
    return sorted(program_dir for program_dir in dataset_root.iterdir() if program_dir.is_dir())


def find_put_file(program_dir: Path) -> Path | None:
    exact_candidates = [
        program_dir / "put",
        program_dir / "put.py",
        program_dir / "put.cpp",
    ]
    for candidate in exact_candidates:
        if candidate.exists():
            return candidate

    for pattern in ("sol_*.cpp", "sol_*.py", "sol_*.cc", "sol_*.cxx"):
        candidates = sorted(
            p for p in program_dir.glob(pattern)
            if p.is_file() and not p.name.endswith("_parsed.cpp") and not p.name.endswith("_parsed.py")
        )
        if candidates:
            return candidates[0]
    return None


def count_input_files(out_dir: Path) -> int:
    if not out_dir.exists():
        return 0
    return sum(1 for p in out_dir.iterdir() if p.is_file() and p.suffix == ".in")


def is_output_dir_full(out_dir: Path, num: int) -> bool:
    return count_input_files(out_dir) >= num


def run_generator_backend(
    root: Path,
    py: str,
    program_dir: Path,
    generator_name: str,
    out_dir: Path,
    num: int,
    seed: int,
) -> None:
    generator = program_dir / generator_name
    if not generator.exists():
        raise FileNotFoundError(f"Generator not found: {generator}")
    run([
        py, str(generator),
        "--out_dir", str(out_dir),
        "--num", str(num),
        "--seed", str(seed),
    ], cwd=root)


def run_llm_backend(
    root: Path,
    py: str,
    spec: Path,
    put: Path,
    out_dir: Path,
    num: int,
    template: str,
    model: str,
    start_index: int = 0,
) -> None:
    run([
        py, "-m", "LLM_Gen.input_generator",
        "--spec", str(spec),
        "--put", str(put),
        "--out", str(out_dir),
        "--num", str(num),
        "--start-index", str(start_index),
        "--template", str(template),
        "--model", str(model),
    ], cwd=root)


def run_batch_task(
    root: Path,
    py: str,
    backend: str,
    program_dir: Path,
    generator_name: str,
    out_root: Path,
    num: int,
    random_num: int,
    llm_num: int,
    seed: int,
    template: str,
    model: str,
) -> tuple[str, str]:
    spec = program_dir / "spec.txt"
    if not spec.exists():
        return ("skipped", f"[SKIP] {program_dir.name}: missing spec.txt")

    out_dir = out_root / program_dir.name
    existing = count_input_files(out_dir)
    if existing >= num:
        return ("skipped", f"[SKIP] {program_dir.name}: {out_dir} already has {existing} .in files (target={num})")
    remaining = num - existing

    if backend == "generator":
        generator = program_dir / generator_name
        if not generator.exists():
            return ("skipped", f"[SKIP] {program_dir.name}: missing {generator_name}")
        run_generator_backend(
            root=root,
            py=py,
            program_dir=program_dir,
            generator_name=generator_name,
            out_dir=out_dir,
            num=remaining,
            seed=seed,
        )
    elif backend == "llm":
        put = find_put_file(program_dir)
        if put is None:
            return ("skipped", f"[SKIP] {program_dir.name}: missing put file")
        run_llm_backend(
            root=root,
            py=py,
            spec=spec,
            put=put,
            out_dir=out_dir,
            num=remaining,
            template=template,
            model=model,
            start_index=existing,
        )
    else:
        generator = program_dir / generator_name
        if not generator.exists():
            return ("skipped", f"[SKIP] {program_dir.name}: missing {generator_name}")
        put = find_put_file(program_dir)
        if put is None:
            return ("skipped", f"[SKIP] {program_dir.name}: missing put file")
        current_random_target = min(random_num, num)
        current_llm_target = max(0, num - current_random_target)
        existing_random = min(existing, current_random_target)
        existing_llm = max(0, existing - current_random_target)
        remaining_random = max(0, current_random_target - existing_random)
        remaining_llm = max(0, current_llm_target - existing_llm)
        run_generator_backend(
            root=root,
            py=py,
            program_dir=program_dir,
            generator_name=generator_name,
            out_dir=out_dir,
            num=remaining_random,
            seed=seed,
        )
        run_llm_backend(
            root=root,
            py=py,
            spec=spec,
            put=put,
            out_dir=out_dir,
            num=remaining_llm,
            template=template,
            model=model,
            start_index=current_random_target + existing_llm,
        )

    return ("generated", f"[DONE] {program_dir.name} -> {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate test inputs using either existing generators or direct LLM generation.",
        epilog=HELP_TEXT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--backend",
        choices=["generator", "llm", "mixed"],
        default="generator",
        help="Choose how inputs are generated. Default: generator",
    )
    parser.add_argument("--pid", default=None, help="Single problem id, e.g. p02547")
    parser.add_argument("--spec", default=None, help="Single spec.txt path. If omitted, run for all <dataset-root>/*/spec.txt")
    parser.add_argument("--put", default=None, help="PUT file path in single mode; used by llm backend")
    parser.add_argument("--dataset-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument("--out-root", default="outputs/inputs", help="Input data output root")

    parser.add_argument("--generator-name", default="input_gen.py", help="Generator backend only. Filename next to spec.txt")
    parser.add_argument("--seed", type=int, default=2, help="Generator backend only. Random seed passed to input_gen.py")

    parser.add_argument("--template", default="PromptTemplates/geninput_direct", help="LLM and mixed backends only. Prompt template")
    parser.add_argument("--model", default="deepseek-chat", help="LLM and mixed backends only. Model name")

    parser.add_argument("--num", type=int, default=100)
    parser.add_argument("--random-num", type=int, default=None, help="Mixed backend only. Generator input count. Default: --num - --llm-num")
    parser.add_argument("--llm-num", type=int, default=0, help="Mixed backend only. LLM boundary input count")
    parser.add_argument("--jobs", type=int, default=1, help="Batch mode only. Number of problems to process in parallel")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    py = sys.executable
    dataset_root = resolve_path(root, args.dataset_root)
    out_root = resolve_path(root, args.out_root)

    if args.pid and args.spec:
        raise ValueError("--pid and --spec cannot be used together")
    if args.jobs <= 0:
        raise ValueError("Invalid jobs: require jobs >= 1")
    if args.num < 0:
        raise ValueError("Invalid --num: require num >= 0")
    if args.llm_num < 0:
        raise ValueError("Invalid --llm-num: require llm-num >= 0")
    if args.random_num is not None and args.random_num < 0:
        raise ValueError("Invalid --random-num: require random-num >= 0")

    mixed_llm_num = args.llm_num
    mixed_random_num = args.random_num if args.random_num is not None else args.num - mixed_llm_num
    if args.backend == "mixed":
        if mixed_random_num < 0:
            raise ValueError("Invalid mixed counts: --llm-num cannot be greater than --num unless --random-num is set")
        mixed_total = mixed_random_num + mixed_llm_num
    else:
        mixed_total = args.num

    if args.pid or args.spec:
        if args.pid:
            if not dataset_root.exists():
                raise FileNotFoundError(f"Dataset root not found: {dataset_root}")
            program_dir = dataset_root / args.pid
            if not program_dir.exists():
                raise FileNotFoundError(f"Problem dir not found: {program_dir}")
            spec = program_dir / "spec.txt"
        else:
            spec = resolve_path(root, args.spec)
            program_dir = spec.parent

        if not spec.exists():
            raise FileNotFoundError(f"spec.txt not found: {spec}")

        out_dir = out_root / program_dir.name
        existing = count_input_files(out_dir)
        if existing >= mixed_total:
            log_line(f"[SKIP] {program_dir.name}: {out_dir} already has {existing} .in files (target={mixed_total})")
            return
        remaining = mixed_total - existing

        if args.backend == "generator":
            print_progress(0, 1, f"problem={program_dir.name}")
            run_generator_backend(
                root=root,
                py=py,
                program_dir=program_dir,
                generator_name=args.generator_name,
                out_dir=out_dir,
                num=remaining,
                seed=args.seed,
            )
        elif args.backend == "llm":
            put = resolve_path(root, args.put) if args.put else (find_put_file(program_dir) or program_dir / "put")
            run_llm_backend(
                root=root,
                py=py,
                spec=spec,
                put=put,
                out_dir=out_dir,
                num=remaining,
                template=args.template,
                model=args.model,
                start_index=existing,
            )
        else:
            print_progress(0, 1, f"problem={program_dir.name}")
            current_random_target = min(mixed_random_num, mixed_total)
            current_llm_target = max(0, mixed_total - current_random_target)
            existing_random = min(existing, current_random_target)
            existing_llm = max(0, existing - current_random_target)
            remaining_random = max(0, current_random_target - existing_random)
            remaining_llm = max(0, current_llm_target - existing_llm)
            run_generator_backend(
                root=root,
                py=py,
                program_dir=program_dir,
                generator_name=args.generator_name,
                out_dir=out_dir,
                num=remaining_random,
                seed=args.seed,
            )
            put = resolve_path(root, args.put) if args.put else (find_put_file(program_dir) or program_dir / "put")
            run_llm_backend(
                root=root,
                py=py,
                spec=spec,
                put=put,
                out_dir=out_dir,
                num=remaining_llm,
                template=args.template,
                model=args.model,
                start_index=current_random_target + existing_llm,
            )
        print_progress(1, 1, f"problem={program_dir.name}")
        log_line(f"[DONE] inputs -> {out_dir}")
        return

    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    program_dirs = find_program_dirs(dataset_root)
    ok = 0
    skipped = 0
    failed = 0

    if args.jobs == 1:
        for done, program_dir in enumerate(program_dirs, 1):
            status, message = run_batch_task(
                root=root,
                py=py,
                backend=args.backend,
                program_dir=program_dir,
                generator_name=args.generator_name,
                out_root=out_root,
                num=mixed_total,
                random_num=mixed_random_num,
                llm_num=mixed_llm_num,
                seed=args.seed,
                template=args.template,
                model=args.model,
            )
            log_line(message)
            if status == "generated":
                ok += 1
            else:
                skipped += 1
            print_progress(done, len(program_dirs), f"problems latest={program_dir.name}")
    else:
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(
                    run_batch_task,
                    root,
                    py,
                    args.backend,
                    program_dir,
                    args.generator_name,
                    out_root,
                    mixed_total,
                    mixed_random_num,
                    mixed_llm_num,
                    args.seed,
                    args.template,
                    args.model,
                ): program_dir
                for program_dir in program_dirs
            }
            for done, future in enumerate(as_completed(futures), 1):
                program_dir = futures[future]
                try:
                    status, message = future.result()
                    log_line(message)
                    if status == "generated":
                        ok += 1
                    else:
                        skipped += 1
                except Exception as exc:
                    failed += 1
                    log_line(f"[FAIL] {program_dir.name}: {exc}")
                print_progress(done, len(program_dirs), f"problems latest={program_dir.name}")

    log_line(
        f"[DONE] generated={ok}, skipped={skipped}, failed={failed}, jobs={args.jobs}, out_root={out_root}"
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
