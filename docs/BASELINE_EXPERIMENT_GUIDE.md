# Baseline Experiment Guide

这份文档面向当前 `MyCatcher / TrickyBugs` 复现实验仓库，目标是把现有项目拆成四条清晰的 baseline 实验线，并说明如何启动各个模块。

当前四条 baseline：

- `CHAT` / `DirectChat`
  - 直接根据 `spec + PUT` 让 LLM 生成测试输入
  - 不使用 program variants
  - 不属于 differential testing
- `DPP`
  - 使用 program variants + differential testing
  - 保持现有主线行为
- `APR`
  - 根据 `spec + PUT` 让 LLM 生成 repair candidates
  - 独立于 TC / TrickCatcher
- `TC` / `TrickCatcher`
  - 走 canonical reproduction pipeline
  - 包含 variant generation / input generation / input checking / differential testing


## 1. Repository Roles

### 1.1 Old pipeline modules

这些模块仍然保留，用于兼容旧流程：

- `start/run_varProgs_gen.py`
  - 生成 variants
- `start/run_input_gen.py`
  - 生成测试输入
- `start/run_check_inputs.py`
  - 用 checker 清洗输入
- `start/run_dif_test.py`
  - 调用 differential testing
- `LLM_Gen/differential_testing.py`
  - DPP 主评测核心
- `start/run_ac_oracle_compare.py`
  - 对比 oracle 与实际 accepted solution 输出
- `start/baseline_summary.py`
  - 汇总旧 DPP 结果

### 1.2 New experiment-facing modules

新的 thesis-facing 入口在：

- `experiments/chat/run_chat.py`
- `experiments/dpp/run_dpp.py`
- `experiments/apr/run_apr.py`
- `experiments/trickcatcher/run_trickcatcher.py`
- `start/run_baselines.py`
  - 统一调度 `chat / apr / dpp / tc`
  - 额外汇总四条线各自的结果

公共复用层在：

- `common/problem_loader.py`
- `common/spec_loader.py`
- `common/put_loader.py`
- `common/checker_runner.py`
- `common/execution.py`
- `common/report_utils.py`
- `common/llm_client.py`


## 2. Directory Conventions

### 2.1 Input data

默认 dataset layout：

- `Datasets/TrickyBugs/PUT_cpp/<pid>/`
  - `spec.txt`
  - PUT source，如 `sol_31.cpp`

默认 canonical / accepted solutions：

- `AC/<pid>/ac_sol.cpp`

默认已有测试输入：

- `outputs/inputs/<pid>/test_*.in`

默认已有 variants：

- `Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp/<pid>/`

### 2.2 New output layout

- `outputs/chat/<pid>/`
  - `raw_llm_output/`
  - `normalized_tests/`
  - `invalid_tests/`
  - `executions/`
  - `report.json`
  - `report.txt`
- `outputs/dpp/<pid>/`
  - `raw.log`
  - `detail.csv`
  - `summary.json`
  - `report.txt`
- `outputs/apr/<pid>/`
  - `raw_llm_output/`
  - `candidate_patches/`
  - `compile_logs/`
  - `executions/`
  - `report.json`
  - `report.txt`
- `outputs/trickcatcher/`
  - `summary.csv`
  - `summary.json`
  - `summary.txt`
  - `per_problem_summary.csv`
  - `stage_logs/`

每个 baseline 根目录还会生成：

- `summary.csv`
- `summary.json`
- `summary.txt`

全局对照文件：

- `outputs/experiment_comparison.csv`
- `outputs/baseline_runs/summary.csv`
  - 由统一入口 `start/run_baselines.py` 生成
  - 每行对应一个 baseline


## 3. Environment Preparation

建议先确认：

- Python 可用：`python3 --version`
- OpenAI-compatible API 环境变量已设置
  - `OPENAI_API_KEY`
  - 可选：`BASE_URL`
- 如果要跑 C++：
  - 系统上有 `g++` / `g++-15` / `clang++`

如果你要实际运行 CHAT / APR / variant generation，还需要保证当前 Python 环境已经安装项目依赖，比如：

- `openai`
- `python-dotenv`

如果只看 CLI 参数或跑 DPP 的已有离线结果汇总，不一定会触发所有 LLM 依赖。


