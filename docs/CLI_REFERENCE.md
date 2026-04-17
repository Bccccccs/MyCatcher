







# MyCatcher 命令参数参考

本文档是对仓库内主要命令行入口的独立说明，基于当前代码中的 `argparse` 定义整理，不覆盖现有 [README.md](/Users/bcccccc/PycharmProjects/MyCatcher/README.md)。

适用范围：

- `start/` 目录下主要实验入口脚本
- 根目录的辅助汇总脚本
- `src/run_clean.py` 清理脚本

不包含内容：

- `LLM_Gen/` 内部模块的全部细节参数
- 每个问题目录下自动生成的 `input_gen.py`
- 非命令行入口的内部函数

## 约定

- “默认值”表示不传该参数时脚本使用的值。
- “dataset layout” 通常指 `Datasets/TrickyBugs/PUT_cpp/<pid>/...`
- “AC layout” 通常指 `AC/<pid>/...`
- 路径参数如果写相对路径，默认相对仓库根目录解析。

## 1. `start/run_gen_io_tools.py`

用途：批量生成两个辅助文件。

- `input_gen.py`
- `check_input.py`

这个脚本本身是兼容包装器，内部等价于：

```bash
python3 start/run_gen_tools.py --tool both
```

### 参数

无自定义参数。

### 适用场景

- 你只想“一次性同时生成 generator 和 checker”
- 不关心更细粒度控制

## 2. `start/run_gen_tools.py`

用途：从 `spec.txt` 生成输入生成器和输入检查器。

### 命令格式

```bash
python3 start/run_gen_tools.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--tool` | `generator` \| `checker` \| `both` | `both` | 生成哪类工具 |
| `--pid` | 字符串 | `None` | 单个问题 id，如 `p02547` |
| `--spec` | 路径 | `None` | 单个 `spec.txt` 路径；传入后只处理一个问题 |
| `--dataset-root` | 路径 | `Datasets/TrickyBugs/PUT_cpp` | 批量模式下的问题根目录 |
| `--generator-template` | 字符串 | `geninput_generator` | 生成 `input_gen.py` 用的 prompt template |
| `--checker-template` | 字符串 | `geninput_inspector` | 生成 `check_input.py` 用的 prompt template |
| `--generator-out` | 路径/文件名 | `input_gen.py` | generator 输出位置 |
| `--checker-out` | 路径/文件名 | `check_input.py` | checker 输出位置 |
| `--model` | 字符串 | `deepseek-chat` | 调用的模型名 |

### 参数语义补充

- `--tool`
  - `generator`：只生成 `input_gen.py`
  - `checker`：只生成 `check_input.py`
  - `both`：两者都生成
- `--pid`
  - 单问题模式
  - 会处理 `--dataset-root/<pid>/spec.txt`
- `--spec`
  - 单问题模式
  - 如果不传，则遍历 `--dataset-root` 下每个问题目录，查找 `<pid>/spec.txt`
- `--generator-out` / `--checker-out`
  - 如果只传文件名，如 `input_gen.py`，会写到 `spec.txt` 同目录
  - 如果传绝对路径，则写到绝对路径
  - 如果传带目录的相对路径，则按仓库根目录解析

### 行为约束

- `--pid` 和 `--spec` 互斥，不能同时传。
- 如果目标输出文件已经存在，脚本会跳过，不覆盖。
- 批量模式下缺少 `spec.txt` 的目录会被统计为 `missing_spec`，不会报错中断。

### 常用例子

```bash
python3 start/run_gen_tools.py --tool both
python3 start/run_gen_tools.py --tool generator --pid p02547
python3 start/run_gen_tools.py --tool generator --spec Datasets/TrickyBugs/PUT_cpp/p02547/spec.txt
python3 start/run_gen_tools.py --tool checker --checker-template geninput_inspector
```

## 3. `start/run_input_gen.py`

用途：生成 `test_*.in` 测试输入。

