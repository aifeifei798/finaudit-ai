# Financial Research Skill

This skill enables the agent to perform end-to-end financial research by integrating information retrieval, evidence review, and authoritative sourcing.

## Core Methodology
1. **Authoritative Sourcing**: Prioritize official filings (SEC EDGAR, HKEX, SEDAR), company investor relations pages, and recognized financial data providers (Bloomberg, Reuters, FactSet).
2. **Evidence Tracing**: Every claim must be linked to a specific page/section of a source document. Use `source_file:page_number` or `URL#section`.
3. **Cross-Verification**: Compare data across at least two independent authoritative sources to resolve discrepancies.
4. **Information Synthesis**: Move from raw data -> evidence -> analysis -> conclusion.

## Search Strategy
- Use specific keywords for regulatory filings (e.g., "Form 10-K", "Annual Report 2023", "Earnings Presentation").
- Search for "Investor Relations" or "IR" portals of the target company.
- Use `webfetch` to retrieve PDF/HTML filings and `grep` to locate key financial metrics.

## Output Requirements
- All findings must be presented as a list of "Fact | Source | Confidence Level".
- Highlight any gaps in available information.
