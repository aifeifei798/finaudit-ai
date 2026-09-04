---
name: sentiment-event-skill
description: "情绪事件流 — 业绩预告/减持/监管函事件日历，只做风险提示不进DCF。Use when 需要事件催化剂、预期差、卖方一致性时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.9.0"
---

# Sentiment Event Skill

噪声大、不可进 DCF，只能作风险提示。与主链解耦，失败不阻塞。

## 输出
- `workspace/targets/{TICKER}_{PERIOD}/extracted/_events.csv`：`date,event_type(预告/减持/问询函/诉讼/分红),source,fn_id,sentiment(-1~1,仅提示),impact(High/Med/Low)`。
- 事件日历按时间倒序，cutoff 后事项单独段落。

## Narrative Drift Tracker 叙事漂移追踪 (v1.9.0 新增，抓温水煮青蛙)
- **输入**: 沙盒初始化挂载 `history_trajectory.json`（过去 4 期电话会/MD&A 承诺快照：`period|claim|tone_strength|fulfilled_TF|FN-ID`)；无历史写 `Gap: no trajectory (first coverage)`，不编造基线。
- **ΔTone 规则**: 逐项比对本期 vs 前 4 期同一业务措辞强度；核心业务连续 2 期下调前瞻用词（稳固→扰动→不可抗力式滑坡）即强制标黄 `NARRATIVE_DRIFT`，并建 Promise-vs-Reality 台账（承诺履行率 < 60% 的管理层，未来指引可信度打 7 折进估值）。
- 单期“中性偏谨慎”在漂移视角下可提级为 High；漂移结论只进风险附录 + 终稿警示段，不直接改目标价（防情绪污染 DCF）。

## 红线
- 禁止用情绪分调整目标价；禁止用 Tertiary 单源定量；卖方一致预期仅引用 (注明家数/日期)，分歧 > 20% 必须披露。
