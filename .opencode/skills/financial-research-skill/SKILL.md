---
name: financial-research-skill
description: "金融信息检索 — 权威信源分级、证据溯源、交叉验证。Use when 需要检索年报、公告、IR、三方数据并做 Fact|Source|Confidence 时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Financial Research Skill

This skill enables the agent to perform end-to-end financial research by integrating information retrieval, evidence review, and authoritative sourcing.

## Core Methodology
1. **Authoritative Sourcing (分级, 与 citation-engine 对齐)**: Primary = SEC EDGAR / 巨潮资讯 / 港交所披露易 / 公司 IR 公告原文 / XBRL；Secondary = 公司路演 PPT、券商研报、Wind/iFind 统计；Tertiary = 新闻/博客 (仅作线索，不可单独定量)。
2. **Evidence Tracing**: Every claim must be linked to a specific page/section. Use `source_file:page_number` or `URL#section`, footnote ID `[FN-xx]` mandatory for numbers.
3. **Cross-Verification**: Compare data across at least two independent authoritative sources to resolve discrepancies. 冲突走 `multi-doc-reasoning-skill` 优先级裁决。
4. **Information Synthesis**: raw data -> evidence -> analysis -> conclusion，禁止跳步。

## Authoritative Domain Allowlist (v1.1.0 新增)
- US: `sec.gov`, `*.company IR domain` (需在报告附录声明实际域名), `nasdaq.com` (仅行情辅助)
- CN: `cninfo.com.cn`, `sse.com.cn`, `szse.com.cn`, `*.com.cn IR` (附录声明)
- HK: `hkexnews.hk`, `*.com.hk IR`
- 非白名单域默认 Tertiary，需 `financial-analyst` 特批方可升级。Paywall/需登录源必须标注 `Access: restricted, confidence capped at Medium`。

## Search Strategy
- Keywords: `"Form 10-K"`, `"Annual Report YYYY"`, `"年报 / 审计报告"`, `"Earnings Presentation"`, `"H shares prospectus"` + ticker/CIK/证券代码。
- EDGAR: 先用 CIK 定位 (company_tickers.json)，再按 filingDate 倒序取最新 10-K/10-Q/8-K；A股先取“审计报告全文 + 财务报表附注”，再取问询函回函。
- Use `webfetch` to retrieve PDF/HTML filings and `grep` to locate key metrics. 单次抓取失败必须重试 1 次 + 换源，仍失败记 `Gap` 而非编造。
- **Cutoff**: 报告首页必须声明 `Data cutoff: YYYY-MM-DD`；cutoff 后事项仅入“期后事项”，不改历史数。

## Output Requirements
- All findings as `Fact | Source | Confidence(High/Med/Low) | FN-ID` table.
- Highlight gaps: `Gap: [missing item] | searched [sources] | impact [blocks X]`。
- 原始文件一律存 `workspace/targets/{TICKER}_{PERIOD}/raw/` (legacy `workspace/raw/` 只读兼容)，文件名 `YYYYMMDD_source_doctype.pdf`。
