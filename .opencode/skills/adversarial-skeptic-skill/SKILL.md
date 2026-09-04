---
name: adversarial-skeptic-skill
description: "红队质询 — 做空视角压力测试、Challenge Log、预发布签收。Use when 需要证伪bull case、跑Revenue/WACC/DSO压力时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.4.0"
---

# Adversarial Skeptic Skill

This skill implements a "Devil's Advocate" or "Short-Seller" perspective to stress-test financial assumptions and identify hidden risks.

## The Skeptic's Mandate
Your goal is NOT to be balanced; your goal is to **disprove the bullish case**. Actively seek contradicting evidence. 找不到反例必须写 `Searched [scope], no counter-evidence found, confidence: Low`，禁止沉默通过。

## Stress Test Scenarios (必须量化进 DCF 敏感性)
1. **Revenue Shock**: Top-3 customer churn / growth → 0% / -10% 三档对 EV 冲击。
2. **Cost Spike**: 材料 +20% / 人力 +15% 对毛利率/FCF 冲击。
3. **Macro Shift**: WACC +200bps 对 DCF 冲击 (与 sensitivity 表联动)。
4. **Working Capital Strain**: DSO +15 天 / 存货 +30 天对现金缺口冲击。
5. **Key-man / Regulatory**: 实控人风险/行业政策一刀切情景 (至少 1 个定性转定量)。

## Red Flag Detection
- **Aggressive Accounting**: 折旧/收入/费用资本化政策突变。
- **Cash Flow Divergence**: Net Income ↑ 但 OCF 平/降 (与 Sloan/M-Score 联动)。
- **Management Over-Optimism**: guidance vs actual 历史兑现率 < 70% → 未来预测 haircut 20%–30% 并披露。

## Output Format: Challenge Log (v1.1.0 结构化)
| ID | Severity(Critical/High/Med) | Assumption | Skeptic's Challenge | Required Evidence | Owner | Status(Open/Resolved/Accepted/Rejected+理由) |
|---|---|---|---|---|---|---|
| C-01 | High | Revenue 15% CAGR | 饱和+竞品低价 | 近3年市占率 | analyst | Open |

- 每个 C-ID 必须有 FN 证据或 `Gap` 声明；Critical 未关闭禁止放行（institutional 模式；batch-autonomous 见熔断）。

## 反馈回路与熔断 (v1.4.0 新增，防“质询-微调”死循环)
- **路由表** (谁改): 估值假设类 → `valuation-expert` / `scenario-sensitivity-analyst`；对账口径类 → `financial-analyst`；证据缺失类 → `financial-researcher` + `evidence-locker`；措辞类 → `report-writer`（`compliance-checker` 只判不写）。
- **状态机**: `Open → Fixed(待复核) → Resolved / Accepted / Rejected with Justification`；复核仍不通过则 `round+1`。
- **熔断**: `skeptic_round` 上限 **2 轮**（记 `pipeline-state.json: {skeptic: {round}}`）。超限仍 Open 的 Critical/High 强制转 `Unresolved Discrepancy`，记入 `reviews/{TICKER}_{PERIOD}_challenge_log.csv` + 终稿醒目章节披露，不得永久卡死流程；institutional 模式仍需 gate-keeper 对 Unresolved 逐条签收，batch-autonomous 模式自动放行并标 Warning。

## HITL Gate: Pre-Publication (v1.1.0 落地)
All Challenge Log items must be signed off before report-writer finalizes. 存储: `workspace/reviews/{TICKER}_{PERIOD}_challenge_log.csv` + `pipeline-state.json: {skeptic: {status: SIGNED_OFF, by, at}}`。状态仅允许 `Resolved / Accepted / Rejected with Justification`；Rejected 必须配替代披露措辞 (audit-compliant)。
