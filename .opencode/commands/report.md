---
description: 全流程重型研报 — 19 Agent 闭环交付 (含欺诈检测与双HITL+独立QA)
agent: orchestrator
---

针对 $ARGUMENTS 执行全流程重型研报 (与 report.json v1.4.0 同义，Markdown 入口)。

0. screen 消歧采集（GICS/申万+restatement_policy）；1. 解析+Footnote Slicer+证据柜inbox登记；2. fraud-screener排雷（定量+附注定性+治理，不跑私有流水）；3. 对账+Pre-Valuation HITL (`gate-keeper` 签收，batch-autonomous降级WARNING放行)；
4. peer+宏观+ESG，情绪旁路；5. Dispatcher选引擎估值（禁对金融强算DCF；SBC/租赁调整；跨币种硬化）+情景+活表图表；6. 仓位；7. 红队(max2轮熔断，超限转Unresolved披露)+合规+Judge三方比对+Pre-Publication 签收+webhook推送；
8. 终稿到 `workspace/reports/`。`black-account-checker`仅当用户另附私有流水时旁路调用（先PII脱敏），默认不进主链。

`orchestrator` 维护 `pipeline-state.json`（run_mode/restatement_policy/discount_currency），任一 SUCCESS 不重跑；T1 失败 cascade 到 T2。
