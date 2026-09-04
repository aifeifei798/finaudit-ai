# Agents Guide - FinAudit AI (v1.8.0 全栈)

## Agents & Skills (19 agents, T1/T2/T3 分级；排雷归 fraud-screener，流水取证归 black-account-checker)
| 层 | Agent | Skills | Tier |
|---|---|---|---|
| L0 | `orchestrator` (Primary, default) | multi-doc-reasoning, citation-engine, market-adapter | T2 |
| L0 | `ticker-resolver` | financial-research, market-adapter | T1 |
| L0 | `gate-keeper` | multi-doc-reasoning, adversarial-skeptic | T2 |
| L1 | `filing-collector` | financial-research, market-adapter | T1 |
| L1 | `financial-researcher` | financial-research, financial-parser | T1 |
| L1 | `evidence-locker` | evidence-locker, citation-engine | T1 |
| L2 | `fraud-screener` (主链排雷，定量+附注定性) | quantitative-fraud-metrics, governance-redflags, market-adapter | T2 |
| L2 | `black-account-checker` (Primary, 流水取证旁路) | pii-sanitizer, black-account-checker | T2 |
| L2 | `financial-analyst` (Pre-Valuation 发起) | multi-doc-reasoning | T2 |
| L2 | `industry-peer-analyst` | peer-comparison, macro-context, esg-redflag, market-adapter | T2 |
| L2 | `sentiment-event-analyst` (旁路) | sentiment-event | T1 |
| L3 | `valuation-expert` (Dispatcher选引擎定价) | valuation-modeling, market-adapter | T2 |
| L3 | `scenario-sensitivity-analyst` | valuation-modeling | T2 |
| L3 | `portfolio-strategist` | portfolio-construction, macro-context | T2 |
| L4 | `adversarial-skeptic` | adversarial-skeptic | T2 |
| L4 | `compliance-checker` (只判不写) | professional-reporting (措辞半) | T3 异构 |
| L4 | `judge-qa` (只判不写) | citation-engine, evidence-locker | T3 异构 |
| L5 | `report-writer` | professional-reporting, citation-engine | T2 |
| L5 | `visualization-excel` | excel-export, chart-visualization | T1 |

- 模型分级见 `.opencode/model-tiers.json` (T1 抽取小模型 / T2 推理大模型 / T3 异构裁判)；`task_type→tier` 由 orchestrator 硬路由；T1 低置信 cascade 到 T2；调用记 `model_id/prompt_hash/token/cost` 入 `run_log.jsonl`。
- 20 skills = 19 + 1 new (`pii-sanitizer-skill`，Step0 强制前置 black-account)。
- 职责切分：`fraud-screener` 只做上市公司排雷（`extracted/` + `footnotes_focus/` 定性联动，不碰私有流水），进 `audit/report` 主链；`black-account-checker` 只做私有流水取证（先本地 PII 脱敏，LLM 只读 sanitized 副本），默认旁路。

## v1.4.0 演进（对应 5 维度断层修复）
1. **估值Dispatcher**：`workspace/params/valuation_routing.yaml` 按 GICS/申万路由（金融PB-ROE/DDM、REITs FFO/NAV、周期mid-cycle、未盈利rNPV/EV-Sales），禁强算 FCFF；SBC/租赁双列调整。
2. **附注通道**：`financial-parser` 建 `footnotes_focus/` + `_footnote_index.csv`；T2/L4 读原文聚焦窗口（Selective Bypass），仍禁读 raw 全文。
3. **PII合规**：`pii-sanitizer-skill/sanitize.py` 本地正则掩码（卡号/证件/手机/姓名→假名），vault 不出域。
4. **工程治理**：`run_mode` 双模式（institutional 阻塞签收 / batch-autonomous 评分放行+Warning）；Challenge Log max 2 轮熔断转 Unresolved 披露 + 反馈路由表；evidence inbox 队列 + 文件锁 + 原子提交；门禁决议写 `webhook_payload.json` 异步推送。
5. **PIT/FX**：`restatement_policy`（实时 as-restated / 回测 as-reported + vintage）；跨币种铁律（Rf 跟经营币种 + CRP + discount_currency 披露）。

