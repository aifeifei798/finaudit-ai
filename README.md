# FinAudit AI

FinAudit AI is an AI-powered framework for high-precision financial auditing, fraud detection, and valuation modeling across **A-shares, Hong Kong, and US markets**. A 19-agent system automates the pipeline from raw filing extraction to professional, footnoted investment reports — with strict HITL gates and model tiering.

## 🚀 Core Capabilities

| Layer | Agents |
|---|---|
| L0 Intake | **Orchestrator** (default, owns `pipeline-state.json`), **Ticker-Resolver** (cross-market code disambiguation), **Gate-Keeper** (sole HITL sign-off) |
| L1 Evidence | **Filing-Collector** (CNINFO/HKEX/EDGAR routing), **Financial Researcher** (XBRL-first parsing), **Evidence-Locker** (sole `_bibliography.csv` writer) |
| L2 Analysis | **Fraud Screener** (M-Score/Z-Score/Sloan + governance red-flags, main-chain only), **Black Account Checker** (private transaction forensics, on-demand sidecar), **Financial Analyst** (multi-doc reconciliation, Pre-Valuation initiator), **Industry-Peer Analyst** (peer benchmarking + macro + ESG screening), **Sentiment-Event Analyst** (event calendar, risk-only sidecar) |
| L3 Valuation | **Valuation Expert** (DCF/WACC pricing), **Scenario-Sensitivity Analyst** (Bull/Base/Bear + WACC×g matrix), **Portfolio Strategist** (sizing/concentration/stops) |
| L4 Risk | **Adversarial Skeptic** (short-seller red team, owns Challenge Log), **Compliance Checker** (trilingual wording review, T3), **Judge-QA** (3-way number reconciliation, heterogeneous T3 model) |
| L5 Output | **Report Writer** (footnoted compliant report), **Visualization-Excel** (living `.xlsx` + chart pack, render-only) |

Model routing (`task_type→tier`, see `.opencode/model-tiers.json`): **T1** small extractors → **T2** large reasoners → **T3** heterogeneous judges; T1 low-confidence cascades to T2; every call logs `model_id/prompt_hash/token/cost` to `run_log.jsonl`.

## 📂 Workspace Architecture

Sandboxed workspace per target (canonical, sole write destination):

`workspace/targets/{TICKER}_{PERIOD}/`
- `raw/`: Original PDFs, XBRL, Excel (`YYYYMMDD_source_doctype.pdf`).
- `extracted/`: Domain-chunked data + `_bibliography.csv` + `_reconciliation_log.csv` + `_assumptions.csv` + `_peers.csv` + `fx_rates.csv` + `macro_brief.md` + `_events.csv` + `_esg_flags.csv`.
- `models/`: Python scripts, `run_log.jsonl` (+ `cost_log.csv`), `MODEL_MAP.md`, `.xlsx` models, `charts/`, `position_table.csv`.
- `pipeline-state.json`: Idempotency state machine (16 stages; SUCCESS skips, FAILED fixes then reruns).

Shared: `workspace/params/{cn,hk,us}.yaml` (market adapters), `workspace/peer_benchmarks/` (peer library + `sw_hs_gics_mapping.csv`), `workspace/targets/_TEMPLATE/` (scaffolding), final reports in `workspace/reports/`, HITL sign-offs in `workspace/reviews/`.

## 🛡️ Guardrails & Compliance

- **Data Integrity**: Latest audited restated figures win; deltas > 1% logged per item.
- **Normalization**: Absolute values + ISO currencies; BS spot vs IS/CF average rates separated.
- **Calculation Safety**: Python-first with market-tiered sanity bounds (e.g., mature WACC 4–20%, g 1.5–3.5%; see `valuation-modeling-skill` for growth/emerging/distressed tiers).
- **Evidence/Reasoning Split**: T2 never reads raw PDFs, only `extracted/`; renderers only read `*_chart_data.csv`.
- **Legal Compliance**: Audit-compliant language; no "fraud"/"fake" labels without regulatory citations.
- **HITL (strict, no bypass)**: Pre-Valuation (`analyst_gate: APPROVED`) and Pre-Publication (`skeptic: SIGNED_OFF` + compliance pass + judge pass), both signed solely by `gate-keeper`.
- **Security**: Hook (`.opencode/plugins/hook.ts`) blocks rm-rf/dd/fork-bombs/curl-wget/curl|sh/python-network/env-leaks/git-force; read-only commands auto-allowed.

## ⌨️ Commands

All commands have `.json` + `.md` dual entries: `screen` (L0–L1 intake) · `audit` (flash fraud screen) · `dcf` (pure valuation) · `black-account` (transaction forensics) · `report` (full 19-agent loop) · `qa` (L4 independent QA).

> v1.3.0 role split: `audit` → `fraud-screener` (listed-company M-Score/governance, main chain only, never touches private flows); `black-account` → `black-account-checker` (private CSV/Excel 6-step forensics, on-demand sidecar, never runs M-Score); `report` main chain uses `fraud-screener`, plus `black-account-checker` only when the user attaches private flows.

## 🛠️ Technical Stack

- **Runtime**: Node.js / TypeScript (opencode-ai plugin system)
- **Analysis**: Python (NumPy, Pandas, SciPy, Openpyxl, Matplotlib)
- **Configuration**: `opencode.json` (agent/skill map) + `.opencode/model-tiers.json` (T1/T2/T3)

## 🏁 Getting Started

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Agents**:
   Review `opencode.json` to map agents to their respective skills.

3. **Run Analysis**:
   ```bash
   # screen a target, run the full report loop, then independently QA it
   opencode run screen --target NVDA_FY2024
   opencode run report --target NVDA_FY2024
   opencode run qa --target NVDA_FY2024
   ```
   The system checks `pipeline-state.json` to resume from the last successful stage.

## 📄 License

Proprietary - For internal financial audit use only.
