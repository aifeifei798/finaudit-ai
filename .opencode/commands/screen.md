---
description: 目标筛查模式 — 代码消歧 + 公告采集 + peer初筛
agent: ticker-resolver
---

针对 $ARGUMENTS 执行目标筛查 (与 screen.json 同义)。

1. `ticker-resolver` 消歧并初始化 `workspace/targets/{TICKER}_{PERIOD}/`；2. `filing-collector` 下载 raw 并写文献初版。输出沙盒就绪报告。
