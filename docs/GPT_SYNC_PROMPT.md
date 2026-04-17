# GPT Sync Prompt

下面这段 prompt 用来把当前项目状态同步给新的 GPT / ChatGPT 对话。你可以直接复制整段发送。

---

You are helping me continue development on my graduation-project repository `MyCatcher`, which reproduces and extends the paper “LLM-Powered Test Case Generation for Detecting Bugs in Plausible Programs” / TrickCatcher.

Current repository status:

1. The repository originally centered on a TrickyBugs / MyCatcher differential-testing workflow.
2. The old core pipeline is still present:
   - `start/run_varProgs_gen.py`
   - `start/run_input_gen.py`
   - `start/run_check_inputs.py`
   - `start/run_dif_test.py`
   - `LLM_Gen/differential_testing.py`
   - `start/run_ac_oracle_compare.py`
   - `start/report_summary.py`
   - `start/baseline_summary.py`
3. The DPP voting logic has already been changed back to a fixed hard 6-vote mechanism.
4. The project has now been extended with a new additive experiment organization so that three baselines are clearly separated:
   - CHAT / DirectChat baseline
   - DPP baseline
   - APR baseline

Current new structure:

- `common/`
  - `problem_loader.py`
  - `spec_loader.py`
  - `put_loader.py`
  - `llm_client.py`
  - `checker_runner.py`
  - `execution.py`
  - `report_utils.py`
  - `path_utils.py`
  - `metrics.py`
- `experiments/chat/`
  - `run_chat.py`
  - `prompt_templates.py`
  - `evaluator.py`
  - `README.md`
- `experiments/dpp/`
  - `run_dpp.py`
  - `prompt_templates.py`
  - `evaluator.py`
  - `README.md`
- `experiments/apr/`
  - `run_apr.py`
  - `prompt_templates.py`
  - `patch_executor.py`
  - `evaluator.py`
  - `README.md`

Baseline semantics:

- CHAT:
  - direct LLM test-case generation from `spec + PUT`
  - not differential testing
  - outputs go to `outputs/chat/<pid>/...`
- DPP:
  - variant-based differential testing baseline
  - reuses the current differential-testing core
  - outputs go to `outputs/dpp/<pid>/...`
- APR:
  - repair-candidate generation baseline
  - independent from TC / TrickCatcher
  - outputs go to `outputs/apr/<pid>/...`

Output conventions:

- `outputs/chat/<pid>/raw_llm_output/`
- `outputs/chat/<pid>/normalized_tests/`
- `outputs/chat/<pid>/invalid_tests/`
- `outputs/chat/<pid>/executions/`
- `outputs/chat/<pid>/report.json`
- `outputs/chat/<pid>/report.txt`

- `outputs/dpp/<pid>/raw.log`
- `outputs/dpp/<pid>/detail.csv`
- `outputs/dpp/<pid>/summary.json`
- `outputs/dpp/<pid>/report.txt`

- `outputs/apr/<pid>/raw_llm_output/`
- `outputs/apr/<pid>/candidate_patches/`
- `outputs/apr/<pid>/compile_logs/`
- `outputs/apr/<pid>/executions/`
- `outputs/apr/<pid>/report.json`
- `outputs/apr/<pid>/report.txt`

Root-level summaries:

- `outputs/chat/summary.csv`
- `outputs/chat/summary.json`
- `outputs/chat/summary.txt`
- `outputs/dpp/summary.csv`
- `outputs/dpp/summary.json`
- `outputs/dpp/summary.txt`
- `outputs/apr/summary.csv`
- `outputs/apr/summary.json`
- `outputs/apr/summary.txt`
- `outputs/experiment_comparison.csv`

Important implementation details:

- The refactor was additive, not a destructive rewrite.
- Old `start/` scripts remain for compatibility.
- New thesis-facing experiment entrypoints are:
  - `python3 experiments/chat/run_chat.py ...`
  - `python3 experiments/dpp/run_dpp.py ...`
  - `python3 experiments/apr/run_apr.py ...`
- `LLM_Gen/differential_testing.py` and `start/run_dif_test.py` were adjusted so the main DPP evaluation now uses a fixed 6-vote threshold.

Validation status:

- New modules pass `py_compile`.
- `--help` works for:
  - `experiments/chat/run_chat.py`
  - `experiments/dpp/run_dpp.py`
  - `experiments/apr/run_apr.py`
- DPP smoke test succeeded on:
  - `python3 experiments/dpp/run_dpp.py --layout dataset --lang cpp --pid p02577 --out-root outputs/dpp_test`

Known limitations / assumptions:

- CHAT and APR require a working LLM API environment to run end-to-end.
- APR currently generates full repaired programs, not unified diff patches.
- APR “fix” status means “appears fixed under available evaluation tests”, not formal proof.
- `outputs/experiment_comparison.csv` is currently a baseline-level comparison scaffold, not a final thesis-ready comprehensive comparison table.

Existing design note and docs:

- `docs/experiment_baseline_design_note.md`
- `docs/BASELINE_EXPERIMENT_GUIDE.md`
- `docs/GPT_SYNC_PROMPT.md`

When continuing work, please:

1. Preserve the separation between CHAT, DPP, and APR.
2. Do not merge APR into TC / DPP.
3. Do not redefine CHAT as differential testing.
4. Prefer reuse through `common/` rather than duplicating logic.
5. Keep changes practical for a thesis reproduction project.
6. Before large changes, inspect existing code and integrate incrementally.

My likely next requests may include:

- refining thesis-ready reporting tables
- improving APR evaluation rigor
- aligning old `start/` scripts with the new experiment layer
- documenting experimental procedures in more academic language
- adding richer aggregate comparison outputs across CHAT / DPP / APR

Please first summarize your understanding of the current repository state before proposing new changes.

---
