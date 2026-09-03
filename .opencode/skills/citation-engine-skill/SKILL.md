# Citation & Footnote Engine Skill

This skill enforces strict traceability and compliance in financial reporting, ensuring every claim is anchored to a verifiable source.

## Audit Compliance Language (Anti-Defamation)
- **Rule**: All citations must be neutral. Avoid using citations to "prove" a crime; instead, use them to "highlight a discrepancy".
- **Example**: Instead of "The CEO lied [p. 12]", use "The CEO's statement on p. 12 contradicts the audited cash flow statement on p. 45".

## Citation Standards
1. **In-line Citations**: Every key number, fact, or judgment must be followed by a citation in brackets.
   - Format: `[Source Document, Page X, Table Y]` or `[Python Calc ID #123]`.
   - Example: "The 2023 EBITDA was $450M [Annual Report 2023, p. 42, Table 2.1]."
2. **Calculation Traceability**: Any number derived from a calculation must refer to the specific Python code block used.
   - Example: "Implied Enterprise Value is $12.4B [Python Calc #45: DCF_Model_v1]."
3. **Source Hierarchy**:
   - Primary: SEC Filings, Audited Financials, Official Press Releases.
   - Secondary: Investor Presentations, Analyst Reports, Industry Data.
   - Tertiary: News Articles, Blogs.

## Compliance & Disclaimers
- **Disclaimer Injection**: Every report must end with a standard legal disclaimer:
  - "This report is for informational purposes only and does not constitute investment advice."
  - "The analysis is based on publicly available data and assumptions which may be subject to change."
- **Conflict Disclosure**: Explicitly state any known conflicts of interest.

## Final Review Checklist
- [ ] Does every number have a source?
- [ ] Are all Python calculations linked?
- [ ] Is the disclaimer present?
- [ ] Are page numbers provided for all PDF references?
- [ ] Has all "defamatory" language been replaced with audit-compliant terminology?