## 4. Common Run Patterns

### 4.1 查看帮助

```bash
python3 experiments/chat/run_chat.py --help
python3 experiments/dpp/run_dpp.py --help
python3 experiments/apr/run_apr.py --help
python3 experiments/trickcatcher/run_trickcatcher.py --help
python3 start/run_baselines.py --help
```

### 4.2 统一入口

如果你希望通过同一个脚本启动多条 baseline，用：

```bash
python3 start/run_baselines.py --baselines chat,apr,dpp,tc --layout dataset --lang cpp
```

只跑其中几条：

```bash
python3 start/run_baselines.py --baselines chat,dpp --layout dataset --lang cpp --pid p02577
```

统一入口会分别调用原来的 runner：

- `chat -> experiments/chat/run_chat.py`
- `apr -> experiments/apr/run_apr.py`
- `dpp -> experiments/dpp/run_dpp.py`
- `tc -> experiments/trickcatcher/run_trickcatcher.py`

并生成：

- `outputs/baseline_runs/summary.csv`
- `outputs/baseline_runs/summary.json`
- `outputs/baseline_runs/summary.txt`
- `outputs/baseline_runs/logs/<baseline>.log`

同时保留各 baseline 自己原有的输出目录：

- `outputs/chat/`
- `outputs/apr/`
- `outputs/dpp/`
- `outputs/trickcatcher/`

### 4.3 单题运行

```bash
python3 experiments/chat/run_chat.py --layout dataset --lang cpp --pid p02577
python3 experiments/dpp/run_dpp.py --layout dataset --lang cpp --pid p02577
python3 experiments/apr/run_apr.py --layout dataset --lang cpp --pid p02577
python3 experiments/trickcatcher/run_trickcatcher.py --lang cpp --pid p02577
```

### 4.4 批量运行

```bash
python3 experiments/chat/run_chat.py --layout dataset --lang cpp
python3 experiments/dpp/run_dpp.py --layout dataset --lang cpp
python3 experiments/apr/run_apr.py --layout dataset --lang cpp
python3 experiments/trickcatcher/run_trickcatcher.py --lang cpp
```


## 5. CHAT Baseline

### 5.1 Goal

`CHAT` baseline 直接做：

1. 读取 `spec.txt`
2. 读取 PUT
3. 构造 direct test generation prompt
4. 调用 LLM 生成候选测试输入
5. 可选经过 checker 校验
6. 用 PUT 和 canonical 执行这些输入
7. 判断是否为 bug-revealing input

### 5.2 Main command

```bash
python3 experiments/chat/run_chat.py \
  --layout dataset \
  --lang cpp \
  --out-root outputs/chat \
  --model deepseek-chat \
  --num-candidates 20 \
  --batch-size 5
```

### 5.3 Important arguments

- `--layout`
  - `dataset` 或 `ac`
- `--pid`
  - 单题运行
- `--lang`
  - `cpp` 或 `py`
- `--dataset-root`
  - 默认 `Datasets/TrickyBugs/PUT_cpp`
- `--canonical-root`
  - 默认 `AC`
- `--out-root`
  - 默认 `outputs/chat`
- `--model`
  - LLM 模型名
- `--num-candidates`
  - 每题目标测试输入数
- `--batch-size`
  - 每次 prompt 让 LLM 产出的 case 数
- `--checker-timeout`
  - checker 超时
- `--skip-checker`
  - 不做合法性校验

### 5.4 Example commands

单题：

```bash
python3 experiments/chat/run_chat.py \
  --layout dataset \
  --lang cpp \
  --pid p02577 \
  --num-candidates 10 \
  --batch-size 5
```

批量：

```bash
python3 experiments/chat/run_chat.py \
  --layout dataset \
  --lang cpp \
  --num-candidates 20 \
  --batch-size 5 \
  --out-root outputs/chat
```

AC layout：

```bash
python3 experiments/chat/run_chat.py \
  --layout ac \
  --lang cpp \
  --ac-root AC \
  --out-root outputs/chat_ac
```

### 5.5 Output meaning

每题目录下：

- `raw_llm_output/`
  - 原始 LLM 响应
- `normalized_tests/`
  - 解析后的标准化测试输入
