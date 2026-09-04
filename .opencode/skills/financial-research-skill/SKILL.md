---
name: financial-research-skill
description: "金融信息检索 — 权威信源分级、证据溯源、交叉验证。Use when 需要检索年报、公告、IR、三方数据并做 Fact|Source|Confidence 时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.6.0"
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

## Regulatory Enquiry Collector (v1.6.0 新增，定期报告之外的致命证据)
- **范围**: CN 近24个月交易所《年报问询函/监管工作函 + 回复公告》（穿透前五大客户、超期应收对手方、受限资产细节）；US 近24个月 SEC Comment Letters（CORRESP/UPLOAD）；HK 监管查询函；临时公告（质押被动平仓、高管/审计委员会主席/内审总监辞职）。
- **优先级**: 问询函+回函与 footnotes 同级，直送 `footnotes_focus/` 聚焦窗口并在 `_footnote_index.csv` 标 `source_class: regulatory_enquiry`；fraud-screener 必须先读问询函窗口再下排雷结论，无问询函覆盖不得声称“监管无质疑”，写 `Not covered, confidence: Low`。
- **命名**: `YYYYMMDD_source_enquiry_<topic>.pdf` 存 `raw/`；缺失记 Gap（定期报告漂亮但问询函缺席本身即风险信号）。

## Global Rate-Limiting Proxy 与共享缓存 (v1.7.0 新增，防批量跑批被交易所拉黑)
- **Token-Bucket 流控**（L1 底层强制）: EDGAR ≤ 8 req/sec + 声明合规 User-Agent（含联系邮箱，SEC 强制要求）；CNINFO/HKEX 动态随机延迟 Jitter + 失败指数退避，403/验证码即停并切代理池，禁止硬扛重试刷 IP。
- **中央持久化缓存** `workspace/shared_filing_cache/`（键：`source/doctype/ticker/period/vintage_hash`）：同业 peer 公共宏观数据、已采定期报告**强制命中缓存**，严禁重复请求外网；缓存命中记 `cache: HIT` 入 `_bibliography.csv`，缺失才走外网并回填。
- batch-autonomous 模式下 collector 必须先查缓存再排队限流，违例导致 IP 封禁记 `collect: FAILED` 并阻断同批后续外网任务（保 IP）。

## Transcript Collector 电话会采集 (v1.8.0 新增，看前视镜)
- **范围**: 最新季度 Earnings Call 全文（Prepared Remarks + Q&A Session）+ NDR 纪要；命名 `YYYYMMDD_source_transcript.pdf` 存 `raw/`，`level=S`（Secondary，仅次于审计财报）。
- **用途**: 捕捉三表外前瞻变量——订单积压 Backlog、CapEx 削减计划、试产良率、Churn、渠道库存/毛利率预警（电话会一句话常比三表先行 1–4 个月）。
- 缺失记 Gap（`transcript: NOT_FOUND`），不得用旧季度电话会冒充当季。

## Guidance Extractor 指引抽取 (v1.8.0 新增)
- 强制提取管理层下季度/全年 Revenue/CapEx/EPS 指引区间 → `extracted/_guidance.csv`（列：`metric|low|high|period|source|FN-ID`)。
- **Guidance-Divergence 铁律**: `valuation-expert` 模型假设与官方指引偏离 > 15% 即触发警告，终稿必须单列解释分歧原因；无解释不得进 base case。

## Ingestion Abstraction Layer 摄取抽象层 (v1.8.0 新增，配置见 `params/ingestion.yaml`)
- **双驱动**: `direct_scraper`（默认：公开端 + 限流池 + 共享缓存）/ `institutional_terminal`（Bloomberg B-PIPE / FactSet / CapIQ / Wind，内网合规，凭证只走 env vault）。
- **契约不变**: 无论哪种驱动，输出 L1 的字段契约完全一致（ticker/period/doctype/vintage_asof/payload/source/hash）；反爬升级或网关阻断即切终端驱动，禁止硬扛刷 IP。

## Search Strategy
- Keywords: `"Form 10-K"`, `"Annual Report YYYY"`, `"年报 / 审计报告"`, `"Earnings Presentation"`, `"H shares prospectus"` + ticker/CIK/证券代码。
- EDGAR: 先用 CIK 定位 (company_tickers.json)，再按 filingDate 倒序取最新 10-K/10-Q/8-K；A股先取“审计报告全文 + 财务报表附注”，再取问询函回函。
- Use `webfetch` to retrieve PDF/HTML filings and `grep` to locate key metrics. 单次抓取失败必须重试 1 次 + 换源，仍失败记 `Gap` 而非编造。
- **Cutoff**: 报告首页必须声明 `Data cutoff: YYYY-MM-DD`；cutoff 后事项仅入“期后事项”，不改历史数。

## Output Requirements
- All findings as `Fact | Source | Confidence(High/Med/Low) | FN-ID` table.
- Highlight gaps: `Gap: [missing item] | searched [sources] | impact [blocks X]`。
- 原始文件一律存 `workspace/targets/{TICKER}_{PERIOD}/raw/` (legacy `workspace/raw/` 只读兼容)，文件名 `YYYYMMDD_source_doctype.pdf`。
