---
name: excel-export-skill
description: "活表导出 — openpyxl公式注入、Assumptions联动、勾稽校验。Use when 需要生成可编辑.xlsx估值模型时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.6.0"
---

# Excel Export Skill

This skill enables the generation of "Living Excel" models where the output is not just a static table, but a functional spreadsheet with active formulas.

## Technical Implementation
- **Library**: Use `openpyxl` for .xlsx with formulas (`data_only=False` for audit)。
- **Formula Injection**: Write `=B2*C2` not `105`; 输入/计算/汇总三层分离：
  - **Assumptions Sheet**: Growth, WACC, Tax, NWC assumptions (黄色底纹 + 数据验证)。
  - **Calculation Sheet**: Linked to Assumptions (禁止硬编码数字，审计时 `Ctrl+`` 全公式可读)。
  - **Summary Sheet**: EV/Equity Value/Share Price linked to Calculation + ` sensitivity table` 位置预留。
- **Canonical Path (v1.1.0 统一)**: `workspace/targets/{TICKER}_{PERIOD}/models/{Company}_Valuation_Model.xlsx` (legacy `workspace/models/` 禁止新写)。

## Delivery Standard
1. **Dynamic Inputs**: Change one Assumptions cell → Summary auto-updates (交付前改 2 个假设做联动测试并截图/log)。
2. **Balance Check**: `=IF(ABS(Assets-Liab-Equity)<=MAX(0.005*TA,scale),"TRUE","FALSE")` 独立 Check 列/行；FALSE 禁止标 SUCCESS。
3. **Audit Trail**: Simple traceable formulas; no array black-box; 每个跨表引用加批注 `source: Assumptions!B4`。
4. **Post-write verify (v1.1.0 新增)**: 写完后用 Python 重开 (`data_only=False`) 抽查 ≥5 个公式含跨表引用 + 用 `libreoffice --headless --convert-to csv` 或 openpyxl 计算值抽查，失败重写。记录 `models/excel_verify.log`。

## Circular-Reference Break (v1.6.0 新增，利息闭环脱钩)
- **铁律**: 利息一律按**期初债务余额**计提（`Interest_t = rate × Debt_{t-1}`），禁止引用当期期末现金/新增借款反推的债务余额；现金→借款→利息→利润→现金闭环在数学上断开，活表改任一假设仍全表联动，且 Excel 永不弹循环引用警告。
- **校验**: 写完后用 openpyxl 扫描公式依赖图，出现自环即重写；联动测试（改 g / WACC 各 1 次）Summary 必须跟动并记 `excel_verify.log`。

## Export Workflow
- **Step 1**: Define structure in Python (`models/build_excel.py`)。
- **Step 2**: Write formulas via `openpyxl`。
- **Step 3**: Save to canonical path above。
- **Step 4**: File path + verify log + Model Map reference in final report; update `pipeline-state.json: {excel: SUCCESS}`。
