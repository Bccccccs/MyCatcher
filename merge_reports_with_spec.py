import argparse
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def collect_problem_ids(report_root: Path) -> list[str]:
    pids: list[str] = []
    for path in sorted(report_root.iterdir()):
        if not path.is_dir():
            continue
        if (path / "report.txt").exists():
            pids.append(path.name)
    return pids


def read_text_or_placeholder(path: Path, missing_label: str) -> str:
    if not path.exists():
        return f"[MISSING] {missing_label}: {path}"
    return path.read_text(encoding="utf-8").rstrip()


def build_merged_report(
    report_root: Path,
    spec_root: Path,
) -> str:
    pids = collect_problem_ids(report_root)
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "DPP",
        "Merged Differential Testing Report With Specs",
        f"Total reports: {len(pids)}",
        f"Generated at: {timestamp}",
    ]

    for pid in pids:
        report_path = report_root / pid / "report.txt"
        spec_path = spec_root / pid / "spec.txt"
        report_text = read_text_or_placeholder(report_path, "report")
        spec_text = read_text_or_placeholder(spec_path, "spec")

        lines.extend(
            [
                f"===== {pid} =====",
                f"Spec Source: {spec_path}",
                "Spec",
                spec_text,
                "",
                f"Report Source: {report_path}",
                report_text,
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge per-problem differential testing reports and include each problem spec."
    )
    parser.add_argument("--report-root", default="outputs/tcases/cpp")
    parser.add_argument("--spec-root", default="Datasets/TrickyBugs/PUT_cpp")
    parser.add_argument(
        "--output",
        default="outputs/tcases/cpp/batch_report_with_spec.txt",
    )
    args = parser.parse_args()

    report_root = resolve_path(args.report_root)
    spec_root = resolve_path(args.spec_root)
    output_path = resolve_path(args.output)

    if not report_root.exists():
        raise FileNotFoundError(f"Report root not found: {report_root}")
    if not spec_root.exists():
        raise FileNotFoundError(f"Spec root not found: {spec_root}")

    merged = build_merged_report(report_root=report_root, spec_root=spec_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(merged, encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
