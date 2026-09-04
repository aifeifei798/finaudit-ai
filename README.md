# FinAudit AI (v1.9.0)

FinAudit AI is an AI-powered framework for high-precision financial auditing, fraud detection, and valuation modeling across **A-shares, Hong Kong, and US markets**. A 19-agent / 21-skill system automates the pipeline from raw filing extraction to professional, footnoted investment reports — with dual-mode HITL gates and model tiering.

## 🚀 Core Capabilities

| Layer | Agents |
|---|---|
| L0 Intake | **Orchestrator** (default, owns `pipeline-state.json`), **Ticker-Resolver** (cross-market code disambiguation), **Gate-Keeper** (sole HITL sign-off) |
| L1 Evidence | **Filing-Collector** (CNINFO/HKEX/EDGAR routing + 24-month regulatory-enquiry sweep + latest-quarter earnings-call transcripts + shared-cache-first batch fetching via dual ingestion drivers), **Financial Researcher** (XBRL-first parsing + dehydrated enquiry letters at footnote priority + management guidance extraction), **Evidence-Locker** (sole `_bibliography.csv` writer) |
| L2 Analysis | **Fraud Screener** (M-Score/Z-Score/Sloan + governance red-flags + footnote focus windows with cross-ref expansion + enquiry letters + flow-statement triangular audit, main-chain only), **Black Account Checker** (salted-PII private transaction forensics with treasury-pool filtering, on-demand sidecar), **Financial Analyst** (multi-doc reconciliation PIT as-reported/restated, Pre-Valuation initiator), **Industry-Peer Analyst** (peer benchmarking + consensus-divergence Alpha + macro + ESG screening), **Sentiment-Event Analyst** (event calendar + cross-period narrative-drift tracking, risk-only sidecar) |
| L3 Valuation | **Valuation Expert** (dispatcher-selected engine: DCF/Multiples/PB-ROE/DDM/rNPV + SOTP for conglomerates + ADR-normalized per-share pricing + distressed fallback + SBC/lease adjustments + Unresolved Haircut + Guidance-Divergence check), **Scenario-Sensitivity Analyst** (Bull/Base/Bear + clamped WACC×g matrix), **Portfolio Strategist** (penalty-, credit- and execution-aware sizing/concentration/stops with ADV/CTB-gated hard caps) |
| L4 Risk | **Adversarial Skeptic** (polarized short-seller CIO with measurable-evidence standard, owns Challenge Log with max-2-round fuse → tiered Unresolved), **Compliance Checker** (trilingual wording review, T3), **Judge-QA** (3-way reconciliation + penalty/price/position/flag consistency + `Dismiss without Merit`, heterogeneous T3 model) |
| L5 Output | **Report Writer** (footnoted compliant report with Consensus-Divergence, Lineage and Data-Completeness appendices), **Visualization-Excel** (living `.xlsx` with beginning-debt interest, no circular refs + chart pack, render-only) |

Model routing (`task_type→tier`, see `.opencode/model-tiers.json`): **T1** small extractors → **T2** large reasoners → **T3** heterogeneous judges; T1 low-confidence cascades to T2; every call logs `model_id/prompt_hash/token/cost` to `run_log.jsonl`.

## 📂 Workspace Architecture

Sandboxed workspace per target (canonical, sole write destination):

