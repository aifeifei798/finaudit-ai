# Governance Red Flags Skill

This skill is designed to identify non-financial warning signs (red flags) in corporate governance and executive behavior that often precede financial collapse or fraud.

## Audit Focus Areas

### 1. Auditor & Accounting Firm Stability
- **Auditor Resignation**: Search for "resignation", "dismissal", "disagreement with auditor" in annual reports, regulatory filings, or news.
- **Frequent Auditor Changes**: Check the history of accounting firms over the last 3-5 years. Frequent changes are a high-risk signal.
- **Qualified Opinions**: Identify any "qualified opinion" or "emphasis of matter" in the auditor's report.

### 2. Executive Turnover (CFO/CEO)
- **CFO Departures**: Track the tenure of the Chief Financial Officer. Sudden departures, especially before annual report releases, are critical red flags.
- **Board Instability**: Frequent changes in the board of directors or audit committee members.

### 3. Share Pledge & Control Risks
- **Pledge Ratio**: Calculate the percentage of shares pledged by the controlling shareholder/actual controller.
- **Threshold**: A pledge ratio > 70% is a severe warning; > 80% is critical (risk of forced liquidation).
- **Margin Call History**: Search for mentions of margin calls or pledge fulfillment issues.

### 4. Abnormal Asset/Liability Movements
- **Non-Recurring Guarantees**: Identify large guarantees provided to related parties or third parties that are not part of normal business operations.
- **Emergency Asset Disposals**: Look for "fire sales" of core assets at the end of the fiscal year to meet profit targets (window dressing).
- **Related Party Transactions**: Audit large, unusual transactions with entities controlled by the same shareholders.

## Workflow
1. **Scan Filings**: Use `financial-researcher` to extract sections on "Corporate Governance", "Related Party Transactions", and "Auditor's Report".
2. **Cross-Reference**: Compare current auditor/CFO with previous years' reports.
3. **Quantify Pledges**: Extract total shares pledged vs. total shares held by the controller.
4. **Flag & Cite**: For every red flag found, provide the exact page/paragraph citation and assign a risk level (Low, Medium, High, Critical).

## Output Format
| Red Flag Category | Finding | Risk Level | Citation |
| :--- | :--- | :--- | :--- |
| Auditor | Auditor resigned due to "disagreement on revenue recognition" | Critical | Page 142, Para 3 |
| Executive | CFO resigned 2 weeks before FY2023 audit | High | News Release 2024-01-10 |
| Pledges | Controller pledge ratio at 82% | Critical | Note 12, Page 88 |
| Assets | Sold core factory to related party at 40% discount | High | Note 21, Page 95 |
