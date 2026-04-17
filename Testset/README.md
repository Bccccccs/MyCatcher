`Testset/` is the input root for the unified test pipeline.

Layout:

```text
Testset/
  p02547/
    spec.txt
    put.cpp
```

Rules:

- Each problem must be in a directory named `pxxxxx`.
- Put the spec in `spec.txt`.
- Put the program under test in `put.cpp` / `put.py`.
- The existing fallback names `sol_*.cpp` / `sol_*.py` are also accepted.

Run:

```bash
.venv/bin/python start/run_testset_pipeline.py
```

Single problem:

```bash
.venv/bin/python start/run_testset_pipeline.py --pid p02547
```

Default outputs:

- `outputs/testset/variants/<pid>/`
- `outputs/testset/inputs/<pid>/`
- `outputs/testset/tcases/<lang>/<pid>/`
- `outputs/testset/logs/`

If you also have canonical programs in `AC/<pid>/`, you can enable them with:

```bash
.venv/bin/python start/run_testset_pipeline.py --canonical-root AC
```
