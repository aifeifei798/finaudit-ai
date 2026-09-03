# Multi-Document Financial Reasoning Skill

This skill focuses on coordinating and reconciling data across multiple financial documents with different reporting cycles, definitions, and assumptions.

## Latest Audited Restatement Rule (Anti-Restatement Trap)
When comparing data across different reporting periods, always prioritize the most recent audited filing for historical data.
- **Rule**: If a 2024 Annual Report provides "Restated" figures for 2022, these figures MUST supersede the original 2022 Annual Report.
- **Action**: Explicitly flag any discrepancies between original and restated data in the "Data Reconciliation" log.
- **Verification**: Before finalizing any trend analysis, verify if the "Comparative" columns in the latest report differ from the "Standalone" reports of previous years.

## Reconciliation Workflow
1. **Timeline Alignment**: Map out the reporting dates of all documents (e.g., 10-K vs 10-Q vs Earnings Call).
2. **Definition Mapping**: Identify how "Revenue", "EBITDA", or "Adjusted EPS" are defined in each document. Note discrepancies (e.g., GAAP vs Non-GAAP).
3. **Conflict Resolution**:
   - Prioritize: Latest Audited Restatement > Regulatory Filing > Earnings Release > Investor Presentation > Third-party Research.
   - Document the conflict and the reason for the chosen value.
4. **Assumption Tracking**: Extract and list all key assumptions (growth rates, discount rates, tax rates) used in each document.

## Reasoning Patterns
- **Trend Analysis**: Compare the same metric across multiple periods to identify anomalies.
- **Consistency Check**: Ensure that the "Summary" section of a report matches the detailed "Financial Tables".
- **Gap Analysis**: Identify what is missing from the official filings that is mentioned in research notes.
