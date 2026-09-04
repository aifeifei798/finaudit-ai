---
name: multi-doc-reasoning-skill
description: "多文档对账 — 重述优先、口径映射、冲突裁决、HITL预估值卡点。Use when 需要跨年报/季报/路演对齐Revenue/EBITDA/假设时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.4.0"
---

# Multi-Document Financial Reasoning Skill

This skill focuses on coordinating and reconciling data across multiple financial documents with different reporting cycles, definitions, and assumptions.

## Latest Audited Restatement Rule (Anti-Restatement Trap)
- **策略参数** `restatement_policy` (v1.4.0, 防回测未来偏差): `as-restated`（实时前瞻默认：最新审计重述优先）vs `as-reported`（历史回测/量化默认：只用当时披露口径，忽略后期重述，`vintage_asof` 定格取数日）。
- **Rule (as-restated)**: If a YYYY Annual Report provides "Restated" figures for YYYY-1, these MUST supersede the original YYYY-1 report.
- **Action**: Explicitly flag discrepancies in `extracted/_reconciliation_log.csv` with columns: `metric|old_value|old_source|restated_value|restated_source|delta_pct|vintage_asof|policy|chosen|reason|FN-ID`; 所用 policy 快照写入 `_assumptions.csv` 一行。
- **Verification**: Before trend analysis, compare "Comparative" columns in latest report vs "Standalone" prior reports; delta > 1% 必须逐项解释 (重分类/并表/差错更正)。

## Reconciliation Workflow
1. **Timeline Alignment**: Map reporting dates (10-K vs 10-Q vs Earnings Call vs 年报/半年报/问询函)。
2. **Definition Mapping**: Build `metric_map.csv`: GAAP Revenue / Non-GAAP Adj. Revenue / Segment Revenue / EBITDA / Adjusted EPS per doc + adjustment bridge。口径不明记 `Undefined`，禁止混用。
3. **Conflict Resolution priority**: Latest Audited Restatement > Regulatory Filing (10-K/年报审计版) > 10-Q/季报 > Earnings Release/业绩快报 > Investor Presentation > Third-party Research。每次裁决写 `chosen + reason + FN-ID`。
4. **Assumption Tracking**: Extract growth/discount/tax/FX assumptions per doc into `extracted/_assumptions.csv`。

## Reasoning Patterns
- **Trend Analysis**: YoY + CAGR + 同业分位三视角；单年 > ±30% 必须找附注解释。
- **Consistency Check**: 报告“摘要/管理层讨论”数字必须与“财务报表”逐项核对，不一致即 flag。
- **Gap Analysis**: 研报有而 filing 无的内容列为 `Unsubstantiated`，不得进入估值 base case。

## HITL Gate: Pre-Valuation (v1.1.0 落地机制，解决空喊问题)
Before passing data to Valuation Expert, the Financial Analyst MUST block and ask if ANY true:
- Material conflicts unresolved by priority rules;
- Abnormal adjustments > 10% of Net Income;
- Key valuation assumptions from non-audited/speculative sources.
**执行**: institutional 模式调用向用户确认工具 (opencode `question` / HITL)，附 `conflict/adjustment + proposed resolution + impact on valuation`，用户明确批准前禁止写 `analyst: SUCCESS`。批准记录追加到 `workspace/targets/{TICKER}_{PERIOD}/pipeline-state.json: {analyst_gate: {status: APPROVED, by, at, notes}}` + `workspace/reviews/{TICKER}_{PERIOD}_prevaluation.md`。
**batch-autonomous 降级 (v1.4.0)**: `run_mode=batch-autonomous` 时不阻塞等待，改为评分制——冲突逐项打 `severity 分 + auto_resolution`，记 `analyst_gate: {status: AUTO_PASSED_WITH_WARNINGS, warnings: [...]}` 并继续流水线；终稿风险章节必须列出全部 warnings。批量跑批/历史回测用此模式，在线专家签批用 institutional。
