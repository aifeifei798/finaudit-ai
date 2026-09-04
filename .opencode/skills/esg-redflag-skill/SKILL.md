---
name: esg-redflag-skill
description: "ESG负面筛查 — 环保处罚/治理争议/社会责任事件，只筛查不打分。Use when 需要ESG风险附录时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# ESG Red Flag Skill

只做负面筛查，不做 ESG 打分建模，避免与 `governance-redflags-skill` 重复。分工：governance 管“人/权/钱”(审计师/质押/担保/RPT)，ESG 管“环境/社会争议”(处罚/事故/诉讼)。

## 筛查项
- E: 环保处罚、碳/排污、安全生产事故 (来源：监管公告/年报或有事项)。
- S: 劳工纠纷、产品召回、数据安全事件。
- G(增量): 独董异议、反腐调查 (与 governance 去重：governance 已覆盖的不再记 ESG)。

## 输出
`extracted/_esg_flags.csv` (`category,finding,risk,FN-ID`) + 报告 ESG 附录 ≤10 行。无发现写 `Searched [scope], none found, confidence: Low`，禁止写“ESG 优秀”。
