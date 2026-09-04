---
name: evidence-locker-skill
description: "证据柜 — 全链路旁路引证 cite(metric)→[doc:page:table]，文献表唯一写者。Use when 需要登记/核验任何引用时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.4.0"
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

## 并发写协议 (v1.4.0 新增，防多 Agent 并行覆写)
- **唯一写者 + 邮箱队列**: 并发 agent 不直写 `_bibliography.csv`，只向 `extracted/evidence_inbox/<agent>_<ts>.json` 投递 `{metric,value,doc_title,doc_date,file_or_url,page_table,scale_currency,level}`；locker 单线程 drain 队列后统一编号。
- **文件锁 + 原子提交**: drain 时建 `_bibliography.lock`（`fcntl.flock`，Windows 回退 `os.open(O_CREAT|O_EXCL)` 哨兵），读-改-写后 `os.replace(tmp, _bibliography.csv)` 原子提交；FN 号用文件内 `max+1` 原子分配，禁止内存计数器。
- **冲突处理**: 同一来源去重复用 ID；锁等待超 30s 记 `evidence: RETRY` 不覆写；坏包移入 `evidence_inbox/_dead_letter/` 并留痕。
