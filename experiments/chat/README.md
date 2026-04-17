# CHAT Baseline

This is the direct-generation baseline, not the canonical TrickCatcher
reproduction path.

Goal: directly ask the LLM to generate bug-revealing test inputs from `spec.txt`
and the PUT, without using program variants or differential voting.

Inputs:
- problem directories under `Datasets/TrickyBugs/PUT_cpp` or `AC`
- `spec.txt`
- PUT source file
- canonical / accepted solution if available
- optional `check_input.py`

Main command:

```bash
python3 experiments/chat/run_chat.py --layout dataset --lang cpp
```

Outputs:
- `outputs/chat/<pid>/raw_llm_output/`
- `outputs/chat/<pid>/normalized_tests/`
- `outputs/chat/<pid>/invalid_tests/`
- `outputs/chat/<pid>/executions/`
- `outputs/chat/<pid>/report.json`
- `outputs/chat/<pid>/report.txt`
- `outputs/chat/summary.csv`

Assumptions and limitations:
- canonical execution is required for reliable bug detection
- checker validation is optional and skipped if no checker exists
- current implementation treats each parsed test input as one candidate artifact
