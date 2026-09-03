# FinAudit AI

FinAudit AI is an AI-powered framework designed for high-precision financial auditing, fraud detection, and valuation modeling. It leverages a multi-agent system to automate the pipeline from raw financial data extraction to professional, footnoted investment reports.

## 🚀 Core Capabilities

The suite employs specialized agents to ensure rigorous analysis and compliance:

- **Black Account Checker**: Audits transaction logs for fraud detection, AML (Anti-Money Laundering) analysis, and suspicious account investigation.
- **Financial Researcher**: Handles authoritative data retrieval and high-fidelity structured data extraction (parsing) from raw filings.
- **Financial Analyst**: Central analysis hub; performs multi-document reasoning, peer benchmarking, quantitative fraud metrics (e.g., M-Score), and corporate governance red-flag detection.
- **Valuation Expert**: Builds financial models (DCF, WACC) and exports functional Excel models.
- **Adversarial Skeptic**: Red-teams the findings to challenge assumptions and identify blind spots.
- **Report Writer**: Synthesizes all findings into a professional, audit-compliant report with strict citations and neutral language.

## 📂 Workspace Architecture

The system uses a sandboxed workspace for each target entity to ensure data isolation and idempotency:

`workspace/targets/{TICKER}_{PERIOD}/`
- `raw/`: Original PDFs, XBRL, and Excel filings.
- `extracted/`: Domain-chunked structured data.
- `models/`: Python scripts, execution logs, and `.xlsx` models.
- `pipeline-state.json`: Tracks stage completion (e.g., `parser`, `analyst`, `valuation`).

Shared resources are located in `workspace/peer_benchmarks/` and final outputs in `workspace/reports/`.

## 🛡️ Guardrails & Compliance

To maintain institutional-grade accuracy, the suite enforces the following rules:

- **Data Integrity**: Prioritizes latest audited restated figures over original reports.
- **Normalization**: All values are normalized to absolute ISO currencies; spot and average rates are separated.
- **Calculation Safety**: All math is performed in a Python sandbox with strict sanity bounds (e.g., WACC 4-20%, g 1.5-3.5%).
- **Legal Compliance**: Uses audit-compliant language; no "fraud" or "fake" labels without regulatory citations.
- **Security**: A custom plugin hook (`.opencode/plugins/hook.ts`) blocks dangerous bash commands and enforces `FINANCIAL_AUDIT_mode=strict`.

## 🛠️ Technical Stack

- **Runtime**: Node.js / TypeScript
- **AI Framework**: opencode-ai plugin system
- **Analysis**: Python (NumPy, Pandas, SciPy, Openpyxl)
- **Configuration**: `opencode.json` for agent/skill mapping

## 🏁 Getting Started

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Agents**:
   Review `opencode.json` to map agents to their respective skills.

3. **Run Analysis**:
   Initiate the pipeline for a specific ticker and period. The system will automatically check `pipeline-state.json` to resume from the last successful stage.

## 📄 License

Proprietary - For internal financial audit use only.
