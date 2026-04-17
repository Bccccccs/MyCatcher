# TrickCatcher Reproduction

This directory is the canonical paper-faithful reproduction path for
MyCatcher.

It keeps the original project workflow centered on TrickCatcher-style
variant-based differential testing:

1. reuse the existing variants dataset for the PUT
2. construct input tools from `spec.txt`
3. generate test inputs from the spec-derived tools
4. check and filter invalid inputs
5. run differential testing across PUT and variants
6. write thesis-friendly aggregate summaries

Main command:

```bash
.venv/bin/python experiments/trickcatcher/run_trickcatcher.py --lang cpp
```

This command reuses the existing variants dataset by default. If you want to
regenerate variants explicitly:

```bash
.venv/bin/python experiments/trickcatcher/run_trickcatcher.py --lang cpp --run-variant-gen
```

Single problem:

```bash
.venv/bin/python experiments/trickcatcher/run_trickcatcher.py --lang cpp --pid p02594
```

Outputs:
- `outputs/tcases/cpp/<pid>/...` keeps the original differential-testing reports
- `outputs/trickcatcher/per_problem_summary.csv`
- `outputs/trickcatcher/summary.json`
- `outputs/trickcatcher/summary.txt`
- `outputs/trickcatcher/analysis/...`
- `outputs/trickcatcher/comparison_scaffold.csv`

Notes:
- This wrapper intentionally reuses the existing `start/` scripts instead of
  replacing them.
- Existing variants are reused by default for the canonical reproduction path.
- Fixed 6-vote DPP behavior is preserved by default through
  `--fixed-min-votes 6`.
- `experiments/chat` remains a direct-generation baseline.
- `experiments/apr` remains a repair baseline.
