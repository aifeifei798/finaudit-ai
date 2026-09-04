---
name: citation-engine-skill
description: "引用脚注引擎 — FN编号、计算溯源、分级文献表、发布前检查。Use when 需要给数字/判断加可验证引用与免责时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.8.0"
---

# Citation & Footnote Engine Skill

This skill enforces strict traceability and compliance in financial reporting, ensuring every claim is anchored to a verifiable source. (措辞红线以 `professional-reporting-skill` 为准，本 skill 只定引用格式。)

## Audit Compliance Language (Anti-Defamation)
- All citations neutral: highlight discrepancy, not prove crime. 例: 不写 "CEO lied [p.12]"，写 "CEO statement p.12 contradicts audited CF p.45 [FN-07][FN-08]"。

## Citation Standards (v1.1.0 机器可验)
1. **Footnote IDs**: 全文 `[FN-01]...[FN-NN]` 顺序编号，同一来源复用同一 ID；行内示例: "2023 EBITDA $450M [FN-12]"。报表尾部文献表必填 (见 §3)。
2. **Source pointer**: `[FN-12] = Annual Report 2023, p.42 Table 2.1, file: raw/20240315_AR.pdf, scale: millions USD`；网页加 `URL + accessed YYYY-MM-DD + archive/hash`。
3. **Calculation Traceability**: 派生数必须 `... [FN-20; Calc #45: models/dcf_v1.py:L88]`，Calc ID = `run_log.jsonl` 中的 run_id，可重跑。
4. **Source Hierarchy**: Primary (filings/audited/IR) > Secondary (deck/sell-side/industry) > Tertiary (news/blogs)。Tertiary 不可单独支撑定量结论。
5. **Exemptions (v1.1.0 新增，防教条)**: 纯算术中间步骤、目录/页眉、敏感性轴标签可免 FN，但最终输出数仍需 FN+Calc。

## Decision Lineage DAG 决策血统图 (v1.8.0 新增，30秒溯源)
- **文件**: `workspace/targets/{TICKER}_{PERIOD}/models/lineage_manifest.json`。每个进终稿/活表的关键数值（Target Price、WACC、FCF、CapEx、g）一条记录：`{metric, value, derived_from: [FN-ID / Calc#run_id / guidance_row / challenge_C-ID / haircut_tier / credit_flag], agent, at}`。
- **示例链**: `Target Price ← WACC (Haircut from Skeptic C-02) ← Footnote 14 cross-ref ← Enquiry Reply p.42`。
- **写者义务**: valuation-expert / scenario / portfolio 每次写数即追加血统记录；report-writer 渲染“Lineage 附录”；judge-qa 抽查 ≥3 条链端到端可达，否则 fail。`run_log.jsonl` 只管成本，血统管因果。
- **Critical-Path Pruning 剪枝 (v1.9.0，防 manifest 爆炸)**: 禁止单元格级全量平铺；仅 Top 20 价值敏感核心节点（Target Price、Terminal FCF、Post-Haircut WACC、Net Debt、Normalized Margin 等）记全链路因果边，中间流水数据用惰性哈希指针（`lazy: sha256(input_refs)`）链接；manifest 硬上限 500KB，超限即 `lineage: FAILED` 重写。

## Bibliography Schema (`workspace/targets/{TICKER}_{PERIOD}/extracted/_bibliography.csv`)
`fn_id,doc_title,doc_date,file_or_url,page_table,scale_currency,level_P/S/T,accessed,hash_or_pages,notes`

## Compliance & Disclaimers
- Every report ends with: "This report is for informational purposes only and does not constitute investment advice." + "Based on publicly available data and assumptions subject to change." + 中文版同义。
- **Conflict Disclosure**: Explicitly state known conflicts; unknown 写 `No known conflicts as of [cutoff]`。

## Final Review Checklist (发布门禁)
- [ ] Does every final number have FN (+Calc if derived)?
- [ ] Are all Python calcs linked to run_id?
- [ ] Disclaimer + 中文版 present?
- [ ] Page numbers for all PDF refs?
- [ ] Defamatory language replaced per professional-reporting-skill?
- [ ] `_bibliography.csv` 行数 == 最大 FN 编号 (无跳号)？
- [ ] skeptic SIGNED_OFF 已校验？
