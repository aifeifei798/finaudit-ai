# FinAudit AI (v1.5.0)

FinAudit AI is an AI-powered framework for high-precision financial auditing, fraud detection, and valuation modeling across **A-shares, Hong Kong, and US markets**. A 19-agent / 20-skill system automates the pipeline from raw filing extraction to professional, footnoted investment reports — with dual-mode HITL gates and model tiering.

## 🚀 Core Capabilities

| Layer | Agents |
|---|---|
| L0 Intake | **Orchestrator** (default, owns `pipeline-state.json`), **Ticker-Resolver** (cross-market code disambiguation), **Gate-Keeper** (sole HITL sign-off) |
| L1 Evidence | **Filing-Collector** (CNINFO/HKEX/EDGAR routing), **Financial Researcher** (XBRL-first parsing), **Evidence-Locker** (sole `_bibliography.csv` writer) |
| L2 Analysis | **Fraud Screener** (M-Score/Z-Score/Sloan + governance red-flags + footnote focus windows with cross-ref expansion, main-chain only), **Black Account Checker** (salted-PII private transaction forensics, on-demand sidecar), **Financial Analyst** (multi-doc reconciliation PIT as-reported/restated, Pre-Valuation initiator), **Industry-Peer Analyst** (peer benchmarking + macro + ESG screening), **Sentiment-Event Analyst** (event calendar, risk-only sidecar) |
| L3 Valuation | **Valuation Expert** (dispatcher-selected engine: DCF/Multiples/PB-ROE/DDM/rNPV + SOTP for conglomerates + SBC/lease adjustments + Unresolved Haircut), **Scenario-Sensitivity Analyst** (Bull/Base/Bear + WACC×g matrix), **Portfolio Strategist** (penalty-aware sizing/concentration/stops with position hard caps) |
| L4 Risk | **Adversarial Skeptic** (short-seller red team, owns Challenge Log with max-2-round fuse → tiered Unresolved), **Compliance Checker** (trilingual wording review, T3), **Judge-QA** (3-way reconciliation + penalty/price/position/flag consistency, heterogeneous T3 model) |
| L5 Output | **Report Writer** (footnoted compliant report), **Visualization-Excel** (living `.xlsx` + chart pack, render-only) |

Model routing (`task_type→tier`, see `.opencode/model-tiers.json`): **T1** small extractors → **T2** large reasoners → **T3** heterogeneous judges; T1 low-confidence cascades to T2; every call logs `model_id/prompt_hash/token/cost` to `run_log.jsonl`.

## 📂 Workspace Architecture

Sandboxed workspace per target (canonical, sole write destination):

`workspace/targets/{TICKER}_{PERIOD}/`
- `raw/`: Original PDFs, XBRL, Excel (`YYYYMMDD_source_doctype.pdf`).
- `extracted/`: Domain-chunked data + `footnotes_focus/` + `_footnote_index.csv` + `evidence_inbox/` + `_bibliography.csv` + `_reconciliation_log.csv` + `_assumptions.csv` + `_peers.csv` + `fx_rates.csv` + `macro_brief.md` + `_events.csv` + `_esg_flags.csv`.
- `models/`: Python scripts, `run_log.jsonl` (+ `cost_log.csv`), `MODEL_MAP.md`, `.xlsx` models, `charts/`, `position_table.csv`.
- `pipeline-state.json`: Idempotency state machine incl. `run_mode` / `restatement_policy` / `discount_currency` / `valuation_engine` / `segments` / `skeptic round` / `unresolved` / `risk_penalty` / `webhook` (SUCCESS skips, FAILED fixes then reruns).

Shared: `workspace/params/{cn,hk,us}.yaml` (market adapters incl. `rf_anchor`/`erp`/`crp`/discount rules + `fx_conversion_timing: T0_spot`) + `valuation_routing.yaml` (GICS/SW engine dispatcher incl. conglomerate probe) + `risk_penalty_matrix.yaml` (Unresolved→valuation/position haircuts), `workspace/peer_benchmarks/` (peer library + `sw_hs_gics_mapping.csv`), `workspace/targets/_TEMPLATE/` (scaffolding), final reports in `workspace/reports/`, HITL sign-offs + `webhook_payload.json` in `workspace/reviews/`.

## 🛡️ Guardrails & Compliance

