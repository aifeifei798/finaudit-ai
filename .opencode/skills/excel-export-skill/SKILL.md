# Excel Export Skill

This skill enables the generation of "Living Excel" models where the output is not just a static table, but a functional spreadsheet with active formulas.

## Technical Implementation
- **Library**: Use `openpyxl` for creating .xlsx files with formulas.
- **Formula Injection**: Instead of writing the result of a calculation (e.g., `100 * 1.05`), write the Excel formula (e.g., `=B2*C2`).
- **Structure**:
  - **Assumptions Sheet**: All input variables (Growth Rate, WACC, Tax Rate) in a dedicated sheet.
  - **Calculation Sheet**: Linked to the Assumptions sheet.
  - **Summary Sheet**: High-level outputs (Enterprise Value, Share Price) linked to the Calculation sheet.

## Delivery Standard
1. **Dynamic Inputs**: The user must be able to change a single cell in the "Assumptions" sheet and see the final valuation update automatically.
2. **Balance Check**: Include a "Check" column that returns `TRUE` if Assets = Liabilities + Equity, and `FALSE` otherwise.
3. **Audit Trail**: Every formula must be simple and traceable. Avoid complex array formulas that are hard to audit.

## Export Workflow
- **Step 1**: Define the model structure in Python.
- **Step 2**: Write the formulas into the cells using `openpyxl`.
- **Step 3**: Save the file to `workspace/models/[Company]_Valuation_Model.xlsx`.
- **Step 4**: Provide the file path in the final report.