支持三种后端：

- `generator`：调用每题目录下已有的 `input_gen.py`
- `llm`：直接调用 `LLM_Gen.input_generator`
- `mixed`：先生成随机输入，再补充 LLM 边界输入

### 命令格式

```bash
python3 start/run_input_gen.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--backend` | `generator` \| `llm` \| `mixed` | `mixed` | 输入生成模式 |
| `--pid` | 字符串 | `None` | 单个问题 id，如 `p02547` |
| `--spec` | 路径 | `None` | 单个 `spec.txt` 路径 |
| `--put` | 路径 | `None` | 单问题 LLM 模式下的 PUT 路径 |
| `--dataset-root` | 路径 | `Datasets/TrickyBugs/PUT_cpp` | 批量模式问题根目录 |
| `--out-root` | 路径 | `outputs/inputs` | 测试输入输出根目录 |
| `--generator-name` | 文件名 | `input_gen.py` | generator 后端要调用的脚本文件名 |
| `--seed` | 整数 | `2` | 传给 `input_gen.py` 的随机种子 |
| `--template` | 字符串/路径 | `PromptTemplates/geninput_direct` | LLM prompt template |
| `--model` | 字符串 | `deepseek-chat` | LLM 模型名 |
| `--num` | 整数 | `100` | 目标输入总数 |
| `--random-num` | 整数 | `None` | mixed 模式下 generator 生成的数量 |
| `--llm-num` | 整数 | `10` | mixed 模式下 LLM 生成的数量 |
| `--jobs` | 整数 | `4` | 批量模式并行问题数 |

### 参数关系

- `--pid` 和 `--spec` 互斥，不能同时传。
- `--random-num` 只在 `mixed` 模式下有意义。
- `mixed` 模式默认：
  - `random-num = num - llm-num`
  - 所以默认是 `90 + 10 = 100`
- 如果 `mixed` 下 `llm-num > num` 且没显式设置 `random-num`，脚本会报错。

### 自动推断逻辑

- `llm` 或 `mixed` 模式下，如果不传 `--put`，脚本会自动在问题目录中找：
  - `put`
  - `put.py` / `put.cpp`
  - `sol_*.cpp` / `sol_*.py`
- 输出目录为：
  - `outputs/inputs/<pid>/`

### 跳过条件

- 如果目标目录现有 `.in` 文件数量已经达到目标数，脚本会直接跳过该问题。

### 常用例子

```bash
python3 start/run_input_gen.py --backend generator
python3 start/run_input_gen.py --backend llm --pid p02547
python3 start/run_input_gen.py --backend mixed --num 100 --llm-num 20
python3 start/run_input_gen.py --backend llm --spec Datasets/TrickyBugs/PUT_cpp/p02547/spec.txt
```

## 4. `start/run_check_inputs.py`

用途：对生成好的输入运行 `check_input.py`，删除非法输入，并输出检查日志。

### 命令格式

```bash
python3 start/run_check_inputs.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--spec` | 路径 | `None` | 单个 `spec.txt` 路径 |
| `--dataset-root` | 路径 | `Datasets/TrickyBugs/PUT_cpp` | 批量模式数据集根目录 |
| `--checker-name` | 文件名 | `check_input.py` | 每题目录中 checker 文件名 |
| `--inputs-root` | 路径 | `outputs/inputs` | 输入根目录 |
| `--max` | 整数 | `None` | 最大输入编号，含上界；不传时按默认比例检查 |
| `--start` | 整数 | `0` | 起始输入编号 |
| `--timeout` | 浮点数 | `10.0` | 每次 checker 运行超时秒数 |
| `--jobs` | 整数 | `8` | 单题内并行检查输入文件的线程数 |
| `--log-name` | 文件名 | `checker_log.txt` | 单题日志文件名 |
| `--summary-log` | 路径 | `outputs/checker_logs/summary.txt` | 批量总日志路径 |

