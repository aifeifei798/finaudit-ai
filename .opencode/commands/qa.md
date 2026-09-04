---
description: 独立质检模式 — 合规审查 + 数字三方比对 + HITL校验
agent: judge-qa
---

针对 $ARGUMENTS 执行独立质检 (与 qa.json 同义)。

`compliance-checker` 查措辞 → `judge-qa` 三方比对 → `gate-keeper` 放行/阻断。fail 阻断 FINAL。
