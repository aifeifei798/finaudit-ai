---
name: evidence-locker-skill
description: "证据柜 — 全链路旁路引证 cite(metric)→[doc:page:table]，文献表唯一写者。Use when 需要登记/核验任何引用时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Evidence Locker Skill

全链路旁路，所有 agent 共享。`_bibliography.csv` 唯一写者，避免多写冲突。

## API (约定)
- `cite(metric, value) → [FN-ID]`：登记 `fn_id,doc_title,doc_date,file_or_url,page_table,scale_currency,level_P/S/T,accessed,hash`。
- `verify(FN-ID) → pass/fail`：回查文件存在 + 页码合法 + scale 非空。
- 网页来源加 `accessed + archive/hash`；XBRL 加 `tag + contextRef + decimals`。

## 规则
- FN 全文顺序无跳号 (`max FN == 行数`)；同一来源复用同一 ID。
- 任何 agent 不得私自编号，先调 locker 登记。终稿前跑全量 `verify`，fail 阻断 FINAL。
