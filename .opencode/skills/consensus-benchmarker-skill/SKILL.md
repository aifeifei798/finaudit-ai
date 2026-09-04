---
name: consensus-benchmarker-skill
description: "一致预期差 — 系统估值 vs 卖方Consensus求Δ，回答Alpha来源。Use when 需要把目标价/EPS/增速与市场预期对比、论证预期差时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.8.0"
---

# Consensus Divergence Engine (v1.8.0，买方视角)

投资看的不是“好不好”，而是“比市场预期好还是差”。脱离 Consensus 的独立估值是闭门造车。

## 输入契约 `extracted/_consensus.csv`
列：`metric|consensus_mean|consensus_n|asof|source|level`。来源优先级：机构终端（Bloomberg/FactSet/Wind/CapIQ，经 IAL 驱动）> 手工录入卖方研报均值（≥3 家）> 缺失记 `Gap: no consensus coverage`。
**诚实铁律**：无覆盖禁止编造 Consensus；无 Consensus 时先用当前股价反推市场内含隐含增长率作基准（打 `CONSENSUS_DATA: MARKET_IMPLIED` 标签），仍无法反推才写 `Consensus Delta: N/A (uncovered)` 并将 conviction 降一档。

## 求差计算（Python-first）
- `Δ_EPS = (our_EPS − consensus_EPS) / |consensus_EPS|`；`Δ_g`、`Δ_Target` 同口径；每个 Δ 注明 `asof`（预期会漂移，过期 > 30 天标 stale）。
- 终稿必须回答：**“我们比市场更乐观/悲观的本质 Alpha 在哪里？”**（如：海外折旧年限被低估→未来两年真实 EPS 比 Consensus 低 15%），配 FN+Calc。
- 高亢奋预警：我们的内在价值低于 Consensus 目标价 > 20%（市场已 Price-in 乐观预期）→ 即使绝对估值“便宜”亦不得推荐重仓，最高观察仓。

## 输出
`models/consensus_delta.csv` + 终稿 `Consensus Divergence` 独立章节；`pipeline-state.json: {consensus: SUCCESS|GAP}`。
