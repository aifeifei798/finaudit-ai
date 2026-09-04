---
name: financial-parser-skill
description: "财报结构化解析 — 单位货币归一、领域分块、XBRL优先、勾稽校验。Use when 需要把PDF/XBRL/Excel转为可计算结构化数据时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
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
