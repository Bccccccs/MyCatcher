# DPP Baseline

This entrypoint is a focused differential-testing runner, not the full
paper-faithful reproduction path.

Goal: run the existing DPP-style variant-based differential testing pipeline as
an isolated baseline with its own outputs and summary files.

Inputs:
- problem directories
- canonical solutions
- generated variants
- generated legal test inputs

Main command:

```bash
python3 experiments/dpp/run_dpp.py --layout dataset --lang cpp
```

For the canonical TrickCatcher-style reproduction workflow, use:

```bash
.venv/bin/python experiments/trickcatcher/run_trickcatcher.py --lang cpp
```

Outputs:
- `outputs/dpp/<pid>/raw.log`
- `outputs/dpp/<pid>/detail.csv`
- `outputs/dpp/<pid>/summary.json`
- `outputs/dpp/<pid>/report.txt`
- `outputs/dpp/summary.csv`

Assumptions and limitations:
- this entrypoint reuses `LLM_Gen/differential_testing.py`
- it expects variants and inputs to already exist
- variant generation remains separate from DPP evaluation
- use this when you only want the evaluation stage, not the full reproduction