### 参数语义补充

- `--spec`
  - 单题模式
  - 此时 checker 路径是 `spec.txt` 同目录下的 `check_input.py`
- `--inputs-root`
  - 批量模式下使用 `outputs/inputs/<pid>/`
  - 单题模式下当前实现直接把它当作输入目录本身使用
- `--start` 与 `--max`
  - 实际检查 `test_<idx>.in`
  - 传了 `--max` 时，范围是 `[start, max]`
  - 不传 `--max` 时，默认只检查当前题目前 `9/10` 的输入，保留后 `1/10` 不动

### 约束

- 要求 `0 <= start <= max`
- 要求 `jobs >= 1`

### 删除逻辑

- `check_input.py` 返回码为 `0`：保留
- 非 `0`：
  - 如果看起来是 checker 自身代码错误，记录为 `checker_error`，不当成输入非法删除原因
  - 否则删除对应输入文件
- checker 超时：直接删除该输入

### 输出

- 单题：在输入目录写 `checker_log.txt`
- 批量：
  - 每题一个 `checker_log.txt`
  - 总结写到 `outputs/checker_logs/summary.txt`

### 常用例子

```bash
python3 start/run_check_inputs.py
python3 start/run_check_inputs.py --spec Datasets/TrickyBugs/PUT_cpp/p02547/spec.txt
python3 start/run_check_inputs.py --start 0 --max 49 --jobs 16
```

## 5. `start/run_varProgs_gen.py`

用途：生成 LLM program variants。

支持两种目录布局：

- `dataset`
- `ac`

支持两种生成模式：

- `dpp`：只用题面/规格
- `tc`：题面/规格 + 参考程序

### 命令格式

```bash
python3 start/run_varProgs_gen.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--layout` | `dataset` \| `ac` | `dataset` | 目录布局 |
| `--pid` | 字符串 | `None` | 单题 id |
| `--spec.txt` | 路径 | `None` | dataset 单题模式下直接指定 spec |
| `--put` | 路径 | `None` | dataset 单题模式下直接指定 PUT |
| `--mode` | `dpp` \| `tc` | `dpp` | 生成模式 |
| `--lang` | `py` \| `cpp` | `cpp` | 目标语言 |
| `--template` | 路径 | `None` | 显式指定 prompt template |
| `--naming` | `default` \| `trickybugs` | `None` | 输出文件命名风格 |
| `--k` | 整数 | `10` | 生成 variants 数量 |
| `--index-start` | 整数 | `0` | 变体文件编号起点 |
| `--model` | 字符串 | `deepseek-chat` | LLM 模型 |
| `--sleep` | 浮点数 | `0.2` | 每次 LLM 调用间隔秒数 |
| `--dataset-root` | 路径 | `Datasets/TrickyBugs/PUT_cpp` | dataset layout 根目录 |
| `--out-root` | 路径 | `None` | dataset layout 共享输出根目录 |
| `--ac-root` | 路径 | `AC` | AC layout 根目录 |
| `--spec-name` | 文件名 | `spec.txt` | AC layout 下规格文件名 |
| `--put-name` | 文件名 | `None` | AC layout 下 PUT 文件名 |
| `--bundle-dir` | 文件名 | `gen_bundle` | AC layout bundle 目录名 |
| `--variants-dirname` | 文件名 | `variants` | AC layout 下 variants 子目录名 |

### 默认模板选择

- `mode=dpp` 且未传 `--template`：
  - 使用 `PromptTemplates/genprog_dfp`
- `mode=tc` 且未传 `--template`：
  - 使用 `PromptTemplates/genprog_tc`

### dataset layout 下的关键规则

- `--pid` 与 `--spec.txt` 互斥。
- `mode=tc` 时必须能找到 PUT：
  - 若未传 `--put`，会自动查找题目目录中的 `put.cpp` / `put.py` / `sol_*.cpp` / `sol_*.py`
