# MyCatcher

MyCatcher 当前的主复现路径对齐 TrickCatcher 论文
“LLM-Powered Test Case Generation for Detecting Bugs in Plausible Programs”：
核心语义是针对 PUT 先生成程序变体，再基于 `spec.txt` 构造输入生成与校验工具，
然后执行变体式差分测试。

当前主要实验对象是 TrickyBugs 风格的 C++ 问题。

## 论文复现主路径

当前推荐的论文复现入口是：

```bash
.venv/bin/python experiments/trickcatcher/run_trickcatcher.py --lang cpp
```

该入口默认复用现有 variants 数据，不会重新生成 variants。
如果需要显式重跑变体生成，再加：

```bash
.venv/bin/python experiments/trickcatcher/run_trickcatcher.py --lang cpp --run-variant-gen
```

单题运行：

```bash
.venv/bin/python experiments/trickcatcher/run_trickcatcher.py --lang cpp --pid p02594
```

这个入口会按阶段串联已有稳定脚本：

```text
1. 复用已有程序 variants（必要时可显式重新生成）
2. 从 spec.txt 生成 input_gen.py / check_input.py
3. 生成测试输入
4. 检查并过滤非法输入
5. 运行 PUT vs variants 的差分测试
6. 写出每题和全局汇总
```

其中：

```text
experiments/chat/
  直接生成测试输入的 baseline，不是论文主流程。

experiments/apr/
  repair baseline，不是论文主流程。

experiments/dpp/
  保留为差分测试阶段的独立运行入口，但不再作为完整论文复现入口。
```

整体流程如下：

1. 生成或收集候选程序变体。
2. 从 `spec.txt` 生成输入工具并产生测试输入。
3. 校验输入合法性。
4. 在 PUT、生成的 variants 和 canonical solution 之间运行差分测试。
5. 汇总 TP/FP、precision、oracle 错误和 no-majority 情况。

## 项目功能

MyCatcher 提供了一套端到端实验流水线，用于研究一组 LLM 生成程序是否可以共同构成可靠的差分测试 oracle。

主要功能包括：

```text
1. 生成输入工具
   使用 LLM 为每个问题生成 input_gen.py 和 check_input.py。

2. 生成测试输入
   为每个问题生成随机输入、边界输入或混合输入。

3. 校验生成输入
   运行生成的 checker，并自动删除非法输入。

4. 生成程序变体
   使用 LLM 为同一个问题生成多个候选解法 variants。

5. 差分测试
   在同一批输入上运行 PUT 和所有 variants。
   通过 variants 的输出投票推断 oracle output。

6. Oracle 校验
   如果存在 canonical accepted solution，就用它校验投票 oracle 是否正确。

7. 结果分析
   生成每题和全局汇总，包括 TP/FP、precision、no-majority rate、
   oracle-wrong count 和 canonical failure 等指标。
```

项目关注的核心问题是：

```text
LLM 生成的多个程序变体能否共同识别 Online Judge 错误解？
多数投票得到的 oracle 是否足够可靠？
```

## 实验流程总览

典型实验流程如下：

```text
spec.txt
  |
  v
生成程序 variants
  |
  v
生成 input_gen.py 和 check_input.py
  |
  v
生成 test_*.in
  |
  v
检查并清理非法输入
  |
  v
运行差分测试
  |
  v
写出 report.txt / summary.json / detail.csv
  |
  v
聚合并分析结果
```

如果只想走论文主路径，直接运行：

```bash
.venv/bin/python experiments/trickcatcher/run_trickcatcher.py --lang cpp
```

如果 input generators 和 variants 已经存在，兼容性的最小实验流程仍然是：

```bash
python3 start/run_input_gen.py
python3 start/run_check_inputs.py
python3 start/run_dif_test.py --layout dataset
python3 start/report_summary.py
python3 start/baseline_summary.py
```

如果你已经把原论文/原仓库里的输入数据放在 `orgrin_Datasets/`，建议先迁移到当前项目原生格式：

```bash
.venv/bin/python start/import_original_inputs.py --source-kind both --overwrite
```

迁移后这些输入会写到：

```text
outputs/inputs/<pid>/test_000.in
outputs/inputs/<pid>/test_001.in
...
```

这样后续的：

```text
start/run_check_inputs.py
start/run_dif_test.py
experiments/trickcatcher/run_trickcatcher.py --skip-input-gen
```

都可以直接复用这些输入。

只跑单个问题：

