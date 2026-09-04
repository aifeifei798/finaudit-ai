---
name: governance-redflags-skill
description: "公司治理红旗 — 审计师稳定性、高管更迭、股权质押、关联担保等非财务预警。Use when 需要扫描治理风险、实控人风险、审计意见时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Governance Red Flags Skill

This skill is designed to identify non-financial warning signs (red flags) in corporate governance and executive behavior that often precede financial collapse or fraud.

## Audit Focus Areas

### 1. Auditor & Accounting Firm Stability
- **Auditor Resignation**: Search for "resignation", "dismissal", "disagreement with auditor" in annual reports, regulatory filings, or news.
- **Frequent Auditor Changes**: ≥2 changes in 3 years, or any change within 6 months before annual report = High; ≥3 changes in 5 years = Critical.
- **Qualified Opinions**: Identify any "qualified opinion / 保留意见", "adverse / 否定意见", "disclaimer / 无法表示意见", or "emphasis of matter / 强调事项段". Non-standard opinion in any of last 3 years = High minimum.

### 2. Executive Turnover (CFO/CEO) & Board
- **CFO Departures**: Sudden departure within 3 months before/after annual report = High; 2+ CFO changes in 3 years = Critical.
- **Board Instability**: 独董占比 < 1/3 (A股/H股) 或 < 50% 独立董事 (美股)，或审计委员会主席变更未披露理由 = Medium+。
- **两权分离/兼任**: 董事长兼总经理 + 家族控制董事会多数席位 = 治理折价因子，需在估值中 haircut。

### 3. Share Pledge & Control Risks (分市场阈值，v1.1.0 修正一刀切)
- **Pledge Ratio** = 控股股东已质押股数 / 其持股总数。
- **A股**: > 50% 关注, > 70% 严重警告, > 80% 临界 (平仓风险)。
- **港股/美股 (margin loan)**: 披露大额 margin facility 或质押率 > 50% 即 High；涉及券商强制出售披露即 Critical。
- **Margin Call History**: Search for 补充质押/平仓/违约处置/冻结轮候冻结。
- 无质押披露不等于零质押：必须写明检索范围 (年报 Note X / 中登 / 公告)，否则记 `N/A (undisclosed)` 而非 0。

### 4. Abnormal Asset/Liability Movements
- **Non-Recurring Guarantees**: 对外担保余额 / 净资产 > 30% (A股) 或 > 20% (美/港无明确上限但需同业对比) = High；为实控人关联方担保 = 直接提级一档。
- **Emergency Asset Disposals**: 年末前 60 天内出售核心资产、售后回租、突击债务重组收益占净利润 > 10% = 窗口粉饰嫌疑。
- **Related Party Transactions**: 与实控人控制主体的大额非经营性往来 (其他应收/预付/资金拆借) 余额 > 净资产 5% 或单笔 > 营收 3% = High，需穿透定价公允性。

## Workflow
1. **Scan Filings**: Use `financial-researcher` to extract sections on "Corporate Governance", "Related Party Transactions", and "Auditor's Report". Canonical input: `workspace/targets/{TICKER}_{PERIOD}/extracted/` (legacy flat `workspace/extracted/` 只读兼容)。
2. **Cross-Reference**: Compare current auditor/CFO with previous 3–5 years' reports; timeline table mandatory.
3. **Quantify Pledges**: Extract pledged vs. held; show formula and page citation.
4. **Flag & Cite**: For every red flag found, provide the exact page/paragraph citation and assign a risk level (Low, Medium, High, Critical).

## Output Format
| Red Flag Category | Finding | Risk Level | Citation |
| :--- | :--- | :--- | :--- |
| Auditor | Auditor resigned due to "disagreement on revenue recognition" | Critical | FY2023 AR p.142 Para 3 [FN-12] |
| Executive | CFO resigned 2 weeks before FY2023 audit | High | News Release 2024-01-10 [FN-13] |
| Pledges | Controller pledge ratio at 82% (A-share >80% critical) | Critical | Note 12 p.88 [FN-14] |
| Assets | Sold core factory to related party at 40% discount | High | Note 21 p.95 [FN-15] |

所有 FN 编号必须在 `citation-engine-skill` 文献表中可回查。未检索到不写“无风险”，写 `Not found in [scope], confidence: Low`。