## v1.5.0 演进（第二阶深水区补丁）
1. **Haircut联动**：`params/risk_penalty_matrix.yaml`——Unresolved 按档惩罚（核心会计 g-50bps/WACC+100bps/仓位≤2%，治理 g-30bps/WACC+50bps/≤3%，其余 ≤5%），judge-qa 四者一致性校验。
2. **PII加盐映射**：`sanitize.py` 每任务随机 Salt + HMAC（`--vault-in` 跨期复用不断链），vault 0600，报告前渲染合规代号后 `--destroy-vault`。
3. **SOTP调度**：ticker-resolver 输出 `is_conglomerate/segments[]`，Dispatcher 拆 2–3 分部独立挂引擎（EV/NBV、PB-ROE、PS、NAV、FFO），models/ 加总 + 控股折价。
4. **附注追溯**：Cross-Reference Resolver（参见附注X→Expansion Fetching，最多 2 跳，悬空记 Gap）。
5. **FX时点铁律**：经营本币折现 → T=0 即期单点转上市币种（`FX: <pair> <rate> @T=0`），禁逐年主观汇率预测。

## v1.6.0 演进（第三阶极端工况防御）
1. **问询函采集**：`regulatory_enquiry_collector`（近24个月问询函+回函+临时公告），与 footnotes 同级进聚焦窗口；无覆盖禁称“监管无质疑”。
2. **资金池过滤**：Step0b `treasury_pattern_recognizer`（摘要+时间+对冲三重指纹，≥2 打标 `[TREASURY_POOL]` 不计恶意，附录披露；反伪装升级 High）。
3. **循环引用**：`excel-export` 期初债务计息（`Interest=rate×Debt_{t-1}`），公式依赖图自环重写。
4. **困境兜底**：`distressed_fallback`（BV<0/连亏/债无价→清算/Net-Net/EV-Sales，禁 DCF/PB-ROE）+ `(WACC−g)≥1.5%` Clamp。
5. **红队极化**：空头 CIO 角色 + KPI（≥3 致命缺陷/打压 30%），无反证的认可判 sycophancy 打回。

## v1.7.0 演进（第四阶工业化硬化）
1. **合议审判**：skeptic 指控须持可测量违背证据；judge-qa 可 `Dismiss without Merit`（结案、不进 Unresolved、不触发惩罚矩阵），防极化误杀好标的致系统性空仓。
2. **问询函脱水**：Enquiry De-hydrator（剔律所套话保留 15%~20% + `dehydrate_log.csv`）+ Cross-Page Table Stitcher（表头继承/列对齐/`STITCH_WARN`）。
3. **ADR归一化**：ticker-resolver 输出 `adr_ratio/dual_class_weights`；`Target(ADR)=(EV−NetDebt)/Shares×Ratio×FX@T=0`，比率链断裂 judge-qa fail。
4. **三角勾稽**：流水-三表矩阵（大存大贷/预付异象/流量-规模背离），流水漂亮亦可推翻标红。
5. **流控缓存**：Token-Bucket（EDGAR≤8 req/s+合规UA，CNINFO/HKEX jitter+退避）+ `shared_filing_cache/` 强制命中，403 即停保 IP。

## v1.8.0 演进（第五阶买方实战壁垒）
1. **电话会指引**：`transcript-collector`（最新季度 Earnings Call 全文+NDR）+ `guidance-extractor`（`_guidance.csv`），模型偏离官方指引 > 15% 挂 `Guidance-Divergence` 警告。
2. **一致预期差**：`consensus-benchmarker-skill`（`_consensus.csv`→`consensus_delta.csv`），终稿回答 Alpha 来源；无覆盖写 N/A 并降 conviction。
3. **信用交叉**：`credit_cross_asset_probe`（`_credit.csv`，spread > 800bps 打 `CREDIT_DISTRESS`，去杠杆+剥夺抄底权限）。
4. **血统图**：`models/lineage_manifest.json`（关键数值的 `derived_from` 因果链），report-writer 渲染附录，judge-qa 抽查。
5. **摄取抽象层**：`params/ingestion.yaml` 双驱动（DirectScraper / InstitutionalTerminal），输出契约不变。