```bash
python3 start/run_input_gen.py --pid p02594
python3 start/run_check_inputs.py --spec Datasets/TrickyBugs/PUT_cpp/p02594/spec.txt
python3 start/run_dif_test.py --layout dataset --pid p02594 --jobs 1
```

## 环境配置

如果需要使用 LLM 生成能力，需要在项目根目录创建 `.env` 文件：

```env
OPENAI_API_KEY=sk-xxx
BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat
```

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

C++ 差分测试当前默认使用 `g++-15` 编译。

## 重要目录

```text
AC/
  Canonical accepted solutions 和 specs。

Datasets/TrickyBugs/PUT_cpp/
  Programs under test，也就是待测程序。

Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp/
  LLM 生成的 C++ 程序变体，用作差分测试投票者。

outputs/inputs/
  生成的测试输入，按 problem id 分组。

outputs/tcases/cpp/
  差分测试结果，包括 reports、summaries、details 和保存的触发用例。

start/
  生成、检查、测试和汇总的入口脚本。

LLM_Gen/
  LLM 生成和差分测试的核心实现。
```

## 核心脚本

### 生成输入工具

`start/run_gen_io_tools.py` 为每个问题生成两个辅助文件：

```text
input_gen.py
  随机输入生成器。

check_input.py
  输入合法性检查器。
```

生成文件会写在每个问题目录下，例如：

```text
Datasets/TrickyBugs/PUT_cpp/p02594/input_gen.py
Datasets/TrickyBugs/PUT_cpp/p02594/check_input.py
```

运行：

```bash
python3 start/run_gen_io_tools.py
```

该脚本会跳过已经存在的文件。

### 生成测试输入

`start/run_input_gen.py` 用于生成 `test_*.in` 输入文件。

只使用 `input_gen.py`：

```bash
python3 start/run_input_gen.py --backend generator
```

只使用 LLM 直接生成：

```bash
python3 start/run_input_gen.py --backend llm
```

默认推荐直接使用 LLM 生成 100 个输入：

```bash
python3 start/run_input_gen.py
```

只生成一个问题：

```bash
python3 start/run_input_gen.py --pid p02594
```

重要参数：

```text
--backend generator|llm|mixed
  选择输入生成方式。

--num
  生成输入总数。

--random-num
  mixed 模式下由 input_gen.py 生成的输入数量。

--llm-num
  mixed 模式下由 LLM 生成的边界输入数量。

--out-root
  输入输出根目录。默认是 outputs/inputs。
```

### 检查输入

`start/run_check_inputs.py` 会对生成输入运行 `check_input.py`，并删除非法输入。

检查所有问题：

```bash
python3 start/run_check_inputs.py
```

检查单个问题：

```bash
python3 start/run_check_inputs.py \
  --spec Datasets/TrickyBugs/PUT_cpp/p02594/spec.txt
```

重要参数：

```text
--inputs-root
  输入目录根路径。默认是 outputs/inputs。

--max
  不传时默认只检查当前题目前 9/10 的输入，保留后 1/10 不动；传入后按显式编号范围检查。

--checker-name
  每个问题目录下 checker 的文件名，通常是 check_input.py。

--jobs
  每个问题内部并行检查的输入文件数量。
```

### 生成程序变体

`start/run_varProgs_gen.py` 用于生成 LLM-based program variants。

Dataset layout，全部问题：

```bash
python3 start/run_varProgs_gen.py --layout dataset
```

Dataset layout，单个问题：

```bash
python3 start/run_varProgs_gen.py --layout dataset --pid p02594
```

AC layout：

```bash
python3 start/run_varProgs_gen.py --layout ac --pid p02730
```

重要参数：

```text
--mode dpp|tc
  dpp 使用 problem spec。
  tc 使用 problem spec 和 solution。

--lang py|cpp
  目标语言。

--k
  生成 variants 的数量。

--template
  prompt template 路径。

--naming default|trickybugs
  输出命名方式。

--out-root
  dataset layout 下 variants 的输出根目录。
```

默认 C++ variants 输出目录：

```text
Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp/<pid>/
```

### 生成 Object/Canonical 风格解法

`start/run_object_sol_gen.py` 可以用 LLM 生成 object/canonical 风格的解法。

```bash
python3 start/run_object_sol_gen.py --pid p02594
```

重要参数：

```text
--dataset-root
  包含问题目录的数据集根目录。

--out-name
  生成解法的输出文件名。

--force
  覆盖已经存在的生成文件。
```

## 差分测试