- 若不传 `--out-root`，脚本会自动推断：
  - TrickyBugs + `cpp` + `dpp` 时，默认类似：
    - `Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp`

### AC layout 下的关键规则

- 不允许使用：
  - `--spec.txt`
  - `--put`
  - `--out-root`
- 输出目录固定为：
  - `AC/<pid>/<bundle-dir>/<variants-dirname>/`
- `mode=tc` 时：
  - 若未传 `--put-name`，会尝试自动找 `ac_sol.cpp` / `put.cpp` 等

### naming 规则

- `--naming trickybugs`
  - 文件名前缀通常按 `p02547_num` 这种风格生成
- 如果不显式传：
  - dataset + TrickyBugs 通常自动推断为 `trickybugs`
  - ac 布局默认直接使用 `trickybugs`

### 常用例子

```bash
python3 start/run_varProgs_gen.py --layout dataset
python3 start/run_varProgs_gen.py --layout dataset --pid p02547
python3 start/run_varProgs_gen.py --layout dataset --mode tc --pid p02547
python3 start/run_varProgs_gen.py --layout ac --pid p02730
```

## 6. `start/run_object_sol_gen.py`

用途：为题目生成 object/canonical 风格解法。

### 命令格式

```bash
python3 start/run_object_sol_gen.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--pid` | 字符串 | `None` | 单题 id |
| `--dataset-root` | 路径 | `Datasets/TrickyBugs/PUT_cpp` | 数据集根目录 |
| `--template` | 路径/模板名 | `PromptTemplates/genprog_dfp` | prompt template |
| `--model` | 字符串 | `deepseek-chat` | LLM 模型 |
| `--out-name` | 文件名 | `object_sol.cpp` | 输出文件名 |
| `--sleep` | 浮点数 | `0.2` | 每题调用之间的休眠时间 |
| `--force` | 开关 | 关闭 | 是否覆盖已有输出 |

### 行为说明

- 单题模式：只处理 `dataset-root/<pid>/`
- 批量模式：遍历所有包含 `spec.txt` 的问题目录
- 如果输出文件已存在且内容非空：
  - 默认跳过
  - 只有传 `--force` 才会覆盖

### 常用例子

```bash
python3 start/run_object_sol_gen.py --pid p02547
python3 start/run_object_sol_gen.py --out-name ac_sol.cpp --force
```

## 7. `start/run_dif_test.py`

用途：差分测试主入口。

支持：

- dataset layout
- AC layout
- fixed voting 与 dynamic voting
- variant prefilter

### 命令格式

```bash
python3 start/run_dif_test.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--layout` | `dataset` \| `ac` | `dataset` | 目录布局 |
| `--pid` | 字符串 | `None` | 单题 id |
| `--lang` | `py` \| `cpp` | `cpp` | 语言 |
| `--variant-mode` | `my` \| `trickybugs` | `trickybugs` | 变体文件命名约定 |
| `--dataset-root` | 路径 | `Datasets/TrickyBugs/PUT_cpp` | dataset 问题根目录 |
| `--variants-root` | 路径 | `Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp` | dataset 变体根目录 |
| `--out-root` | 路径 | `outputs/tcases` | dataset 模式下输出根目录 |
| `--canonical-root` | 路径 | `AC` | dataset 模式下 canonical 根目录 |
| `--canonical-name` | 文件名 | `None` | canonical 文件名 |
| `--ac-root` | 路径 | `AC` | AC layout 根目录 |
| `--put-name` | 文件名 | `None` | AC layout 下待测程序文件名 |
| `--bundle-dir` | 文件名 | `gen_bundle` | AC layout bundle 目录名 |
| `--variants-dirname` | 文件名 | `variants` | AC layout 下 variants 目录名 |
| `--out-dirname` | 文件名 | `tcases` | AC layout 下输出目录名 |
| `--tests-root` | 路径 | `outputs/inputs` | 测试输入根目录 |
| `--timeout` | 浮点数 | `2.0` | 单程序运行超时 |
| `--min-votes` | 整数 | `None` | legacy fixed threshold |
| `--fixed-min-votes` | 整数 | `6` | fixed voting 阈值 |
| `--dynamic-min-variant-outputs` | 整数 | `6` | dynamic voting 接受前要求的最少成功 variant 输出数 |
| `--prefilter-variants` | 开关 | 关闭 | 启用预过滤 |
| `--prefilter-sample-size` | 整数 | `20` | 预过滤抽样输入数 |
| `--prefilter-max-fail-rate` | 浮点数 | `0.2` | 预过滤允许的最大失败率 |
| `--prefilter-max-mismatch-rate` | 浮点数 | `0.3` | 预过滤允许的最大与 canonical 不一致率 |
| `--prefilter-min-keep` | 整数 | `3` | 若通过过滤的 variant 太少，则回退到不过滤 |
| `--jobs` | 整数 | `8` | 并行处理问题数 |

