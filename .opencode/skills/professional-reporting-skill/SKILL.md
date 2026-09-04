---
name: professional-reporting-skill
description: "专业研报撰写 — 合规措辞、Fact/Analysis/Judgment三段、Challenge决议附录。Use when 需要把分析转为可审阅研报时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Professional Reporting Skill

This skill transforms raw financial analysis into research-ready materials suitable for professional review and editing.

## Audit Compliance Language (Anti-Defamation Redlines, 与 citation-engine 单一来源对齐：措辞以本 skill 为准，引用格式以 citation-engine 为准)
- **PROHIBITED**: "Fraud", "Fake", "Scam", "Cooking the books", "Embezzlement", "Lying", "Deception", 及中文“造假/诈骗/洗钱/挪用 (定罪式)” — 无监管/司法引用时禁用。
- **APPROVED**:
  - "Fraud" → "Material inconsistency in financial reporting" / "Significant accounting anomaly" / "Aggressive revenue recognition".
  - "Lying" → "Discrepancy between management narrative and audited data".
  - "Fake" → "Unsubstantiated claim" / "Lack of supporting evidence".
  - "Embezzlement" → "Unauthorized fund transfer" / "Unexplained related-party outflow".
- **Rule**: Any definitive illegality claim must quote regulator (SEC/CSRC/HKEX) or court judgment with FN; otherwise use "suggests / appears / indicates need for further investigation".

## Report Structure
1. **Executive Summary**: 结论先行 (Risk rating + 推荐 + 3 条关键证据 FN)。
2. **Detailed Analysis** per chapter `Fact / Analysis / Judgment` 三段分离：Fact 仅可验证数+FN；Analysis 允许推断但标 confidence；Judgment 给 Bull/Bear + agent 立场。
3. **Valuation & Sensitivity**: DCF + peer median 双锚 + sensitivity 表来源 `[Python Calc #ID]`。
4. **Evidence Appendix**: sources + page refs + calc steps (复用 citation-engine 文献表)。
5. **Challenge Resolution Summary (v1.1.0 强制)**: 逐条 C-ID → Resolved/Accepted/Rejected + 处理 (改数/加披露/降 confidence)。
6. **Visualizations**: 每个图配数据表路径 (`models/*_chart_data.csv`)，禁止只有图无数。

## Writing Style
- Objective & Neutral; Precise (`10.2%` not `about 10%`); Structured (bullets/tables/headers)。
- 首页必须含 `Data cutoff / Currency / Scale / Restatement basis` 四要素。

## Review Readiness
- Every judgment ≥1 evidence FN; judgment 无 FN 视为 draft，禁止标 FINAL。
## HITL Gate: Pre-Publication
MUST NOT publish until Adversarial Skeptic SIGNED_OFF (`pipeline-state.json: {skeptic.status: SIGNED_OFF}` + `workspace/reviews/*_challenge_log.csv` 全关闭)。Report-writer 附 Challenge Resolution Summary，否则 CI/复核打回。