## Workspace (Canonical v1.8.0)
- `workspace/targets/{TICKER}_{PERIOD}/`: 独立沙盒 (唯一写入目标)。
  - `raw/`、`extracted/` (领域分块 + `footnotes_focus/` + `_footnote_index.csv` + `evidence_inbox/` + `_bibliography.csv` + `_reconciliation_log.csv` + `_assumptions.csv` + `_peers.csv` + `fx_rates.csv` + `macro_brief.md` + `_events.csv` + `_esg_flags.csv`)、`models/` (`run_log.jsonl` + `MODEL_MAP.md` + `.xlsx` + `charts/` + `position_table.csv`)、`pipeline-state.json` (含 run_mode/restatement_policy/discount_currency/valuation_engine/segments/skeptic round/unresolved/risk_penalty/webhook)。
- `workspace/targets/_TEMPLATE/`：脚手架；`workspace/params/{cn,hk,us}.yaml` (rf_anchor/erp/crp/discount规则) + `valuation_routing.yaml`；`workspace/peer_benchmarks/`：peer 库 + `sw_hs_gics_mapping.csv`；`workspace/reports/`：终稿；`workspace/reviews/`：双签收 + `webhook_payload.json`。
- Legacy 扁平 `workspace/raw|extracted|models/`：只读兼容。

## Guardrails (增量 v1.4.0)
1–7 见 v1.1.0 (重述优先 / Unit-FX / Python-first / 合规措辞 / 领域分块 / 沙盒 / 幂等)。
8. **证据与推理分离**：T2 读 extracted + footnotes_focus 原文窗口，禁读 raw PDF 全文；Parser 只转录不结论。
9. **计算与语言分离**：数字结论 Python-first + `[Calc #run_id]`；渲染层只读 `*_chart_data.csv`；金融/REITs/未盈利禁 FCFF-DCF。
10. **乐观执行悲观质检**：sentiment/macro/esg 旁路失败不阻塞；终稿必须 compliance pass + judge pass；skeptic 超 2 轮转 Unresolved 披露放行。
11. **PII 不出域**：未脱敏流水禁入任何 LLM；vault/映射不出域、不进 prompt/日志。

## HITL Gates (gate-keeper 唯一签收；batch-autonomous 可降级)
- **Pre-Valuation**：analyst 发起 → institutional 需 gate-keeper 签 `*_prevaluation.md` + `analyst_gate: APPROVED`；batch-autonomous 记 `AUTO_PASSED_WITH_WARNINGS` 继续。
- **Pre-Publication**：skeptic Log 全关（或 Unresolved 已披露签收）+ compliance pass + judge pass → gate-keeper 写 `skeptic: SIGNED_OFF`，report-writer 方可 FINAL；决议同步 `webhook_payload.json`。

## Infrastructure & Tooling
- **Config**: `opencode.json` (19 agent) + `.opencode/model-tiers.json` (T1/T2/T3)。
- **Safety**: hook 拦截 rm-rf/dd/fork/curl-wget/curl|sh/python网络/env泄漏/git-force；只读自动放行。
- **Env**: `BLACK_ACCOUNT_AUDIT=1`, `AUDIT_MODE=strict`, `FINANCIAL_AUDIT_MODE=strict`。
- **Commands**: `screen/collect` (L0-L1) / `audit/dcf/report` (主链，排雷=T2 fraud-screener，估值=Dispatcher) / `black-account` (流水取证旁路=Primary black-account-checker，Step0 PII脱敏) / `qa` (L4)，均 `.json`+`.md` 双入口；`report` 为 19-agent 全闭环（主链18 + 流水旁路1按需）；`--mode=batch-autonomous` 用于批量初筛/回测。
