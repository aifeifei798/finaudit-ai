---
description: 纯估值建模模式 — 三表清洗与 DCF 测算
agent: valuation-expert
---

针对 $ARGUMENTS 执行纯估值建模 (与 dcf.json 同义，Markdown 入口)。

流程：`financial-research-skill` + `financial-parser-skill` 清洗三表 → `valuation-modeling-skill` DCF (WACC 推导 + Base/Bull/Bear + 敏感性) → `peer-comparison-skill` median 交叉 → `excel-export-skill` 在 `workspace/targets/{TICKER}_{PERIOD}/models/` 生成活表并验证联动。

要求：Python-first，每数必 `[Python Calc #ID]`，越界抛错重估。跳过文字废话，直奔数据与模型。