### 参数分组说明

#### dataset layout 相关

- 生效参数：
  - `--dataset-root`
  - `--variants-root`
  - `--out-root`
  - `--canonical-root`
  - `--canonical-name`
- 输出根目录实际为：
  - `<out-root>/<lang>/`

#### AC layout 相关

- 生效参数：
  - `--ac-root`
  - `--put-name`
  - `--bundle-dir`
  - `--variants-dirname`
  - `--out-dirname`
  - `--canonical-name`

#### 投票参数

- `--fixed-min-votes`
  - fixed baseline 的票数阈值
- `--dynamic-min-variant-outputs`
  - dynamic voting 在做“过半判断”前，要求至少有多少个 variant 成功输出
- `--min-votes`
  - 兼容旧逻辑保留，不建议作为新实验主参数

#### prefilter 参数

- 只有开启 `--prefilter-variants` 后才真正参与控制
- 含义：
  - 先在抽样输入上跑 canonical 与 variants
  - 移除失败率过高或与 canonical 不一致率过高的 variants

### 输入前置要求

- `--tests-root` 必须存在
- dataset 模式下：
  - `dataset-root`
  - `variants-root`
  - `canonical-root`
  都必须存在
- ac 模式下：
  - `ac-root` 必须存在

### 常用例子

```bash
python3 start/run_dif_test.py --layout dataset
python3 start/run_dif_test.py --layout dataset --pid p02547 --jobs 1
python3 start/run_dif_test.py --layout dataset --prefilter-variants
python3 start/run_dif_test.py --layout ac --pid p02730
```

## 8. `start/run_ac_oracle_compare.py`

用途：用 accepted solution 在合法输入上重跑，和差分测试保存下来的 oracle 输出做对比。

### 命令格式

```bash
python3 start/run_ac_oracle_compare.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--pid` | 字符串 | `None` | 单题 id |
| `--ac-root` | 路径 | `AC` | accepted solutions 根目录 |
| `--inputs-root` | 路径 | `outputs/inputs` | 合法输入根目录 |
| `--oracle-root` | 路径 | `outputs/tcases/cpp` | 差分测试报告根目录 |
| `--out-root` | 路径 | `outputs/ac_oracle_compare/cpp` | 实际输出和对比报告保存目录 |
| `--put-name` | 文件名 | `None` | AC/<pid>/ 中正确解文件名 |
| `--lang` | `py` \| `cpp` | `cpp` | 语言 |
| `--timeout` | 浮点数 | `2.0` | 单次程序运行超时 |

### 路径约定

- 输入：
  - `<inputs-root>/<pid>/test_*.in`
- 差分测试报告：
  - `<oracle-root>/<pid>/report.txt`
- 输出：
  - `<out-root>/<pid>/actual_outputs/*.out`
  - `<out-root>/<pid>/report.txt`

### 自动查找正确解

