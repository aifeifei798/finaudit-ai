---
name: quantitative-fraud-metrics
description: "定量欺诈检测 — Beneish M-Score、Altman Z-Score、Sloan应计异常等数学化舞弊 tripwire。Use when 需要计算盈余操纵概率、现金债悖论、应计偏离时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Quantitative Fraud Metrics Skill

This skill provides a rigorous mathematical framework for detecting financial manipulation, moving beyond qualitative "red flags" to quantitative "tripwires".

## 1. Beneish M-Score Model

> 修正说明 (v1.1.0): 原 `PLTA` 笔误已修正为标准 `LVGI` (Leverage Index)；`DEPI` 分子分母已按 Beneish 1999 原文校准。

A score > -1.78 suggests a high likelihood of manipulation; -2.22 ~ -1.78 is the grey zone requiring additional evidence; < -2.22 is unlikely.

**Formula Components (t = 本期, t-1 = 上期):**

- **DSRI (Days Sales in Receivables Index)**: (Receivables_t / Sales_t) / (Receivables_{t-1} / Sales_{t-1})
- **GMI (Gross Margin Index)**: [(Sales_{t-1} - COGS_{t-1}) / Sales_{t-1}] / [(Sales_t - COGS_t) / Sales_t]
- **AQI (Asset Quality Index)**: [1 - (CurrentAssets_t + NetPPE_t) / TotalAssets_t] / [1 - (CurrentAssets_{t-1} + NetPPE_{t-1}) / TotalAssets_{t-1}]
- **SGI (Sales Growth Index)**: Sales_t / Sales_{t-1}
- **LVGI (Leverage Index, 原误写 PLTA)**: (TotalLiab_t / TotalAssets_t) / (TotalLiab_{t-1} / TotalAssets_{t-1})
- **DEPI (Depreciation Index)**: [Depreciation_{t-1} / (Depreciation_{t-1} + NetPPE_{t-1})] / [Depreciation_t / (Depreciation_t + NetPPE_t)]
- **SGAI (SG&A Expenses Index)**: (SGA_t / Sales_t) / (SGA_{t-1} / Sales_{t-1})
- **TATA (Total Accruals to Total Assets)**: (IncomeBeforeExtra_t - CFO_t) / TotalAssets_t

**M-Score Formula:**

```text
M = -4.87 + 0.920*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI + 0.115*LVGI - 0.172*SGAI + 4.679*TATA - 0.327*DEPI
```

> 注：市面流传有系数变体 (-0.048*GMI / 0.115*LVGI / -0.327*SGAI 等)。本 skill 采用 Beneish 1999 原文 8 变量系数。必须在报告中声明所用系数版本，并在 `models/` 下保留 Python 脚本以便复现。禁止心算。

**判定：**

| M-Score | 含义 | 动作 |
|---|---|---|
| < -2.22 | 操纵概率低 | 通过，记录数值 |
| -2.22 ~ -1.78 | 灰区 | 需至少 1 个独立佐证 (Z-Score / 现金债悖论 / 治理红旗) |
| > -1.78 | 高操纵概率 | 触发 🔴，要求 Cash Verification 证据块 |

**缺失值处理：** 任一输入缺失 → 该期 M-Score 记为 `N/A (insufficient data)`，禁止用 0 或均值填充后仍给结论；必须在 Data Reconciliation log 中列明缺失字段及来源页码。

## 2. Altman Z-Score (破产风险交叉验证)

- 上市制造企业: `Z = 1.2*WC/TA + 1.4*RE/TA + 3.3*EBIT/TA + 0.6*MVE/TL + 1.0*Sales/TA`
- 判定: Z > 2.6 安全; 1.1–2.6 灰区; < 1.1 (新兴市场 < 1.8) 困境。
- 非制造/新兴市场使用 Altman Z'' 变体并声明版本。

## 3. Sloan Accrual Anomaly + F-Score 简筛

- **Sloan**: Accruals = (NetIncome - CFO) / TotalAssets；若连续 2 年 > 0.10 或同业分位 > P75，标记应计激进。
- **Dechow F-Score**: 有条件时计算 Prob(Manipulation)；F > 1.0 高于平均风险，F > 2.0 显著风险。允许 `N/A` 但需说明原因。

## 4. "High Cash, High Debt" Paradox (The "Kangmei" Trigger)

Detects companies that report massive cash balances while simultaneously borrowing heavily at high rates.

**Trigger Conditions (需同时命中 ≥2 条才触发 🔴):**

- **Cash-to-ShortDebt**: (Cash & Equivalents) / (Short-term Debt + CPLTD) > 1.5
- **Interest Coverage Gap**: (Interest Expense / Average Cash) > 0.05
- **Cash Flow Divergence**: (Net Income - Operating Cash Flow) / Total Assets > 0.10 for 3 consecutive years

## 5. Execution Protocol

- **Step 1**: 从 `workspace/targets/{TICKER}_{PERIOD}/extracted/financial_statements/` 提取 8 变量 + Z-Score 输入 (BS/IS/CF)。
- **Step 2**: 在 `workspace/targets/{TICKER}_{PERIOD}/models/` 下用 Python (numpy/pandas) 计算 M-Score / Z-Score / Sloan，脚本必须含 sanity bounds 校验。
- **Step 3**: 检查 "High Cash, High Debt" paradox。
- **Step 4**: 任一 tripwire 命中 → `fraud-screener` 提级至 🔴 并要求 "Cash Verification" 证据块 (银行函证/受限资金附注/利息收入匹配)。
- **Step 4b (定性附注联动, v1.4.0)**: 同步读 `extracted/_footnote_index.csv` + `footnotes_focus/` 原文窗口（担保/表外VIE/受限资金/保理追索/诉讼/关联拆借）；定量灰区以上必须配 ≥1 附注原文佐证或明确 `Gap: footnotes_focus missing`，禁止纯数字下🔴定论。
- **Step 5**: 所有数值引用格式 `[Python Calc #ID: script_name.py]`，并在 `pipeline-state.json` 记录 `fraud_metrics: SUCCESS|N/A`。

## 6. Python 参考实现骨架

```python
# models/fraud_mscore.py — 允许库: numpy, pandas, math, pathlib, json
import pandas as pd, math, json, pathlib
def m_score(dsri, gmi, aqi, sgi, lvgi, sgai, tata, depi):
    # 按 Beneish 1999 原文系数；调用方需传入 8 个已清洗浮点数
    return -4.87 + 0.920*dsri + 0.528*gmi + 0.404*aqi + 0.892*sgi + 0.115*lvgi - 0.172*sgai + 4.679*tata - 0.327*depi
```