`workspace/targets/{TICKER}_{PERIOD}/`
- `raw/`: Original PDFs, XBRL, Excel (`YYYYMMDD_source_doctype.pdf`) + regulatory enquiries (`YYYYMMDD_source_enquiry_<topic>.pdf`, trailing 24 months) + earnings-call transcripts (`YYYYMMDD_source_transcript.pdf`, latest quarter).
- `extracted/`: Domain-chunked data + `footnotes_focus/` + `_footnote_index.csv` + `evidence_inbox/` + `_bibliography.csv` + `_reconciliation_log.csv` + `_assumptions.csv` + `_peers.csv` + `_guidance.csv` + `_consensus.csv` + `_credit.csv` + `_execution.csv` + `fx_rates.csv` + `macro_brief.md` + `_events.csv` + `_esg_flags.csv` + `history_trajectory.json` (mounted, trailing 4 periods).
- `models/`: Python scripts, `run_log.jsonl` (+ `cost_log.csv`), `lineage_manifest.json` (Top-20 pruned, ≤500KB), `MODEL_MAP.md`, `.xlsx` models, `charts/`, `position_table.csv`, `consensus_delta.csv`.
- `pipeline-state.json`: Idempotency state machine incl. `run_mode` / `restatement_policy` / `discount_currency` / `valuation_engine` / `segments` / `enquiry` / `transcript` / `guidance` / `consensus` / `credit` / `skeptic round` / `unresolved` / `risk_penalty` / `degraded_modules` / `lineage` / `webhook` (SUCCESS skips, FAILED fixes then reruns).

Shared: `workspace/params/{cn,hk,us}.yaml` (market adapters incl. `rf_anchor`/`erp`/`crp`/discount rules + `fx_conversion_timing: T0_spot` + `credit_distress_spread_bps: 800` + `max_position_adv_pct`/`ctb_block_pct`) + `valuation_routing.yaml` (GICS/SW engine dispatcher incl. conglomerate probe + distressed fallback) + `risk_penalty_matrix.yaml` (Unresolved→valuation/position haircuts) + `ingestion.yaml` (DirectScraper / InstitutionalTerminal dual drivers, identical output contract), `workspace/peer_benchmarks/` (peer library + `sw_hs_gics_mapping.csv`), `workspace/shared_filing_cache/` (rate-limited source cache, batch-first hit), `eval/` (50-case Golden Benchmark + `run_eval.py` CI gate: Recall ≥92% / FalseAlarm ≤8%), `workspace/targets/_TEMPLATE/` (scaffolding), final reports in `workspace/reports/`, HITL sign-offs + `webhook_payload.json` in `workspace/reviews/`.

## 🛡️ Guardrails & Compliance