- 若不传 `--put-name`，会按语言自动尝试：
  - C++：`ac_sol.cpp`、`put.cpp`、`ac_sol`
  - Python：`ac_sol.py`、`put.py`、`ac_sol`

### 常用例子

```bash
python3 start/run_ac_oracle_compare.py --pid p02547
python3 start/run_ac_oracle_compare.py --oracle-root outputs/tcases/cpp --out-root outputs/ac_oracle_compare/cpp
```

## 9. `start/report_summary.py`

用途：解析每题 `report.txt`，生成紧凑汇总 CSV。

### 命令格式

```bash
python3 start/report_summary.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--report-root` | 路径 | `outputs/tcases/cpp` | 含 `<pid>/report.txt` 的目录 |
| `--out` | 路径 | `outputs/tcases/cpp/report_status_summary.csv` | 输出 CSV 路径 |

### 输出内容

会聚合：

- `status_*`
- `label_*`
- `saved`
- `tp_count`
- `fp_count`
- `oracle_wrong_count`
- `canonical_fail_count`
- `precision`
- `fixed_*`

并额外生成一行 `TOTAL`。

### 常用例子

```bash
python3 start/report_summary.py
python3 start/report_summary.py --report-root outputs/tcases/cpp --out outputs/tcases/cpp/report_status_summary.csv
```

## 10. `start/baseline_summary.py`

用途：基于已有 `summary.json` 和 `detail.csv` 生成更稳定的分析工件。

### 命令格式

```bash
python3 start/baseline_summary.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--report-root` | 路径 | `outputs/tcases/cpp` | 含 `<pid>/summary.json` 和 `detail.csv` 的目录 |
| `--out-dir` | 路径 | `outputs/summary` | 汇总产物目录 |
| `--compiler` | 字符串 | `g++-15` | canonical 编译检查使用的编译器 |
| `--skip-compile-check` | 开关 | 关闭 | 是否跳过 canonical 编译检查 |

### 主要输出

- `baseline_dpp_per_problem.csv`
- `baseline_dpp_global.txt`
- `baseline_dpp_global.csv`
- `baseline_dpp_test_cases.csv`
- `baseline_dpp_unclassified_found.csv`
- `baseline_dpp_canonical_anomalies.csv`
- `baseline_dpp_high_fp_analysis.csv`

### 参数语义补充

- `--compiler`
  - 只用于“可选的 canonical 编译检查”
  - 对已有差分测试结果本身不产生影响
- `--skip-compile-check`
  - 开启后不再调用编译器验证 canonical 是否能编译

### 常用例子

```bash
python3 start/baseline_summary.py
python3 start/baseline_summary.py --out-dir outputs/summary
python3 start/baseline_summary.py --compiler g++ --skip-compile-check
```

## 11. `start/sync_problem_pool.py`

用途：把同时存在于 `problems/` 和原始数据集目录中的题目同步到当前实验目录。

### 命令格式

```bash
python3 start/sync_problem_pool.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--limit` | 整数 | `None` | 只同步前 N 个匹配题目 |
| `--pid` | 可重复字符串参数 | `None` | 只同步指定 pid；可重复多次 |
| `--manifest` | 路径 | `outputs/manifests/problem_pool_sync.json` | manifest 输出路径 |

### 参数语义补充

- `--pid` 可以多次写，例如：

```bash
python3 start/sync_problem_pool.py --pid p02547 --pid p02730
```

- 同步内容包括：
  - `Datasets/TrickyBugs/PUT_cpp/<pid>`
  - `Datasets/TrickyBugs/GenProgs/dpp_generated_progs_cpp/<pid>`
  - `AC/<pid>/ac_sol.cpp`

### 拷贝策略

- 目标存在时跳过，不覆盖
- canonical source 会优先从：
  - `reference_programs/sol_*.cpp`
  - 否则 `fixed_programs/cpp/sol_*.cpp`
  中选取