- **Data Integrity (PIT-aware)**: live forward uses `as-restated` (latest audited restatement wins); historical backtests use `as-reported` (original vintage, `vintage_asof` frozen); deltas > 1% logged per item.
- **Normalization**: Absolute values + ISO currencies; BS spot vs IS/CF average rates separated; cross-currency targets converted once at T=0 spot (`FX: <pair> <rate> @T=0`), never per-year subjective FX forecasts.
- **Calculation Safety**: Python-first with market-tiered sanity bounds (e.g., mature WACC 4–20%, g 1.5–3.5%; see `valuation-modeling-skill` for growth/emerging/distressed tiers).
- **Valuation Routing**: dispatcher-selected engine per `valuation_routing.yaml` — financials → PB-ROE/DDM, REITs → FFO/NAV, cyclicals → mid-cycle mean, pre-profit Biotech/SaaS → rNPV/EV-Sales; conglomerates (`is_conglomerate`) split into 2–3 segments with independent engines summed as SOTP + holding discount; forced FCFF-DCF on bypass industries raises `ValueError`. SBC/lease dual-column adjustments mandatory.
- **Unresolved Haircut**: any `Unresolved Discrepancy` forces repricing (core accounting: g −50bps / WACC +100bps) and position hard caps (≤2% or watchlist); judge-qa blocks FINAL on flag/price/position inconsistency.
- **Evidence/Reasoning Split**: T2 reads `extracted/` + `footnotes_focus/` verbatim windows (Selective Bypass + Cross-Reference Expansion Fetching up to 2 hops), never raw PDF full text; renderers only read `*_chart_data.csv`.
- **Legal Compliance**: Audit-compliant language; no "fraud"/"fake" labels without regulatory citations.
- **PII Non-egress**: raw private flows never enter any LLM; `pii-sanitizer-skill/sanitize.py` Step 0 applies per-task salted HMAC pseudonyms (stable within one vault lifecycle, `--vault-in` keeps cross-period topology intact), vault 0600 local-only, rendered to compliance codenames then `--destroy-vault`.
- **HITL (dual-mode)**: institutional = blocking Pre-Valuation (`APPROVED`) + Pre-Publication (`SIGNED_OFF` + compliance + judge pass), signed solely by `gate-keeper`; `batch-autonomous` downgrades to `AUTO_PASSED_WITH_WARNINGS` / Unresolved-disclosure pass-through for batch screening and backtests.
- **Anti-deadlock**: Challenge Log max 2 rounds, then forced `Unresolved Discrepancy` disclosure; evidence inbox queue + file lock + atomic commit prevents concurrent `_bibliography.csv` overwrites.
- **Security**: Hook (`.opencode/plugins/hook.ts`) blocks rm-rf/dd/fork-bombs/curl-wget/curl|sh/python-network/env-leaks/git-force; read-only commands auto-allowed.

## ⌨️ Commands

All commands have `.json` + `.md` dual entries: `screen` (L0–L1 intake) · `audit` (flash fraud screen) · `dcf` (dispatcher-selected engine valuation) · `black-account` (PII-sanitized transaction forensics) · `report` (full 19-agent loop) · `qa` (L4 independent QA).

> v1.3.0 role split: `audit` → `fraud-screener` (listed-company M-Score/governance, main chain only, never touches private flows); `black-account` → `black-account-checker` (private CSV/Excel 6-step forensics, on-demand sidecar, never runs M-Score); `report` main chain uses `fraud-screener`, plus `black-account-checker` only when the user attaches private flows.
> v1.4.0: valuation dispatcher (`valuation_routing.yaml`, no forced FCFF-DCF for financials/REITs/cyclicals/pre-profit) · footnote focus windows (`footnotes_focus/`) · PII sanitizer Step 0 before any LLM sees private flows · `institutional`/`batch-autonomous` dual run modes + Challenge-Log max-2-round fuse + evidence inbox locking + `webhook_payload.json` · PIT `as-reported`/`as-restated` + cross-currency discount hardening.
> v1.5.0: Unresolved→估值/仓位强制 Haircut（`risk_penalty_matrix.yaml`）· PII 加盐确定性映射（跨期不断链+阅后销毁）· SOTP 分部调度（集团拆 2–3 分部独立引擎加总）· 附注交叉引用追溯（Expansion Fetching）· FX 折算 T=0 即期单点铁律。

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
    # batch screening / backtests (non-blocking gates + as-reported PIT)
    opencode run report --target universe_batch --mode batch-autonomous --restatement-policy as-reported
    # private-flow forensics (PII sanitized locally first, never sent raw to LLMs)
    opencode run black-account --input private_flows.csv
    ```
    The system checks `pipeline-state.json` to resume from the last successful stage.

## 📄 License

Proprietary - For internal financial audit use only.