- **Data Integrity (PIT-aware)**: live forward uses `as-restated` (latest audited restatement wins); historical backtests use `as-reported` (original vintage, `vintage_asof` frozen); deltas > 1% logged per item.
- **Normalization**: Absolute values + ISO currencies; BS spot vs IS/CF average rates separated; cross-currency targets converted once at T=0 spot (`FX: <pair> <rate> @T=0`), never per-year subjective FX forecasts.
- **Calculation Safety**: Python-first with market-tiered sanity bounds (e.g., mature WACC 4–20%, g 1.5–3.5%; see `valuation-modeling-skill` for growth/emerging/distressed tiers). Distressed fallback (BV<0 / persistent negative FCF → liquidation/Net-Net/EV-Sales, no DCF/PB-ROE) with `(WACC−g)≥1.5%` clamp; living workbooks accrue interest on beginning debt (`Interest=rate×Debt_{t-1}`), never circular.
- **Valuation Routing**: dispatcher-selected engine per `valuation_routing.yaml` — financials → PB-ROE/DDM, REITs → FFO/NAV, cyclicals → mid-cycle mean, pre-profit Biotech/SaaS → rNPV/EV-Sales; conglomerates (`is_conglomerate`) split into 2–3 segments with independent engines summed as SOTP + holding discount; forced FCFF-DCF on bypass industries raises `ValueError`. SBC/lease dual-column adjustments mandatory. Per-share pricing hardened by ADR ratio chain (`Target(ADR)=(EV−NetDebt)/Shares×Ratio×FX@T=0`).
- **Unresolved Haircut**: any `Unresolved Discrepancy` forces repricing (core accounting: g −50bps / WACC +100bps) and position hard caps (≤2% or watchlist); judge-qa blocks FINAL on flag/price/position inconsistency.
- **Evidence/Reasoning Split**: T2 reads `extracted/` + `footnotes_focus/` verbatim windows (Selective Bypass + Cross-Reference Expansion Fetching up to 2 hops), never raw PDF full text; renderers only read `*_chart_data.csv`.
- **Enquiry Parity**: 24-month regulatory enquiry letters + replies rank with footnotes in focus windows (dehydrated to 15%~20% with `dehydrate_log.csv`; cross-page tables stitched with header inheritance); screeners must read them before concluding, never claim "no regulatory challenge" when uncovered.
- **Treasury-Aware Forensics**: cash-pooling sweeps fingerprinted (memo + timing + offset, ≥2 to tag `[TREASURY_POOL]`) and excluded from malicious fast-in-out/circular counts with appendix disclosure; disguised sweeps escalate to High. Clean flows never clear a name alone — flow-statement triangular audit (cash-debt paradox / prepayment surge / flow-scale divergence) can still force red.
- **Dialectical Bench**: skeptic runs as aggressive short-seller CIO (≥3 fatal flaws / −30% price target KPI) but every charge needs measurable violation evidence; judge-qa may `Dismiss without Merit` meritless charges (closed, no penalty-matrix trigger). Evidence-free approval counts as sycophancy and is sent back.
- **Source Rate-Limiting**: Token-Bucket on L1 (EDGAR ≤8 req/s + compliant UA, CNINFO/HKEX jitter + backoff, 403 halts); `shared_filing_cache/` hit-first, no duplicate exchange requests.
- **Forward Guidance**: latest-quarter earnings-call transcripts (remarks + Q&A) feed `_guidance.csv`; model assumptions diverging > 15% from official guidance raise a `Guidance-Divergence` warning that must be explained before entering the base case.
- **Consensus Delta**: our EPS/growth/target is differenced against sell-side consensus (`_consensus.csv`→`consensus_delta.csv`); every report must state where our Alpha versus the market comes from; uncovered names print `N/A` with conviction cut one notch.
- **Credit Veto**: any live bond spread > 800bps flags `CREDIT_DISTRESS` — forced deleveraging, no bottom-fishing buys (watchlist at most); no credit coverage is a Gap, never implied safety.
- **Decision Lineage**: every key reported number carries a `derived_from` chain in `models/lineage_manifest.json` (e.g., Target ← WACC haircut ← Footnote 14 ← Enquiry Reply p.42); Top-20 critical-path nodes get full edges, intermediates use lazy hash pointers (manifest ≤500KB); judge-qa spot-checks ≥3 chains end to end.
- **Execution Reality**: position size is capped at `min(penalty cap, 10% × ADV_30D)` with slippage warnings; shorts require borrow depth with CTB ≤ 15%, otherwise downgraded to avoid/protective-put; CTB carry enters Bull/Bear P&L.
- **Narrative Drift**: trailing-4-period `history_trajectory.json` tracks management tone first-derivatives; two consecutive guidance downgrades on a core business force a yellow flag plus a promise-fulfillment ledger (risk appendix only, never touches DCF).
- **Golden Regression**: `eval/` replays 25 fraud + 25 clean cases on every agent/model upgrade; CI gate Recall ≥92% / FalseAlarm ≤8%.
- **Graceful Degradation**: missing bonds → synthetic credit score (`CREDIT_DATA: SYNTHETIC`); missing consensus → market-implied baseline (`CONSENSUS_DATA: MARKET_IMPLIED`); every gap lands in the Data Completeness Matrix and `degraded_modules[]`, never cascading failures.
- **Legal Compliance**: Audit-compliant language; no "fraud"/"fake" labels without regulatory citations.
- **PII Non-egress**: raw private flows never enter any LLM; `pii-sanitizer-skill/sanitize.py` Step 0 applies per-task salted HMAC pseudonyms (stable within one vault lifecycle, `--vault-in` keeps cross-period topology intact), vault 0600 local-only, rendered to compliance codenames then `--destroy-vault`.
- **HITL (dual-mode)**: institutional = blocking Pre-Valuation (`APPROVED`) + Pre-Publication (`SIGNED_OFF` + compliance + judge pass), signed solely by `gate-keeper`; `batch-autonomous` downgrades to `AUTO_PASSED_WITH_WARNINGS` / Unresolved-disclosure pass-through for batch screening and backtests.
- **Anti-deadlock**: Challenge Log max 2 rounds, then forced `Unresolved Discrepancy` disclosure; evidence inbox queue + file lock + atomic commit prevents concurrent `_bibliography.csv` overwrites.
- **Security**: Hook (`.opencode/plugins/hook.ts`) blocks rm-rf/dd/fork-bombs/curl-wget/curl|sh/python-network/env-leaks/git-force; read-only commands auto-allowed.