`start/run_dif_test.py` 是主要实验入口。它会对每个问题调用 `LLM_Gen/differential_testing.py`，将原始输出保存到 `raw.log`，并写出批处理报告。

Dataset layout 需要以下结构：

```text
PUT:
  Datasets/TrickyBugs/PUT_cpp/<pid>/sol_*.cpp

Canonical solution:
  AC/<pid>/ac_sol.cpp

Variants:
  Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp/<pid>/*_parsed.cpp

Inputs:
  outputs/inputs/<pid>/test_*.in

Outputs:
  outputs/tcases/cpp/<pid>/
```

AC layout 需要以下结构：

```text
AC/<pid>/spec.txt
AC/<pid>/<solution file>
AC/<pid>/gen_bundle/variants/
outputs/inputs/<pid>/
AC/<pid>/gen_bundle/tcases/
```

运行所有 dataset-layout C++ 问题：

```bash
python3 start/run_dif_test.py --layout dataset
```

运行单个问题：

```bash
python3 start/run_dif_test.py --layout dataset --pid p02594
```

使用单 worker，便于调试：

```bash
python3 start/run_dif_test.py --layout dataset --pid p02594 --jobs 1
```

把结果写到单独目录：

```bash
python3 start/run_dif_test.py \
  --layout dataset \
  --pid p02594 \
  --out-root /tmp/mycatcher_test
```

重要参数：

```text
--layout dataset|ac
  选择目录布局。

--pid
  只运行单个问题。

--lang py|cpp
  程序语言。

--variant-mode my|trickybugs
  variants 文件命名约定。

--timeout
  单个程序的运行超时时间。

--jobs
  并行运行的问题数量。

--fixed-min-votes
  固定投票机制的阈值。默认是 6。

--dynamic-min-variant-outputs
  动态投票机制接受 oracle 前要求的最少有效 variant 输出数。
  默认是 6。

--prefilter-variants
  在投票前启用 variant 质量过滤。
```

## 投票机制

当前差分测试会同时记录两种投票机制：

1. `dynamic`：主状态。`status`、`found`、`tp_count`、`fp_count`、`precision` 默认使用 dynamic 结果。
2. `fixed`：固定票数 baseline。相关结果记录在 `fixed_*` 字段中。

### Fixed Voting

Fixed voting 使用固定投票阈值。

默认值：

```text
fixed_min_votes = 6
```

逻辑：

```text
if votes >= fixed_min_votes:
    fixed_status = AGREE / FOUND / PUT_FAIL
else:
    fixed_status = NO_MAJORITY
```

其中 `votes` 表示产生最常见输出的 variants 数量。

10 个 variants 时的例子：

```text
votes = 6 -> fixed 接受
votes = 5 -> fixed 拒绝，记为 NO_MAJORITY
```

修改固定阈值：

```bash
python3 start/run_dif_test.py \
  --layout dataset \
  --fixed-min-votes 6
```

### Dynamic Voting

Dynamic voting 先要求有足够数量的 variants 成功输出，然后对这些成功输出执行过半投票。

默认值：

```text
dynamic_min_variant_outputs = 6
```

逻辑：

```text
variant_outputs = 成功运行并产生输出的 variants 数量

if variant_outputs < dynamic_min_variant_outputs:
    dynamic_status = NO_MAJORITY
else:
    dynamic_required_votes = variant_outputs // 2 + 1
    if votes >= dynamic_required_votes:
        dynamic_status = AGREE / FOUND / PUT_FAIL
    else:
        dynamic_status = NO_MAJORITY
```

在默认 `dynamic_min_variant_outputs = 6` 时：

```text
variant_outputs = 5  -> 拒绝，NO_MAJORITY
variant_outputs = 6  -> 需要 4 票
variant_outputs = 7  -> 需要 4 票
variant_outputs = 8  -> 需要 5 票
variant_outputs = 9  -> 需要 5 票
variant_outputs = 10 -> 需要 6 票
```

修改动态机制的最少有效输出数：

```bash
python3 start/run_dif_test.py \
  --layout dataset \
  --dynamic-min-variant-outputs 6
```

### 兼容参数

`--min-votes` 仍然可以被 `start/run_dif_test.py` 接受，并传给 `LLM_Gen/differential_testing.py` 作为 legacy fixed threshold。新的实验建议优先使用：

```text
--fixed-min-votes
--dynamic-min-variant-outputs
```

## Report 字段

每个问题输出目录包含：

