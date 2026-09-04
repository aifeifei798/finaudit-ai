---
name: peer-comparison-skill
description: "可比公司 benchmarking — peer筛选、IQR去极值、分位估值。Use when 需要相对估值、行业对标、premium/discount论证时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Peer Comparison Skill

This skill provides the methodology for relative valuation and benchmarking against industry competitors.

## Peer Set Selection (v1.1.0 量化收紧)
1. **Quantitative Filters**: Revenue 0.5x–2x target; EBITDA margin ±5pp (周期行业 ±10pp); Market Cap 0.3x–3x; 同一财年口径。
2. **Qualitative Filters**: business model, geography, customer base, product overlap ≥3 项吻合才纳入；剔除主业占比 < 50% 的 conglomerate (除非分部估值 SOTP)。
3. **Min N**: 初筛 ≥8 家，最终 ≥5 家；不足 5 家必须扩大到上下游/全球同业并降 confidence 至 Medium 以下。
4. **Outlier Removal**: IQR method on each multiple separately; `Q1-1.5*IQR ~ Q3+1.5*IQR` 外剔除并留痕 (`peer_screen_log.csv`)。禁止为抬/压估值手工踢 peer，不调需双人/HITL 批准。
- Peer 主库: `workspace/peer_benchmarks/{INDUSTRY}/peers.csv` (字段: ticker, name, revenue, ebitda_margin, mktcap, source, asof)；目标快照存 `workspace/targets/{TICKER}_{PERIOD}/extracted/_peers.csv`。

## Benchmarking Metrics
- **Valuation Multiples**: P/E, EV/EBITDA, P/S, P/BV (负值记 N/A 不入中位)。
- **Operational Ratios**: Revenue Growth, Gross Margin, ROE, ROIC, Debt/Equity.
- **Efficiency Ratios**: Asset Turnover, Inventory Turnover, DSO.
- 一律用 median + P25/P75 区间，禁止只报 mean；每个 multiple 注明 `N (post-IQR)`。

## Analysis Workflow
- **Relative Positioning**: Growth vs Multiple 散点 (数据表随附，不只贴图)。
- **Premium/Discount Justification**: 溢价必须点名驱动 (growth/margin/ROIC/市占)，折价必须点名风险 (leverage/governance/liquidity)，各配 FN。
- **Implied Valuation**: `Implied EV = peer_median_EV/EBITDA * target_EBITDA` 等逐 multiple 计算 + median-of-medians 综合，并与 DCF 交叉 (差异 > 25% 需解释)。
- 输出 `models/peer_comps.csv + peer_chart_data.csv`，脚本同样 Python-first。

```python
# IQR 去极值示例 (允许库: pandas, numpy, pathlib, json)
import pandas as pd
def iqr_filter(s: pd.Series):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
    return s[(s >= lo) & (s <= hi)]
```
