---
name: valuation-modeling-skill
description: "估值建模 — Python优先计算、WACC/DCF/情景敏感性、健全性边界。Use when 需要DCF/WACC/倍数/三表勾稽与Base/Bull/Bear时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.4.0"
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
- 跨币种（H股/ADR）必须先按 `market-adapter-skill` 跨币种铁律定 `discount_currency + CRP` 再算 Ke/WACC，终值一律 T=0 即期单点转换（`FX: <pair> <rate> @T=0`），否则 `ValueError`。

## Valuation Dispatcher (v1.4.0 新增，防“一刀切”DCF)
- **输入**: ticker-resolver 输出 `{gics11, sw31/hs11, profitable_flag, business_model}` + `workspace/params/valuation_routing.yaml@v1.4.0`。
- **路由**: Financials→`financials_bypass` (PB-ROE + DDM，禁 FCFF/WACC)；REITs→`reit_bypass` (FFO/AFFO + NAV/cap rate)；周期→`mid_cycle_normalized` (5–10Y均值盈利 + PB Band，禁单年峰值外推)；未盈利Biotech/SaaS→`pipeline_or_sales` (rNPV / EV/Sales + Rule of 40，禁负FCF设正永续g)；其余→`dcf_fcff`。
- **硬规则**: 命中 bypass 行业却被要求跑标准 DCF 时，脚本必须 `raise ValueError("engine mismatch: <industry> forbids fcff_dcf, reroute per valuation_routing.yaml")` 并中止 SUCCESS；路由选择写入 `_assumptions.csv` 一行 `valuation_engine: <engine> per routing@v1.4.0`。

## Multiples-Engine (v1.4.0 新增，与 DCF 平级)
- **模型集**: PE/PB Band (5Y median ±1σ)、EV/EBITDA、SOTP (conglomerate 分部加总)、DDM (金融/高分红)。
- **口径**: 一律 median + P25/P75，负值记 N/A 不入均值；每个 multiple 注明 `N (post-IQR)`；`median-of-medians` 综合 + 与主引擎交叉 (差异 > 25% 必须解释取舍)。
- DCF 仍要求 Gordon + Exit Multiple 双终值（差异 > 20% 解释），但不再是唯一引擎。

## SBC 与租赁调整 (v1.4.0 新增，防隐形现金流失真)
- **SBC**: 美股科技必查。双列披露 `FCF_reported` vs `FCF_adj = FCF_reported - SBC`（另计 SBC 相关现金税影响）；若 `SBC/FCF > 20%` 标 High；摊薄股数必须给 trajectory，EPS/DDM 用稀释后股数。
- **租赁 (IFRS 16 / ASC 842)**: 双列 `EBITDA_pre/post_lease`；EV 必须把租赁负债计入 Debt；FCF 附桥接表说明经营/筹资重分类影响。未做桥接不得进 base case。

## Confidence Haircut 联动 (v1.5.0 新增，Unresolved 强制惩罚估值)
- **输入**: `pipeline-state.json: {unresolved_discrepancies}` + `workspace/params/risk_penalty_matrix.yaml@v1.5.0`。
- **规则**: 存在 Unresolved 即先算惩罚参数再定价——核心会计争议档 `g -50bps、WACC +100bps`；重大治理档 `g -30bps、WACC +50bps`；其余 High 档 `g -20bps、WACC +50bps`；多项并存取最严一档不叠加。
- **硬约束**: 目标价必须基于惩罚后参数重算并双列披露（惩罚前/后）；未读 unresolved 列表直接定价即判错，judge-qa 交叉不一致阻断 FINAL。

## SOTP 分部加总 (v1.5.0 新增，集团型企业禁单引擎)
- **探针**: ticker-resolver 给 `is_conglomerate=true`（多主业、次主业≥20%或附注可拆≥2分部）即拆 2–3 个分部，每分部独立挂引擎（寿险EV/NBV、银行PB-ROE、科技PS、联营投资NAV、开发NAV、持有物业FFO/CapRate），`models/` 出 SOTP 加总活表 + 控股折价（conglomerate discount）披露。
- 单引擎硬套平安/腾讯/阿里类集团即判错，judge-qa 阻断。

## Distressed Fallback 困境兜底 (v1.6.0 新增，防 BV<0 / NaN 爆炸)
- **触发**: 净资产 < 0，或近三年 FCF 连续 < 0，或债务市值不可得（违约深跌）——满足任一即 distressed，严禁标准 DCF / PB-ROE，违者 `ValueError`。
- **切换**: 强制清算价值法（Liquidation / Net-Net）或 EV/Sales 中枢；E 权重改用市值（无市值用账面 floor 0 + 披露），禁用负账面 E 进 WACC 权重。
- **Clamp**: Sensitivity 矩阵先验 `(WACC − g) ≥ 1.5%`，违例格记 `N/A (clamped)` 不渲染；visualization 空值不断图表管线。

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
