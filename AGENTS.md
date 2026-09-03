# Agents Guide - FinAudit AI

## Agents & Skills
- `black-account-checker` (Default): Audit/fraud detection. Skills: `black-account-checker`, `quantitative-fraud-metrics`, `governance-redflags-skill`.
- `financial-researcher`: IR/source verification. Skills: `financial-research-skill`, `financial-parser-skill`.
- `financial-analyst`: Multi-doc reasoning. Skill: `multi-doc-reasoning-skill`.
- `valuation-expert`: Modeling. Skills: `valuation-modeling-skill`, `peer-comparison-skill`, `excel-export-skill`.
- `adversarial-skeptic`: Red-teaming. Skill: `adversarial-skeptic-skill`.
- `report-writer`: Final output. Skills: `professional-reporting-skill`, `citation-engine-skill`.

## Workspace
- `workspace/targets/{TICKER}_{PERIOD}/`: Independent sandbox for each target.
  - `raw/`: Original PDFs, XBRL, Excel filings.
  - `extracted/`: Domain-chunked structured data.
  - `models/`: Python scripts, execution logs, `.xlsx` models.
  - `pipeline-state.json`: State record for idempotency (e.g., `{"parser": "SUCCESS", "analyst": "SUCCESS", "valuation": "PENDING"}`).
- `workspace/peer_benchmarks/`: Shared industry peer database.
- `workspace/reports/`: Final footnoted reports.

## Guardrails
1. **Restatement**: Prioritize latest audited restated figures over original reports.
2. **Unit/FX**: Normalize to absolute values/ISO currencies; separate spot vs average rates.
3. **Calculation**: Python-only math with sanity bounds (WACC 4-20%, g 1.5-3.5%).
4. **Legal**: Audit-compliant language; no "fraud/fake" without regulatory citations.
5. **Context**: Domain-chunked parsing for large reports.
6. **Python Sandbox**:
   - Allowed libraries: `numpy`, `pandas`, `scipy`, `openpyxl`, `math`.
   - No network access (no `requests`, `akshare`, `yfinance`, etc.).
   - No access to system environment variables (e.g., `os.environ`).
   - All scripts must be written to the target's `models/` directory.
7. **Idempotency**: Check `pipeline-state.json` before starting any stage; skip if `SUCCESS`. Update state immediately upon stage completion.

## HITL Gates
- **Pre-Valuation**: `financial-analyst` must request confirmation for data conflicts/abnormal adjustments.
- **Pre-Publication**: `adversarial-skeptic` challenges must be signed off before `report-writer` finalizes.

## Infrastructure & Tooling
- **Config**: `opencode.json` (Agent/Skill mappings).
- **Safety**: `.opencode/plugins/hook.ts` blocks dangerous bash; sets `FINANCIAL_AUDIT_MODE=strict`.
- **Env**: `BLACK_ACCOUNT_AUDIT=1`, `AUDIT_MODE=strict`, `FINANCIAL_AUDIT_mode=strict`.
- **Log Analysis**: Use `awk`, `sort`, `uniq`, `grep` for transaction logs.
