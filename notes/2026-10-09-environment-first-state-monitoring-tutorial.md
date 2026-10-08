# 教学 Notes — Environment First × Continuous T-State Monitoring

**Recorded:** 2026-10-09 01:41 Asia/Shanghai (+08:00)  
**Type:** GOD principle tutorial / human decision protocol / SPEC, NOT automated production capability  
**North Star:** Each T creates a better T+1. Purpose is one of Output / Connection / Observation / Recovery.

## 1. 为什么要学这个？

把“在什么地方工作”当成主动的时间和注意力资本配置，而不是无关紧要的背景。一个环境如果让任务迟迟不能启动，应当快速调整，不必把黄金时间投入沉没成本。

关键区分：**State ≠ Environment**。任务未启动，原因可能是任务不清晰、缺工具、外界干扰、精力不足，也可能是环境不匹配。检测 state 是为了行动，不是为了不断自我分析。

## 2. T-State 的最小观测向量

`T = (Intent, Close, FirstAction, Progress, Energy, Friction, Environment, T+1)`

- **Intent**：Output / Connection / Observation / Recovery，四选一。
- **Close**：这一段要交付什么可核验结果？如 CV 版本、提交回执、代码测试、发送前已审阅的邮件草稿。
- **FirstAction**：十分钟内真正能动手的第一步。
- **Progress**：任务是否在推进？思考、阅读、研究也可以算进展，前提是指向当前任务并可解释。
- **Energy / Friction**：睡眠、身体状态、噪音、诱因、工具与上下文切换成本。
- **Environment**：当前地点是否匹配任务？是否有安全合理的替代工作地点？
- **T+1**：下一段在哪里、做什么、第一步是什么？

## 3. State Controller：Observe → Classify → Act → Verify

| 状态 | 触发信号（启发式而非精确测量） | 决策 |
|---|---|---|
| GREEN | 持续有效推进 / 有可解释研究价值 | 不动环境，保护专注 |
| YELLOW | 约 15 分钟仍未启动或进展停滞 | STOP；排除阻碍；启动 10 分钟 micro-action |
| RED | 约 30 分钟仍停滞，或刚修复又连续漂移 | 有可行替代地点就 SWITCH_ENV；否则重设任务 |
| RECOVERY | 计划休息，或低精力/夜深强行工作得不偿失 | 主动恢复，保护 T+1，不算失败 |
| CLOSE | 达成客观终点 | 保存证据，指定下一个 T |

**注意：** 15/30 分钟仅为决策护栏；出现明显漂移可以提前处理，不需机械等待。每分钟反复检测 state 会制造新的分心；在 T 开始、重大转换、明显漂移或终止时检测即可。

## 4. 操作教程：从任务到 Close

**STEP 0 — Preflight（出发前）：** 任务命名 + 定义 Close + 选地点 + 检查工具/插座/网络/电量 + 安排备选。  
**STEP 1 — Start：** 直接做 10 分钟 FirstAction，禁止无限准备。  
**STEP 2 — YELLOW：** 如果启动困难，站起、移除诱因、缩小任务、计时十分钟。  
**STEP 3 — RED：** 修复无效则切换环境；别把“出去逛逛”误当成 SWITCH_ENV。夜深/能量耗尽时切换为 Recovery。  
**STEP 4 — Verify：** 记录真正完成的 artifact 或 blocker，禁止把“打算申请”写成“已申请”。  
**STEP 5 — Better T+1：** 明确下一地点、下一行动以及触发条件。

## 5. 以“申请工作”为例

- Intent：Output。
- Close A：定稿一份岗位匹配的 CV；Close B：确认已提交或写下准确阻碍。
- FirstAction：打开 CV，对照岗位 JD 修改最重要的三处证据。
- 如果 15 分钟没有进入内容编辑：YELLOW → 切成 10 分钟 micro-edit。
- 如果仍 30 分钟未形成有效动作，且附近有合适工作点：RED → 迅速前往该点，不再继续在原环境空耗。
- 如果已是深夜且睡眠不足：RECOVERY → 设定下一段的地点/首动作后休息。
- 验证只看实际 CV 文件、申请回执、邮件草稿等证据，不能靠主观“感觉很努力”。

## 6. Test / Acceptance Scenarios

这些是**合成数据上的决策契约测试**，不是实际状态检测，也不是个人历史的准确分钟级观测。

| ID | Synthetic input | Expected |
|---|---|---|
| T01 | 任务持续推进 | CONTINUE |
| T02 | 15 分钟没有启动 | RESET_10M |
| T03 | 30 分钟没有启动 + 有合适备选地点 | SWITCH_ENV |
| T04 | 30 分钟没启动 + 无合适备选 | RESET_10M（避免无目的移动） |
| T05 | 30 分钟停滞 + 精力耗尽 | RECOVER |
| T06 | 明确计划的 Recovery | RECOVER（不是漂移） |
| T07 | 交付成果已经完成 | CLOSE |
| T08 | 8 分钟内反复出现漂移 + 有备选地点 | SWITCH_ENV（提前处理） |
| T09 | 10 分钟未启动且无其他警讯 | START |
| T10 | 仍在有效研究但没生成文件 | CONTINUE（不误判） |

**Executable reference contract:** `PTime/tests/test_alphatime_environment_spec.py`（PTime 仓库内相对路径 `tests/test_alphatime_environment_spec.py`）。在 PTime 项目根目录执行 `python -m pytest -q tests/test_alphatime_environment_spec.py`。  

**Verified on 2026-10-09 (local sandbox, Python 3.13.5, pytest 9.0.2):** `10 passed in 0.07s`（运行的是与提交相同的独立合成规范脚本）。此通过记录仅验证规范样例的逻辑，不等于 PTime v2.3 已实现监测、更不等于真实生活行为被验证。

## 7. 一分钟复盘模板

```text
Timestamp [Asia/Shanghai +08:00]:
T / Intent:
Environment fit (Yes/No/Unknown):
FirstAction started at:
Progress evidence:
State (GREEN/YELLOW/RED/RECOVERY/CLOSE):
Intervention (RESET_10M / SWITCH_ENV / RECOVER / CONTINUE):
Actual Close / Blocker:
Better T+1 (where / first action):
```

## 8. Exit Criteria

这条原则真正有效的标准不是笔记写得多，而是下一次现实中的任务：
1. 是否更快启动；
2. 是否更早识别并退出低产出的环境；
3. 是否产生了可核验 Close；
4. 是否为 T+1 保存精力与明确行动。

**Boundary:** 当前内容是教学、规则、独立规范测试；不存在自动侦测手机行为/位置/环境的已部署功能。

## 9. PTime 领域边界 / Public-safe Notes

- PTime 仓库当前为 **public**；此处不记录真实住址、交往对象、职业联系、详细个人事件时间线或其他敏感私有日志。
- 这是一项 **behavioral decision SPEC**：不改 `VERSION`，不宣称 v2.3 Markov Chain Discrete-Time Manager 已实现。
- 与 `docs/MARKOV_CHAIN_DISCRETE_TIME_MANAGER.md` 的 T→T+1→T+2 设计一致：状态需包含精力、任务清晰度、环境阻力、睡眠债，Recovery 为合格转移。
- Synthetic tests 只验证可执行参考决策，并不调用 PTime CLI、没有后台定时任务，没有主动读取真实位置或私人数据。