## 12. `src/run_clean.py`

用途：清理实验产物、自动生成工具和缓存。

注意：文件实际位于 `src/run_clean.py`，不是 `start/`。

### 命令格式

```bash
python3 src/run_clean.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--scope` | `inputs` \| `outputs` \| `all` | `all` | 清理范围 |

### scope 含义

- `inputs`
  - 只清 `outputs/inputs`
- `outputs`
  - 清 `outputs/inputs`
  - 清 `outputs/tcases`
- `all`
  - 清 `outputs/inputs`
  - 清 `outputs/tcases`
  - 删除自动生成的 `input_gen.py` / `check_input.py`
  - 删除缓存目录，如 `__pycache__`

### 风险说明

- 这是破坏性操作。
- `scope=all` 会删除数据集目录下自动生成的工具文件。

### 常用例子

```bash
python3 src/run_clean.py --scope inputs
python3 src/run_clean.py --scope outputs
python3 src/run_clean.py --scope all
```

## 13. `merge_reports_with_spec.py`

用途：把每题 `report.txt` 和对应 `spec.txt` 合并成一个总文档。

### 命令格式

```bash
python3 merge_reports_with_spec.py [参数]
```

### 参数列表

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--report-root` | 路径 | `outputs/tcases/cpp` | 报告根目录 |
| `--spec-root` | 路径 | `Datasets/TrickyBugs/PUT_cpp` | 规格根目录 |
| `--output` | 路径 | `outputs/tcases/cpp/batch_report_with_spec.txt` | 合并输出文件 |

### 输入约定

- 报告路径：
  - `<report-root>/<pid>/report.txt`
- 规格路径：
  - `<spec-root>/<pid>/spec.txt`

### 行为说明

- 仅遍历那些“目录内存在 `report.txt`”的题目
- 如果某个 spec 或 report 缺失，会在合并文档里写入 `[MISSING]`

### 常用例子

```bash
python3 merge_reports_with_spec.py
python3 merge_reports_with_spec.py --report-root outputs/tcases/cpp --spec-root Datasets/TrickyBugs/PUT_cpp
```

## 常见参数模式总结

### 单题运行常见写法

- 用 `--pid p02547`
- 或直接用 `--spec path/to/spec.txt`

注意：

- 不是每个脚本都同时支持 `--pid` 和 `--spec`
- `run_input_gen.py` 中 `--pid` 和 `--spec` 互斥
- `run_varProgs_gen.py` 中是 `--pid` 和 `--spec.txt` 互斥

### 路径类参数常见结构

- dataset 输入根：
  - `Datasets/TrickyBugs/PUT_cpp`
- AC 根：
  - `AC`
- 测试输入根：
  - `outputs/inputs`
- 差分测试输出根：
  - `outputs/tcases`

### 并行参数

- `run_input_gen.py --jobs`
  - 批量模式下并行处理问题
- `run_check_inputs.py --jobs`
  - 单题内部并行检查输入文件
- `run_dif_test.py --jobs`
  - 并行处理问题

### 覆盖/跳过策略

- `run_gen_tools.py`
  - 已有文件时跳过
- `run_gen_io_tools.py`
  - 通过 `run_gen_tools.py`，同样跳过已有文件
- `run_object_sol_gen.py`
  - 默认跳过已有输出，传 `--force` 才覆盖
- `sync_problem_pool.py`
  - 已存在目标时跳过

## 建议阅读顺序

如果你是第一次跑整套流程，建议按这个顺序看命令：

1. `start/run_gen_io_tools.py`
2. `start/run_input_gen.py`
3. `start/run_check_inputs.py`
4. `start/run_varProgs_gen.py`
5. `start/run_dif_test.py`
6. `start/report_summary.py`
7. `start/baseline_summary.py`

## 备注

如果你后面还想要，我可以继续补两类文档：

- “每个命令的输入目录结构图”
- “每个命令的参数组合推荐模板”