## ⌨️ Commands

All commands have `.json` + `.md` dual entries: `screen` (L0–L1 intake) · `audit` (flash fraud screen) · `dcf` (dispatcher-selected engine valuation) · `black-account` (PII-sanitized transaction forensics) · `report` (full 19-agent loop) · `qa` (L4 independent QA).

> v1.3.0 role split: `audit` → `fraud-screener` (listed-company M-Score/governance, main chain only, never touches private flows); `black-account` → `black-account-checker` (private CSV/Excel 6-step forensics, on-demand sidecar, never runs M-Score); `report` main chain uses `fraud-screener`, plus `black-account-checker` only when the user attaches private flows.
> v1.4.0: valuation dispatcher (`valuation_routing.yaml`, no forced FCFF-DCF for financials/REITs/cyclicals/pre-profit) · footnote focus windows (`footnotes_focus/`) · PII sanitizer Step 0 before any LLM sees private flows · `institutional`/`batch-autonomous` dual run modes + Challenge-Log max-2-round fuse + evidence inbox locking + `webhook_payload.json` · PIT `as-reported`/`as-restated` + cross-currency discount hardening.
> v1.5.0: mandatory Unresolved→valuation/position Haircut (`risk_penalty_matrix.yaml`) · salted deterministic PII mapping (unbroken cross-period topology + destroy-after-read) · SOTP segment dispatch (conglomerates split into 2–3 segments with independent engines, summed) · footnote cross-reference tracing (Expansion Fetching) · T=0 spot FX conversion iron rule.
> v1.6.0: regulatory-enquiry sweep (trailing-24-month enquiry letters + replies + ad-hoc announcements, ranked with footnotes) · treasury-pool fingerprint filter (`[TREASURY_POOL]` + anti-camouflage escalation) · beginning-debt interest breaking circular refs · distressed fallback (liquidation/Net-Net/EV-Sales) + `(WACC−g)≥1.5%` clamp · polarized red team (short-seller CIO + KPI, anti-sycophancy).
> v1.7.0: dialectical bench (evidentiary standard + judge's `Dismiss without Merit` against false positives) · enquiry de-hydrator (15%–20% + cross-page table stitching) · ADR/dual-class normalization (hardened ratio chain) · flow-statement triangular audit (piercing off-BS factoring) · token-bucket rate limiting + shared filing cache.
> v1.8.0: earnings-call transcripts + guidance extractor (`Guidance-Divergence` > 15% must-explain) · consensus-divergence engine (state your Alpha vs the street) · credit-spread veto (`CREDIT_DISTRESS` > 800bps) · decision lineage DAG (`lineage_manifest.json`) · ingestion abstraction layer (DirectScraper / InstitutionalTerminal, identical contract).
> v1.9.0: execution reality (ADV cap + borrow/CTB gate) · narrative-drift tracker (ΔTone + promise ledger) · Golden Benchmark regression suite (Recall ≥92% / FalseAlarm ≤8%) · critical-path lineage pruning (Top-20, ≤500KB) · graceful degradation (synthetic credit + market-implied consensus + completeness matrix).

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
