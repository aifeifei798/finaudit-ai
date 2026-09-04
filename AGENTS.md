# Agents Guide - FinAudit AI (v1.3.0 全栈)

## Agents & Skills (19 agents, T1/T2/T3 分级；排雷归 fraud-screener，流水取证归 black-account-checker)
| 层 | Agent | Skills | Tier |
|---|---|---|---|
| L0 | `orchestrator` (Primary, default) | multi-doc-reasoning, citation-engine, market-adapter | T2 |
| L0 | `ticker-resolver` | financial-research, market-adapter | T1 |
| L0 | `gate-keeper` | multi-doc-reasoning, adversarial-skeptic | T2 |
| L1 | `filing-collector` | financial-research, market-adapter | T1 |
| L1 | `financial-researcher` | financial-research, financial-parser | T1 |
| L1 | `evidence-locker` | evidence-locker, citation-engine | T1 |
| L2 | `fraud-screener` (主链排雷) | quantitative-fraud-metrics, governance-redflags, market-adapter | T2 |
| L2 | `black-account-checker` (Primary, 流水取证旁路) | black-account-checker | T2 |
| L2 | `financial-analyst` (Pre-Valuation 发起) | multi-doc-reasoning | T2 |
| L2 | `industry-peer-analyst` | peer-comparison, macro-context, esg-redflag, market-adapter | T2 |
| L2 | `sentiment-event-analyst` (旁路) | sentiment-event | T1 |
| L3 | `valuation-expert` (定价) | valuation-modeling, market-adapter | T2 |
| L3 | `scenario-sensitivity-analyst` | valuation-modeling | T2 |
| L3 | `portfolio-strategist` | portfolio-construction, macro-context | T2 |
| L4 | `adversarial-skeptic` | adversarial-skeptic | T2 |
| L4 | `compliance-checker` (只判不写) | professional-reporting (措辞半) | T3 异构 |
| L4 | `judge-qa` (只判不写) | citation-engine, evidence-locker | T3 异构 |
| L5 | `report-writer` | professional-reporting, citation-engine | T2 |
| L5 | `visualization-excel` | excel-export, chart-visualization | T1 |

- 模型分级见 `.opencode/model-tiers.json` (T1 抽取小模型 / T2 推理大模型 / T3 异构裁判)；`task_type→tier` 由 orchestrator 硬路由；T1 低置信 cascade 到 T2；调用记 `model_id/prompt_hash/token/cost` 入 `run_log.jsonl`。
- 19 skills = 12 keep + 7 new (`market-adapter`, `macro-context`, `sentiment-event`, `esg-redflag`, `portfolio-construction`, `chart-visualization`, `evidence-locker`)。
- 职责切分 (v1.3.0)：`fraud-screener` 只做上市公司排雷（输入`extracted/`，Python-first，不碰私有流水），进 `audit/report` 主链；`black-account-checker` 只做私有流水六步法取证（输入用户CSV/Excel），默认旁路，仅 `black-account` 命令或用户另附流水时调用。

## Workspace (Canonical v1.2.0)
- `workspace/targets/{TICKER}_{PERIOD}/`: 独立沙盒 (唯一写入目标)。
  - `raw/`、`extracted/` (领域分块 + `_bibliography.csv` + `_reconciliation_log.csv` + `_assumptions.csv` + `_peers.csv` + `fx_rates.csv` + `macro_brief.md` + `_events.csv` + `_esg_flags.csv`)、`models/` (`run_log.jsonl` + `MODEL_MAP.md` + `.xlsx` + `charts/` + `position_table.csv`)、`pipeline-state.json`。
- `workspace/targets/_TEMPLATE/`：脚手架；`workspace/params/{cn,hk,us}.yaml`：市场参数表；`workspace/peer_benchmarks/`：peer 库 + `sw_hs_gics_mapping.csv`；`workspace/reports/`：终稿；`workspace/reviews/`：双签收。
- Legacy 扁平 `workspace/raw|extracted|models/`：只读兼容。

## Guardrails (增量 v1.2.0)
1–7 见 v1.1.0 (重述优先 / Unit-FX / Python-first / 合规措辞 / 领域分块 / 沙盒 / 幂等)。
8. **证据与推理分离**：T2 禁读 raw PDF 全文，只读 extracted；Parser 只转录不结论。
9. **计算与语言分离**：数字结论 Python-first + `[Calc #run_id]`；渲染层只读 `*_chart_data.csv`。
10. **乐观执行悲观质检**：sentiment/macro/esg 旁路失败不阻塞；终稿必须 compliance pass + judge pass。

## HITL Gates (gate-keeper 唯一签收，严格版无旁路)
- **Pre-Valuation**：analyst 发起 → gate-keeper 签 `*_prevaluation.md` + `analyst_gate: APPROVED`。
- **Pre-Publication**：skeptic Log 全关 + compliance pass + judge pass → gate-keeper 写 `skeptic: SIGNED_OFF`，report-writer 方可 FINAL。

## Infrastructure & Tooling
- **Config**: `opencode.json` (19 agent) + `.opencode/model-tiers.json` (T1/T2/T3)。
- **Safety**: hook 拦截 rm-rf/dd/fork/curl-wget/curl|sh/python网络/env泄漏/git-force；只读自动放行。
- **Env**: `BLACK_ACCOUNT_AUDIT=1`, `AUDIT_MODE=strict`, `FINANCIAL_AUDIT_MODE=strict`。
- **Commands**: `screen/collect` (L0-L1) / `audit/dcf/report` (主链，排雷=T2 fraud-screener) / `black-account` (流水取证旁路=Primary black-account-checker) / `qa` (L4)，均 `.json`+`.md` 双入口；`report` 为 19-agent 全闭环（主链18 + 流水旁路1按需）。
