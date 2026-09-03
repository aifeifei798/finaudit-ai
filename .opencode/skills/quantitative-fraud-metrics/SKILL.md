# Quantitative Fraud Metrics Skill

This skill provides a rigorous mathematical framework for detecting financial manipulation, moving beyond qualitative "red flags" to quantitative "tripwires".

## 1. Beneish M-Score Model
The M-Score is used to identify the probability of earnings manipulation. A score > -1.78 suggests a high likelihood of manipulation.

**Formula Components:**
- **DSRI (Days Sales in Receivables Index)**: (Net Receivables_t / Net Sales_t) / (Net Receivables_{t-1} / Net Sales_{t-1})
- **GMI (Gross Margin Index)**: Gross Margin_{t-1} / Gross Margin_t
- **AQI (Asset Quality Index)**: [1 - (Current Assets + Depreciable Assets)_t / Total Assets_t] / [1 - (Current Assets + Depreciation)_t-1 / Total Assets_{t-1}]
- **SGI (Sales Growth Index)**: Net Sales_t / Net Sales_{t-1}
- **PLTA (Leverage Index)**: Total Liabilities_t / Total Assets_t / (Total Liabilities_{t-1} / Total Assets_{t-1})
- **DEPI (Depreciation Index)**: Depreciation_{t-1} / Depreciation_t
- **SGAI (SG&A Expenses Index)**: (SGA_t / Sales_t) / (SGA_{t-1} / Sales_{t-1})
- **TATA (Total Accruals to Total Assets)**: (Income from Ops - Cash Flow from Ops) / Total Assets

**M-Score Formula**: 
M = -4.87 + 0.920*DSRI - 0.048*GMI + 0.404*AQI + 0.892*SGI - 0.115*PLTA + 0.468*DEPI - 0.327*SGAI + 1.137*TATA

## 2. "High Cash, High Debt" Paradox (The "Kangmei" Trigger)
Detects companies that report massive cash balances while simultaneously borrowing heavily at high rates.

**Trigger Conditions**:
- **Cash-to-Debt Ratio**: (Cash & Equivalents) / (Short-term Debt + Current Portion of Long-term Debt) > 1.5
- **Interest Coverage Gap**: (Interest Expense / Average Cash) > 0.05 (meaning they pay significant interest while holding idle cash)
- **Cash Flow Divergence**: (Net Income - Operating Cash Flow) / Total Assets > 0.10 for 3 consecutive years.

## 3. Execution Protocol
- **Step 1**: Extract the 8 required variables from the Balance Sheet and Income Statement.
- **Step 2**: Run the M-Score calculation via Python.
- **Step 3**: Check for "High Cash, High Debt" paradox.
- **Step 4**: If any trigger is hit, the `black-account-checker` must elevate the risk rating to 🔴 (High) and demand a "Cash Verification" evidence block.
