---
name: valuation-modeling-skill
description: "估值建模 — Python优先计算、WACC/DCF/情景敏感性、健全性边界。Use when 需要DCF/WACC/倍数/三表勾稽与Base/Bull/Bear时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Valuation and Modeling Skill

This skill provides the framework for building and auditing financial models, ensuring mathematical integrity and scenario robustness.

## MANDATORY: Python-First Calculation
- **NO** mental math for DCF, WACC, LBO, Multiples, Three-Statement balancing.
- **Workflow**: 1) Define formula in report → 2) Python (NumPy/Pandas) in sandbox → 3) Use exact output → 4) Cite `[Python Calc #ID: script.py]`。
- **Sandbox Path (canonical)**: `workspace/targets/{TICKER}_{PERIOD}/models/` (legacy `workspace/models/` 只读兼容)。

## Python Sandbox Restrictions (v1.1.0 修正不可用白名单)
- **Library Whitelist**: `numpy`, `pandas`, `scipy`, `openpyxl`, `math` + 只读标准库 `pathlib`, `json`, `csv`, `datetime`, `decimal`。`os` 仅允许 `os.path` 只读拼接，禁止 `os.environ` / `os.system` / `subprocess` / `socket`。
- **No Network**: `requests`, `akshare`, `yfinance`, sockets 禁止；数据只读 `extracted/` 或 `raw/`。
- **No Environment Access**: `os.environ` 禁止 (hook 层亦拦截 `printenv|env|os.environ`)。
- 所有脚本头必须含 `DATA_ROOT = pathlib.Path(__file__).resolve().parents[1]` 且禁止绝对路径硬编码。

## Financial Sanity Bounds (分市场，v1.1.0 放宽一刀切)
默认成熟市场主业 (需在 Assumptions 声明适用档，否则用对应档):

| 变量 | 默认档 (成熟) | 高增长/新兴市场档 | 困境/高杠杆档 | 越界动作 |
|---|---|---|---|---|
| WACC | 4%–20% | 6%–25% (声明国别风险溢价) | 8%–30% | `ValueError` + 重估假设 |
| Terminal g | 1.5%–3.5% | 2%–5% (≤ 长期名义GDP+1pp) | 0%–2% | `ValueError` |
| D/E | > 5.0 High Leverage Warning + 偿债测试 | 同左 | 同左 | 强制流动性附表 |
| Revenue Growth (成熟单年) | >100% / <-50% Growth Anomaly | 初创允许 >100% 但需 cohort 佐证 | 下滑 >30% 需减值测试 | Warning + Bull/Bear 展开 |
| Multiples | 为负记 `N/A` 不入均值 | 同左 | 同左 | 剔除并披露 |

脚本必须含 `validate_bounds()` 失败即抛错，中止写入 SUCCESS。

## WACC 推导 (v1.1.0 新增，防拍脑袋)
- `WACC = Ke*E/(D+E) + Kd*(1-T)*D/(D+E)`；`Ke = Rf + β*ERP (+size/country alpha, 单列披露)`。
- Rf 用 10Y 国债 (备注日期)，β 用 2–5Y 周频回归或 Barra/同业 median (注明源)，ERP 4%–6% 默认并做 ±1pp 敏感性。Kd 用实际加权票息或 YTM，不得直接套 Rf+200bp 了事。

## Modeling Principles
1. **Hardcode Minimization**: All inputs in "Assumptions" section.
2. **Formula Transparency**: Traceable formulas; no deep nested IF; helper rows.
3. **Balance Checks**: `Assets - Liabilities - Equity = 0` (容差 `0.5%*TA`)；非零 Warning 并阻断 SUCCESS。
4. **Actuals vs. Forecasts**: 历史/预测分 sheet + 条件格式区分；预测期 ≤5Y (CU/成长期可 10Y 但需分段 g)。
5. **终值二选一披露**: Gordon + Exit Multiple 双算，差异 > 20% 必须解释取舍。

## Workflow
- **Audit**: 从终值回 trace 到 assumption，保留 trace log。
- **Scenario**: Base/Bull/Bear 三表 (growth/WACC/margin 联动，禁止只改 g)。
- **Sensitivity**: WACC ±1pp × g ±0.5pp 双维表 + 龙卷风图数据表。

## Deliverables
- Editable CSV/XLSX + "Model Map" (`models/MODEL_MAP.md`)；每次运行写 `models/run_log.jsonl` (input hash, output hash, bounds pass/fail)。
