---
name: sentiment-event-skill
description: "情绪事件流 — 业绩预告/减持/监管函事件日历，只做风险提示不进DCF。Use when 需要事件催化剂、预期差、卖方一致性时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Sentiment Event Skill

噪声大、不可进 DCF，只能作风险提示。与主链解耦，失败不阻塞。

## 输出
- `workspace/targets/{TICKER}_{PERIOD}/extracted/_events.csv`：`date,event_type(预告/减持/问询函/诉讼/分红),source,fn_id,sentiment(-1~1,仅提示),impact(High/Med/Low)`。
- 事件日历按时间倒序，cutoff 后事项单独段落。

## 红线
- 禁止用情绪分调整目标价；禁止用 Tertiary 单源定量；卖方一致预期仅引用 (注明家数/日期)，分歧 > 20% 必须披露。
