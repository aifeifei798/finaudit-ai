# Valuation and Modeling Skill

This skill provides the framework for building and auditing financial models, ensuring mathematical integrity and scenario robustness.

## MANDATORY: Python-First Calculation
To eliminate LLM arithmetic hallucinations, ALL financial calculations must be performed using Python code executed in a sandbox.
- **NO** mental math or text-based calculations for: DCF, WACC, LBO, Multiples, or Three-Statement balancing.
- **Workflow**: 
  1. Define the formula in the report.
  2. Write a Python script using NumPy/Pandas to execute the calculation.
  3. Use the exact output from the Python execution in the final text.
  4. Cite the calculation as `[Python Calc #ID]`.
- **Sandbox Path**: All scripts must be written to the target's `models/` directory (e.g., `workspace/targets/{TICKER}_{PERIOD}/models/`).

## Python Sandbox Restrictions
To ensure security and stability, all Python scripts must adhere to the following:
- **Library Whitelist**: Only the following libraries are permitted: `numpy`, `pandas`, `scipy`, `openpyxl`, `math`.
- **No Network Access**: Use of `requests`, `akshare`, `yfinance`, or any other networking library is strictly forbidden. All data must be read from the `extracted/` or `raw/` directories.
- **No Environment Access**: Access to `os.environ` or system environment variables is forbidden to prevent API key leakage.
- **Execution**: Scripts are executed in a stripped environment; do not rely on system-level configurations.

## Financial Sanity Bounds (Anti-Hallucination Tripwires)
Every Python script MUST include a validation block to check for economically absurd results. If a value falls outside these bounds, the script must raise a `ValueError` and trigger a re-evaluation of assumptions:
- **WACC (Weighted Average Cost of Capital)**: Must be between `[4%, 20%]`.
- **Terminal Growth Rate (g)**: Must be between `[1.5%, 3.5%]`. (Cannot exceed global GDP growth).
- **Multiples (P/E, P/S, EV/EBITDA)**: Must be positive. If negative, mark as `N/A` and do not include in averages.
- **Debt/Equity Ratio**: If > 5.0, trigger a "High Leverage Warning" and require a solvency check.
- **Revenue Growth**: If > 100% or < -50% for a mature company, trigger a "Growth Anomaly Warning".

## Modeling Principles
1. **Hardcode Minimization**: All inputs must be in a dedicated "Assumptions" section. No hardcoded numbers inside formulas.
2. **Formula Transparency**: Use clear, traceable formulas. Avoid deeply nested IF statements; use helper rows/columns.
3. **Balance Checks**: Every model must have a "Balance Check" (e.g., Assets - Liabilities - Equity = 0). Any non-zero result must trigger a warning.
4. **Actuals vs. Forecasts**: Clearly distinguish between historical data (actuals) and projected data (forecasts) using different formatting or separate sheets.

## Workflow for Spreadsheet Tasks
- **Audit**: Trace the flow of a specific value from the final output back to the raw assumption.
- **Scenario Analysis**: Create "Base", "Bull", and "Bear" cases by varying key drivers (e.g., Revenue Growth, WACC).
- **Sensitivity Analysis**: Build data tables to show how the valuation changes with +/- 1% shifts in critical variables.

## Deliverables
- Provide models in a format that is editable (CSV/XLSX compatible) with a "Model Map" explaining the structure.
