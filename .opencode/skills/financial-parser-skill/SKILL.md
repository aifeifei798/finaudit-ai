---
name: financial-parser-skill
description: "财报结构化解析 — 单位货币归一、领域分块、XBRL优先、勾稽校验。Use when 需要把PDF/XBRL/Excel转为可计算结构化数据时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.7.0"
---

# Financial Parser Skill

This skill ensures that raw financial documents (PDFs, XBRL, Excel) are converted into high-fidelity structured data before analysis.

## Canonical Paths (v1.1.0 统一，解决三处打架)
- **Canonical**: `workspace/targets/{TICKER}_{PERIOD}/raw/` (输入) → `workspace/targets/{TICKER}_{PERIOD}/extracted/<domain>/` (输出) → `workspace/targets/{TICKER}_{PERIOD}/models/` (脚本)。
- **Legacy compat**: 旧扁平 `workspace/raw|extracted|models/` 仅只读 fallback，新任务禁止写入；如命中 legacy 必须在 log 中提示迁移。
- Peer 公共库: `workspace/peer_benchmarks/{INDUSTRY}/` (不存在则创建目录 + README)。

## Unit & Currency Normalization (Anti-Unit Chaos)
- **Standardization**: Convert all values to absolute numbers (e.g., "1.2 billion" → 1,200,000,000; "12,345 千元" → 12,345,000)。
- **Currency ISO**: Tag every value with ISO 4217 (USD, CNY, HKD, JPY...)。
- **FX Rate Logic**:
  - Balance Sheet → Spot Rate at reporting date (注明来源: Fed H.10 / 外管局中间价 / 公司附注汇率)。
  - Income/Cash Flow → Average Rate for the period (同上注明)。
  - 禁止混用即期/均值；汇率表单独存 `extracted/fx_rates.csv`。
- **Verification**: Cross-check the "Units" header of every table (e.g., "In thousands of USD") and apply the multiplier strictly; multiplier 必须作为独立字段 `scale: 1000` 落盘。

## Domain-Chunked Parsing (Anti-Context Overflow)
Split into `workspace/targets/{TICKER}_{PERIOD}/extracted/`:
- `financial_statements/`: BS, IS, CF (CSV + JSON, 保留行列对齐)。
- `notes_debt/`: Debt, loans, guarantees footnotes.
- `notes_revenue/`: Revenue recognition and segment data.
- `related_parties/`: RPT and ownership.
- `management_discussion/`: MD&A outlook (事实与观点分列)。
- `audit_opinion/`: Auditor's report and KAMs.
- 单 chunk > 模型上下文 1/2 时继续按“附注号”切分，禁止整表截断。

## Footnote Slicer 独立通道 (v1.4.0 新增，附注不再降级为普通文本)
- **输出**: `extracted/footnotes_focus/` + 索引 `extracted/_footnote_index.csv` (列: `note_id|title|pages|risk_score|risk_reason|verbatim_path|FN-ID`)。
- **必筛重点章节** (命中即重点推理，不许只抽数字): Commitments & Contingencies（担保/表外/VIE）、Related Parties（关联定价/资金拆借）、Segment Reporting、Restricted Cash（受限资金）、Debt Covenants、Litigation、AR保理附追索权、股份质押。
- **流程**: T1 粗筛全附注打 `risk_score (0-3)` → score≥2 的章节保留**原文聚焦窗口** (verbatim excerpt，单窗 ≤4k tokens，保留 `source_file:page:note_id` 锚点) 供 T2 fraud-screener / L4 做定性推理；score≤1 只存摘要 + 页码指针。
- **Selective Long-Context Bypass**: T2/L4 只读 `footnotes_focus/` 原文窗口，仍禁读 raw PDF 全文——既控 token，又不漏附注猫腻。未建聚焦窗口不得声称“已扫附注”，写 `Not screened, confidence: Low`。

## Cross-Reference Resolver (v1.5.0 新增，防跨注孤岛)
- **触发正则** (中英): `详见附注.{0,8}?[十一二三四五六七八九十\d\(\)（）五、,\. \-Notes]+` / `(see|refer to|Note)\s*\d+[\.\(\d\)]*` / `附注十一（五）类` 精确锚点。
- **Expansion Fetching**: 任一聚焦窗口命中引用即自动连带抽取目标附注原文并入同一窗口包（`expansion_from: [note_ids]` 记入 `_footnote_index.csv`）；最多展开 2 跳，防无限递归；目标缺失记 `Dangling ref → Gap`。
- 担保明细藏关联方大表脚注、或有事项一句话挂受限资产等“捉迷藏”写法，必须靠本机制还原主干上下文，孤岛片段禁作定性结论唯一依据。

## Enquiry De-hydrator 问询函双阶脱水器 (v1.7.0 新增，防 Token 爆仓与表格串行)
- **语义降噪**：入库前剔除律所/会计所套话段落（正则特征句库：`经核查认为.*符合.*准则.*规定` / `具有合理性` / `we concur.*in all material respects` / 准则条文背诵段），目标保留率 15%~20%；剔除清单记 `dehydrate_log.csv`（段落数/字数/保留率），可审计回放。
- **Cross-Page Table Stitcher**：跨页大表（前五大客户/账龄穿透）按表头继承 + 列对齐重构：续页无表头即继承上一页表头；合并单元格展开；逐行校验列数一致，错位行标 `STITCH_WARN` 人工复核；缝合后抽查 5 行对原 PDF 页码。
- 脱水后窗口才进 `footnotes_focus/`（`source_class: regulatory_enquiry`），原始全文仍存 `raw/` 备查。

## Extraction Standards
1. **Table Integrity**: 优先 XBRL tags (SEC) / 巨潮结构化财报；PDF 表格用 camelot/tabula 类工具并人工抽查 5 行；禁止用纯文本流推断表格。
2. **Footnote Mapping**: Every number must be checked for footnotes; footnotes extracted and linked (`value_id -> note_id`)。
3. **XBRL Integration**: For SEC filings, prioritize XBRL tags over OCR/text parsing; 记录 `tag + contextRef + decimals`。
4. **Formula Preservation**: Extract underlying formula from .xlsx (openpyxl `data_only=False`) rather than just value; 公式与值双列存储。

## Validation Workflow
- **Cross-Check (容差 v1.1.0)**: 明细求和 vs 报表合计数差异 > `max(0.5% * total, scale)` 记 `Parsing Error`；以内记 `Rounding OK`。汇率/单位错误一票否决。
- **Unit Verification**: Explicitly identify currency and scale for every table.
- **Page Anchoring**: Every data point tagged `source_file:page:table_id` + footnote `FN-ID`。
- 完成后更新 `pipeline-state.json: {parser: SUCCESS|FAILED, parser_notes: ...}`。
