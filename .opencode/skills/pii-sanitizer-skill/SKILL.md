---
name: pii-sanitizer-skill
description: "PII脱敏 — 私有流水/尽调资料进入LLM前的本地强制脱敏（正则+轻量掩码，卡号/姓名/账户不出域）。Use when 处理银行流水、开户资料、交易对手含真实身份信息时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.4.0"
---

# PII Sanitizer Skill (v1.4.0, P0 合规强制)

`black-account-checker` 处理私有流水前的 **Step 0 强制关卡**。原始含 PII 文件**禁止**直接进入任何商用 LLM（T1/T2 亦然）；必须先本地脱敏，LLM 只见脱敏副本。

## 脱敏范围
- 卡号/账号（16–19位数字，含空格/连字符分隔）：保留前6后4，其余 `*`，如 `6222********1234`。
- 身份证/护照号：保留前3后4，其余 `*`。
- 手机号：保留前3后4（`138****1234`）。
- 姓名/对手方：`张*三`式掩码 + 稳定假名映射（`CP_001`），映射 vault 只存本地，永不随 prompt 外发。
- 金额/日期/渠道/交易类型**不脱敏**（分析必需），但禁止与明文账户拼成 URL 外发。

## 执行协议
1. **本地运行** `sanitize.py`（同目录，标准库 only，无网络）：`python3 sanitize.py --in raw.csv --out sanitized.csv --vault ./vault.json --report ./sanitize_report.json`。
2. 检查 `sanitize_report.json`：`pii_hits>0` 必须全掩码后才放行；`unmasked=0` 方可进入六步法。
3. LLM 输入一律用 `sanitized.csv`；证据索引引用脱敏行号 + 假名；原始文件路径写入 vault，不写入 prompt / 报告 / 日志。
4. 跨境红线：未经用户明确授权，脱敏/原始文件均不得传出境内执行环境；违规即阻断。

## 输出
- `sanitized.csv`（LLM 唯一可读输入）+ `vault.json`（本地映射，600权限）+ `sanitize_report.json`（命中计数/规则版本）。
