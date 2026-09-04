---
name: macro-context-skill
description: "宏观简报 — 利率/汇率/PMI/行业政策快照，每目标只调一次。Use when 需要无风险利率、ERP、国别溢价、政策传导背景时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Macro Context Skill

低频调用、高复用。与主链解耦，失败记 Gap 不阻塞估值 (用默认 Rf/ERP 并降 confidence)。

## 输入输出
- 输入: `{market: cn|hk|us, period}`。
- 输出: `workspace/targets/{TICKER}_{PERIOD}/extracted/macro_brief.md`，含：10Y 国债收益率 (Rf, 注日期)、ERP 假设 (默认 4%–6%)、汇率 (BS 即期/CF 均值来源)、PMI/行业政策 3–5 条 (每条 FN)。
- 月度缓存：同 market+month 直接复用，不重复检索。

## 与估值衔接
`valuation-expert` 的 Rf/β/ERP 必须引用 `macro_brief.md` 的 FN，禁止拍脑袋。政策冲击只进 Bear 情景，不改 base。
