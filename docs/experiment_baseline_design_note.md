# Experiment Baseline Design Note

## Current Structure

The current repository is centered on a TrickyBugs / MyCatcher differential-testing workflow:

- `start/run_varProgs_gen.py`
  discovers problems, loads `spec.txt` and optional PUTs, then invokes
  `LLM_Gen.variant_generator` to generate program variants.
- `start/run_input_gen.py`
  generates test inputs from either existing generators or direct LLM prompting.
- `start/run_check_inputs.py`
  validates generated inputs via per-problem `check_input.py`.
- `LLM_Gen/differential_testing.py`
  executes variants, PUT, and canonical solution, then writes detailed reports.
- `start/run_dif_test.py`
  is the batch entrypoint that resolves PUT/canonical/variant/input locations and
  orchestrates differential testing.
- `start/run_ac_oracle_compare.py`, `start/report_summary.py`, and
  `start/baseline_summary.py`
  parse and aggregate DPP-style outputs after the main run.

## Reusable Pieces

The repository already has useful reusable logic for:

- problem directory traversal and path resolution
- PUT discovery in dataset / AC layouts
- spec loading from `spec.txt`
- checker-based legality validation
- C++ / Python execution and canonical-oracle comparison
- report and summary writing
- LLM client setup and code extraction

## Coupling Problems

The main coupling issue is that these responsibilities are spread across batch
scripts in `start/`, and the current reporting/output structure is strongly
biased toward the DPP differential-testing baseline:

- path discovery logic is duplicated across scripts
- differential-testing assumptions leak into reporting
- direct-chat input generation is not isolated as its own baseline
- APR does not have a separate experiment pipeline

## Refactoring Direction

Add a new additive experiment organization without replacing the current
pipeline:

- `common/`
  contains reusable loaders, execution helpers, checker runners, metrics, and
  report writers.
- `experiments/chat/`
  implements direct test-case generation and evaluation as an independent
  baseline.
- `experiments/dpp/`
  wraps the existing differential-testing core in a clean DPP-specific
  experiment entrypoint and result layout.
- `experiments/apr/`
  implements repair-candidate generation and evaluation as a separate baseline.

The old `start/` scripts remain intact for compatibility. The new
`experiments/*/run_*.py` entrypoints become the thesis-facing experiment
interface.
