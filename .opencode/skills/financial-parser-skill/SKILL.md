# Financial Parser Skill

This skill ensures that raw financial documents (PDFs, XBRL, Excel) are converted into high-fidelity structured data before analysis.

## Unit & Currency Normalization (Anti-Unit Chaos)
To prevent magnitude errors (e.g., confusing millions with billions), all extracted data must be normalized:
- **Standardization**: Convert all values to absolute numbers (e.g., "1.2 billion" $\rightarrow$ 1,200,000,000).
- **Currency ISO**: Tag every value with its ISO 4217 currency code (e.g., USD, CNY, JPY).
- **FX Rate Logic**: 
  - Balance Sheet items $\rightarrow$ Use Spot Rate at reporting date.
  - Income Statement/Cash Flow items $\rightarrow$ Use Average Rate for the period.
- **Verification**: Cross-check the "Units" header of every table (e.g., "In thousands of USD") and apply the multiplier strictly.

## Domain-Chunked Parsing (Anti-Context Overflow)
Avoid dumping entire reports into a single file. Split extracted data into domain-specific chunks in `workspace/extracted/`:
- `financial_statements/`: Three main statements (BS, IS, CF).
- `notes_debt/`: Debt, loans, and guarantees footnotes.
- `notes_revenue/`: Revenue recognition and segment data.
- `related_parties/`: Related party transactions and ownership.
- `management_discussion/`: MD&A and strategic outlook.
- `audit_opinion/`: Auditor's report and key audit matters.

## Extraction Standards
1. **Table Integrity**: Use specialized PDF table extraction tools to maintain row/column alignment. Never rely on raw text flow for tables.
2. **Footnote Mapping**: Every number in a financial table must be checked for associated footnotes. These footnotes must be extracted and linked to the specific data point.
3. **XBRL Integration**: For SEC filings, prioritize XBRL tags over OCR/text parsing.
4. **Formula Preservation**: Extract the underlying formula from .xlsx files rather than just the calculated value.

## Validation Workflow
- **Cross-Check**: Sum the individual line items in a table and compare with the reported total. If they differ, flag as "Parsing Error".
- **Unit Verification**: Explicitly identify the currency and scale for every extracted table.
- **Page Anchoring**: Every extracted data point must be tagged with the source file name and page number.
