---
name: portfolio-construction-skill
description: "组合构建 — 多标的目标价+波动率转仓位/集中度/止损。Use when 需要从单标估值到持仓建议时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.5.0"
---

# Portfolio Construction Skill

必须在单标估值完成后调用，不可前置污染目标价。

## 输入输出
- 输入：多标的 `{target_price, bull_bear_range, volatility, liquidity, halt_rule}` (A股含 ±10% 涨跌停，港美无)。
- 输出：`建议仓位% (如 2%–4%)` + 集中度约束 (单标 ≤10%，单行业 ≤30%) + 止损/催化剂 + `models/position_table.csv`。
- 行情与基本面解耦：波动率来自行情快照，基本面来自估值，二者分列。

## 红线
禁止无 Bull/Bear 区间给仓位；禁止杠杆建议；止损必须同时给价格与基本面证伪条件。

## Unresolved 仓位硬顶 (v1.5.0 新增，防“红旗+重仓”分裂)
- 先读 `pipeline-state.json: {unresolved_discrepancies}` + `risk_penalty_matrix.yaml`，再定仓位；输入目标价必须已是惩罚后价格，否则退回 L3。
- 硬顶：核心会计争议 ≤2%（或观察仓 0%）；重大治理 ≤3%；其余 High ≤5%；多项取最严。终稿仓位表须与红旗章节同页互链并披露惩罚档。
