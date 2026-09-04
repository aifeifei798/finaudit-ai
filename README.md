# FinAudit AI (v1.7.0)

FinAudit AI is an AI-powered framework for high-precision financial auditing, fraud detection, and valuation modeling across **A-shares, Hong Kong, and US markets**. A 19-agent / 20-skill system automates the pipeline from raw filing extraction to professional, footnoted investment reports — with dual-mode HITL gates and model tiering.

## 🚀 Core Capabilities

| Layer | Agents |
|---|---|
| L0 Intake | **Orchestrator** (default, owns `pipeline-state.json`), **Ticker-Resolver** (cross-market code disambiguation), **Gate-Keeper** (sole HITL sign-off) |
| L1 Evidence | **Filing-Collector** (CNINFO/HKEX/EDGAR routing + 24-month regulatory-enquiry sweep + shared-cache-first batch fetching), **Financial Researcher** (XBRL-first parsing + dehydrated enquiry letters at footnote priority), **Evidence-Locker** (sole `_bibliography.csv` writer) |
| L2 Analysis | **Fraud Screener** (M-Score/Z-Score/Sloan + governance red-flags + footnote focus windows with cross-ref expansion + enquiry letters + flow-statement triangular audit, main-chain only), **Black Account Checker** (salted-PII private transaction forensics with treasury-pool filtering, on-demand sidecar), **Financial Analyst** (multi-doc reconciliation PIT as-reported/restated, Pre-Valuation initiator), **Industry-Peer Analyst** (peer benchmarking + macro + ESG screening), **Sentiment-Event Analyst** (event calendar, risk-only sidecar) |
| L3 Valuation | **Valuation Expert** (dispatcher-selected engine: DCF/Multiples/PB-ROE/DDM/rNPV + SOTP for conglomerates + ADR-normalized per-share pricing + distressed fallback + SBC/lease adjustments + Unresolved Haircut), **Scenario-Sensitivity Analyst** (Bull/Base/Bear + clamped WACC×g matrix), **Portfolio Strategist** (penalty-aware sizing/concentration/stops with position hard caps) |
| L4 Risk | **Adversarial Skeptic** (polarized short-seller CIO with measurable-evidence standard, owns Challenge Log with max-2-round fuse → tiered Unresolved), **Compliance Checker** (trilingual wording review, T3), **Judge-QA** (3-way reconciliation + penalty/price/position/flag consistency + `Dismiss without Merit`, heterogeneous T3 model) |
| L5 Output | **Report Writer** (footnoted compliant report), **Visualization-Excel** (living `.xlsx` with beginning-debt interest, no circular refs + chart pack, render-only) |

Model routing (`task_type→tier`, see `.opencode/model-tiers.json`): **T1** small extractors → **T2** large reasoners → **T3** heterogeneous judges; T1 low-confidence cascades to T2; every call logs `model_id/prompt_hash/token/cost` to `run_log.jsonl`.

## 📂 Workspace Architecture

Sandboxed workspace per target (canonical, sole write destination):

`workspace/targets/{TICKER}_{PERIOD}/`
- `raw/`: Original PDFs, XBRL, Excel (`YYYYMMDD_source_doctype.pdf`) + regulatory enquiries (`YYYYMMDD_source_enquiry_<topic>.pdf`, trailing 24 months).
- `extracted/`: Domain-chunked data + `footnotes_focus/` + `_footnote_index.csv` + `evidence_inbox/` + `_bibliography.csv` + `_reconciliation_log.csv` + `_assumptions.csv` + `_peers.csv` + `fx_rates.csv` + `macro_brief.md` + `_events.csv` + `_esg_flags.csv`.
- `models/`: Python scripts, `run_log.jsonl` (+ `cost_log.csv`), `MODEL_MAP.md`, `.xlsx` models, `charts/`, `position_table.csv`.
- `pipeline-state.json`: Idempotency state machine incl. `run_mode` / `restatement_policy` / `discount_currency` / `valuation_engine` / `segments` / `enquiry` / `skeptic round` / `unresolved` / `risk_penalty` / `webhook` (SUCCESS skips, FAILED fixes then reruns).

Shared: `workspace/params/{cn,hk,us}.yaml` (market adapters incl. `rf_anchor`/`erp`/`crp`/discount rules + `fx_conversion_timing: T0_spot`) + `valuation_routing.yaml` (GICS/SW engine dispatcher incl. conglomerate probe) + `risk_penalty_matrix.yaml` (Unresolved→valuation/position haircuts), `workspace/peer_benchmarks/` (peer library + `sw_hs_gics_mapping.csv`), `workspace/shared_filing_cache/` (rate-limited source cache, batch-first hit), `workspace/targets/_TEMPLATE/` (scaffolding), final reports in `workspace/reports/`, HITL sign-offs + `webhook_payload.json` in `workspace/reviews/`.

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
> v1.6.0: 问询函采集（近24个月问询函+回函+临时公告，与附注同级）· 资金池指纹过滤（`[TREASURY_POOL]`+反伪装升级）· 期初债务计息破循环引用 · 困境兜底（清算/Net-Net/EV-Sales）+ `(WACC−g)≥1.5%` Clamp · 红队极化（空头CIO+KPI，反阿谀）。
> v1.7.0: 合议审判（举证标准+法官`Dismiss without Merit`防误杀）· 问询函脱水（15%~20%+跨页表格缝合）· ADR/双重股权归一化（比率链硬化）· 流水-三表三角勾稽（穿透表外保理）· 令牌桶流控+共享公告缓存。

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