- `invalid_tests/`
  - checker 不通过的输入和失败原因
- `executions/`
  - 每个测试输入对应的执行结果
- `report.json`
  - 结构化统计
- `report.txt`
  - 便于论文记录的文本摘要

根目录：

- `outputs/chat/summary.csv`
  - 每题一行
- `outputs/chat/summary.json`
  - 整体统计
- `outputs/chat/summary.txt`
  - 人类可读摘要


## 6. DPP Baseline

### 6.1 Goal

`DPP` baseline 是现有 variant-based differential testing 主线的独立封装。

它默认假设你已经有：

- variants
- legal inputs
- canonical solution

### 6.2 Main command

```bash
python3 experiments/dpp/run_dpp.py \
  --layout dataset \
  --lang cpp \
  --out-root outputs/dpp
```

### 6.3 Important arguments

- `--layout`
  - `dataset` / `ac`
- `--pid`
  - 单题运行
- `--variants-root`
  - 默认 `Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp`
- `--tests-root`
  - 默认 `outputs/inputs`
- `--fixed-min-votes`
  - 默认 `6`
- `--prefilter-variants`
  - 启用 variant 预过滤

### 6.4 Example commands

单题：

```bash
python3 experiments/dpp/run_dpp.py \
  --layout dataset \
  --lang cpp \
  --pid p02577 \
  --out-root outputs/dpp
```

批量：

```bash
python3 experiments/dpp/run_dpp.py \
  --layout dataset \
  --lang cpp \
  --out-root outputs/dpp \
  --fixed-min-votes 6
```

AC layout：

```bash
python3 experiments/dpp/run_dpp.py \
  --layout ac \
  --lang cpp \
  --ac-root AC \
  --bundle-dir gen_bundle \
  --variants-dirname variants \
  --out-root outputs/dpp_ac
```

### 6.5 DPP dependency chain

如果你从头开始补数据，通常是：

1. 先生成 variants

```bash
python3 start/run_varProgs_gen.py --layout dataset --mode dpp --lang cpp
```

2. 生成测试输入

```bash
python3 start/run_input_gen.py --backend mixed --dataset-root Datasets/TrickyBugs/PUT_cpp
```

3. checker 清洗

```bash
python3 start/run_check_inputs.py --dataset-root Datasets/TrickyBugs/PUT_cpp --inputs-root outputs/inputs
```

4. 用新的 DPP baseline 入口跑评测

```bash
python3 experiments/dpp/run_dpp.py --layout dataset --lang cpp --out-root outputs/dpp
```

### 6.6 Output meaning

每题目录下：

- `raw.log`
  - 调用 `LLM_Gen/differential_testing.py` 的完整输出
- `detail.csv`
  - 测试用例级别明细
- `summary.json`
  - 结构化摘要
- `report.txt`
  - 文本报告

根目录：

- `summary.csv`
- `summary.json`
- `summary.txt`


## 7. APR Baseline

### 7.1 Goal

`APR` baseline 直接根据：

- `spec`
- PUT

让 LLM 产出 repair candidates，然后：

1. 保存 raw LLM 输出
2. 归一化为完整 repaired program
3. 编译/语法检查
4. 在现有测试输入上执行 repaired candidate / PUT / canonical
5. 判断：
   - 是否 compile 成功
   - 是否能运行
   - 是否改变行为
   - 是否在当前可用测试下看起来修复了 bug

### 7.2 Main command

```bash
python3 experiments/apr/run_apr.py \
  --layout dataset \
  --lang cpp \
  --out-root outputs/apr \
  --model deepseek-chat \
  --num-candidates 5
```

### 7.3 Important arguments

- `--layout`
  - `dataset` / `ac`
- `--pid`
  - 单题运行
- `--tests-root`
  - 默认 `outputs/inputs`
- `--out-root`
  - 默认 `outputs/apr`
- `--num-candidates`
  - 每题 repair candidate 数
- `--timeout`
  - 程序执行超时

### 7.4 Example commands

单题：

```bash
python3 experiments/apr/run_apr.py \
  --layout dataset \
  --lang cpp \
  --pid p02577 \
  --num-candidates 3
```

批量：

```bash
python3 experiments/apr/run_apr.py \
  --layout dataset \
  --lang cpp \
  --num-candidates 5 \
  --out-root outputs/apr
```

