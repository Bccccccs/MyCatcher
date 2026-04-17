# APR Baseline

This is the repair baseline, not the canonical TrickCatcher reproduction path.

Goal: ask the LLM to generate repaired programs for each PUT, then evaluate
candidate repairs independently from CHAT and DPP.

Inputs:
- problem directories under dataset or AC layout
- `spec.txt`
- PUT source file
- canonical solution if available
- existing test inputs under `outputs/inputs/<pid>/`

Main command:

```bash
python3 experiments/apr/run_apr.py --layout dataset --lang cpp
```

Outputs:
- `outputs/apr/<pid>/raw_llm_output/`
- `outputs/apr/<pid>/candidate_patches/`
- `outputs/apr/<pid>/compile_logs/`
- `outputs/apr/<pid>/executions/`
- `outputs/apr/<pid>/report.json`
- `outputs/apr/<pid>/report.txt`
- `outputs/apr/summary.csv`

Assumptions and limitations:
- the current baseline asks for full repaired programs rather than textual diff
  patches
- apparent fix status is only under the available evaluation tests
- if no canonical or no tests are available, candidates are still generated but
  cannot be fully evaluated
