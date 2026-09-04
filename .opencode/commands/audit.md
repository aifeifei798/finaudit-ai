---
description: 闪电排雷模式 — 快速检测财务与治理高危风险
agent: black-account-checker
---

针对 $ARGUMENTS 执行闪电排雷 (与 audit.json 同义，Markdown 入口)。

请调用 `black-account-checker`、`quantitative-fraud-metrics`、`governance-redflags-skill`，输入 `workspace/targets/{TICKER}_{PERIOD}/raw/`，2 分钟内出具《财务与治理高危风险排雷体检单》。

必查：M-Score (灰区即预警) / 现金债悖论 / 股权质押 (分市场阈值) / 审计意见 / CFO 异动。
输出：`workspace/targets/{TICKER}_{PERIOD}/extracted/_audit_flash.md` + 更新 `pipeline-state.json {fraud_metrics}`。