AC layout：

```bash
python3 experiments/apr/run_apr.py \
  --layout ac \
  --lang cpp \
  --ac-root AC \
  --out-root outputs/apr_ac
```

### 7.5 Output meaning

每题目录下：

- `raw_llm_output/`
  - 原始 repair 响应
- `candidate_patches/`
  - 归一化后的候选程序
- `compile_logs/`
  - 编译日志
- `executions/`
  - 每个 candidate 的执行评估结果
- `report.json`
  - 结构化统计
- `report.txt`
  - 文本摘要

根目录：

- `summary.csv`
- `summary.json`
- `summary.txt`


## 8. Old Utility Modules

这些模块现在仍然有价值：

### 8.1 Generate generator / checker tools

```bash
python3 start/run_gen_tools.py --tool generator
python3 start/run_gen_tools.py --tool checker
```

### 8.2 Generate direct inputs / mixed inputs

```bash
python3 start/run_input_gen.py --backend llm --pid p02577
python3 start/run_input_gen.py --backend mixed --num 100 --llm-num 10
```

### 8.3 Validate generated inputs

```bash
python3 start/run_check_inputs.py --dataset-root Datasets/TrickyBugs/PUT_cpp
```

### 8.4 Generate variants

```bash
python3 start/run_varProgs_gen.py --layout dataset --mode dpp --lang cpp
python3 start/run_varProgs_gen.py --layout dataset --mode tc --lang cpp
```

### 8.5 Old differential testing entry

```bash
python3 start/run_dif_test.py --layout dataset --lang cpp
```

说明：

- 旧入口仍可用
- thesis 写作和 baseline 分组建议优先使用新的 `experiments/*/run_*.py`


## 9. Recommended Thesis Workflow

如果你要做可写论文的对比实验，建议按下面方式组织：

### 9.1 CHAT

```bash
python3 experiments/chat/run_chat.py --layout dataset --lang cpp --out-root outputs/chat
```

### 9.2 DPP

```bash
python3 start/run_varProgs_gen.py --layout dataset --mode dpp --lang cpp
python3 start/run_input_gen.py --backend mixed --dataset-root Datasets/TrickyBugs/PUT_cpp
python3 start/run_check_inputs.py --dataset-root Datasets/TrickyBugs/PUT_cpp
python3 experiments/dpp/run_dpp.py --layout dataset --lang cpp --out-root outputs/dpp
```

### 9.3 APR

```bash
python3 experiments/apr/run_apr.py --layout dataset --lang cpp --out-root outputs/apr
```

### 9.4 Comparison

查看：

- `outputs/chat/summary.csv`
- `outputs/dpp/summary.csv`
- `outputs/apr/summary.csv`
- `outputs/experiment_comparison.csv`


## 10. Current Known Limitations

- `CHAT` 和 `APR` 会真实依赖 LLM API 环境
- `APR` 当前生成的是完整 repaired program，不是 diff patch
- `APR` 的 fix 判断是“在当前可用测试下 apparent fix”，不是形式化正确性证明
- `DPP` 目前最稳定，因为直接复用了已有主线
- `outputs/experiment_comparison.csv` 目前是 baseline-level 对照，不是完整论文统计总表


## 11. Quick Smoke-Test Commands

如果你只想快速验证结构而不立刻大规模跑：

```bash
python3 experiments/chat/run_chat.py --help
python3 experiments/dpp/run_dpp.py --help
python3 experiments/apr/run_apr.py --help
```

DPP 单题烟测：

```bash
python3 experiments/dpp/run_dpp.py --layout dataset --lang cpp --pid p02577 --out-root outputs/dpp_test
```

运行后检查：

```bash
cat outputs/dpp_test/summary.csv
cat outputs/dpp_test/summary.txt
```


## 12. Suggested Writing Mapping

论文中可以这样表述：

- `CHAT baseline`
  - direct LLM test input generation from specification and PUT
- `DPP baseline`
  - variant-based differential oracle construction with fixed 6-vote threshold
- `APR baseline`
  - LLM-based repair candidate generation and repair-oriented evaluation

这样三条线在代码结构、入口、输出、报告上都已经可以独立叙述。
