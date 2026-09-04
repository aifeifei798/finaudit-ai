---
description: 全流程重型研报 — 18 Agent 闭环交付 (含欺诈检测与双HITL+独立QA)
agent: orchestrator
---

针对 $ARGUMENTS 执行全流程重型研报 (与 report.json v1.2.0 同义，Markdown 入口)。

0. screen 消歧采集；1. 解析+证据柜登记；2. 黑账流水+M-Score+治理；3. 对账+Pre-Valuation HITL (`gate-keeper` 签收)；
4. peer+宏观+ESG，情绪旁路；5. DCF+情景+活表图表；6. 仓位；7. 红队+合规+Judge三方比对+Pre-Publication 签收；
8. 终稿到 `workspace/reports/`。

`orchestrator` 维护 `pipeline-state.json`，任一 SUCCESS 不重跑；T1 失败 cascade 到 T2。