```text
report.txt
summary.json
detail.csv
raw.log
case_XXXX.in
case_XXXX.oracle
case_XXXX.put
```

`report.txt` 和 `detail.csv` 中重要的单测试字段：

```text
votes
  给最常见输出投票的 variants 数量。

variant_total
  当前问题加载的 variants 总数。

variant_outputs
  当前测试中成功产生输出的 variants 数量。

required_votes
  主状态使用的 dynamic threshold。

dynamic_status
  dynamic 投票机制下的状态。

dynamic_required_votes
  根据 variant_outputs 计算出的 dynamic majority threshold。

fixed_status
  fixed 投票机制下的状态。

fixed_required_votes
  fixed threshold，默认是 6。

final_label
  dynamic voting 下的 TP/FP/NOT_FOUND 等标签。

fixed_final_label
  fixed voting 下的 TP/FP/NOT_FOUND 等标签。
```

`summary.json` 中的重要字段：

```text
found, no_majority, tp_count, fp_count, precision
  dynamic voting 的主指标。

fixed_found, fixed_no_majority, fixed_tp_count, fixed_fp_count, fixed_precision
  fixed voting baseline 指标。

oracle_wrong_count
  被选择的 oracle 与 canonical solution 不一致的测试数量。

canonical_fail_count
  canonical solution 失败或超时的测试数量。
```

## 汇总结果

项目里有两个汇总脚本，用途不同。

`start/report_summary.py` 解析 `report.txt`，生成紧凑 CSV，适合快速比较每个问题的 status counts 和 precision。

生成 CSV summary：

```bash
python3 start/report_summary.py \
  --report-root outputs/tcases/cpp \
  --out outputs/tcases/cpp/report_status_summary.csv
```

如果 `report.txt` 中包含 dynamic 和 fixed 指标，输出 CSV 也会包含两套指标。

`start/baseline_summary.py` 读取 `summary.json` 和 `detail.csv`，生成更稳定的分析结果，包括异常问题报告。

生成 baseline summary：

```bash
python3 start/baseline_summary.py \
  --report-root outputs/tcases/cpp \
  --out-dir outputs/summary
```

`outputs/summary/` 下典型输出包括：

```text
per_problem.csv
  每个问题一行，包含 found/no_majority/TP/FP/precision 等指标。

global_summary.txt
  全局总数和 global precision。

high_fp.csv
  FP 相对 TP 偏高的问题。

canonical_issues.csv
  canonical 编译、运行或输出异常的问题。
```

## Oracle 对比

`start/run_ac_oracle_compare.py` 会在合法输入上运行 accepted solutions，并将 accepted-solution output 与差分测试保存的 oracle output 对比。

```bash
python3 start/run_ac_oracle_compare.py \
  --pid p02594 \
  --inputs-root outputs/inputs \
  --oracle-root outputs/tcases/cpp \
  --out-root outputs/ac_oracle_compare/cpp \
  --lang cpp
```

该脚本适合用于分析 false positives 的来源，例如：

```text
1. majority-voted oracle 错误。
2. canonical solution 本身异常。
3. 输出比较或 normalization 有问题。
4. PUT 确实存在 bug。
```

## Variant Prefilter

差分测试支持在投票前使用 canonical solution 对 variants 做预过滤。

```bash
python3 start/run_dif_test.py \
  --layout dataset \
  --prefilter-variants \
  --prefilter-sample-size 20 \
  --prefilter-max-fail-rate 0.2 \
  --prefilter-max-mismatch-rate 0.3 \
  --prefilter-min-keep 3
```

prefilter 会移除在 sample tests 上经常运行失败或经常与 canonical 不一致的 variants。它可以减少由坏 variants 导致的投票噪声和 `NO_MAJORITY`，但也可能降低 voter diversity。

## 推荐实验方式

比较投票策略时，建议使用固定参数跑同一批问题：

```bash
python3 start/run_dif_test.py \
  --layout dataset \
  --fixed-min-votes 6 \
  --dynamic-min-variant-outputs 6
```

然后检查每个问题的 `summary.json`，或聚合结果：

```bash
python3 start/report_summary.py
```

建议同时观察以下指标：

```text
no_majority
found
tp_count
fp_count
precision
fixed_no_majority
fixed_found
fixed_tp_count
fixed_fp_count
fixed_precision
oracle_wrong_count
```

实验目标不只是降低 `NO_MAJORITY`，还要避免因为 oracle 质量下降导致 false positives 大幅增加。
