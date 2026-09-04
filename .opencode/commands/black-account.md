---
description: 启动查黑账审计流程（提供账户/流水/尽调资料，进行异常检测与风险核查）
agent: black-account-checker
---

请先加载 pii-sanitizer-skill 做 Step 0 本地脱敏（原始流水禁入 LLM，核验 sanitize_report PASS），再加载 black-account-checker skill 按调查六步法执行。用户输入：$ARGUMENTS
输入为用户提供的私有流水/尽调资料（CSV/Excel优先）；金额先归一绝对值+ISO 币种；禁止网络外发账户明文。
注意：本命令只做流水取证，不跑上市公司M-Score/治理红旗；如需上市公司排雷请用 `audit`（fraud-screener）。

### 必查项
- Step 0 PII 脱敏与核验（未 PASS 禁止进入六步法）
- 数据清洗与字段标准化
- 红线指标扫描（拆分/快进快出/循环/休眠激活/集中分散/高频小额/对手方黑名单）
- 关联网络构建
- 风险定级与报告输出

### 输出要求
- 每个发现标注置信度和证据链
- 原始数据行号可追溯
- 最终给出可执行的处置建议
