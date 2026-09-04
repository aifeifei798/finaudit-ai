---
name: market-adapter-skill
description: "市场适配 — A/H/US准则/货币/阈值/正则三参数表切换。Use when 需要按市场切换会计口径、FX来源、估值边界、欺诈词库时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.5.0"
---

# Market Adapter Skill

所有 skill 通过 `{market}` 参数切换行为，不写 if-else 硬编码。参数表见 `workspace/params/{cn,hk,us}.yaml`。

## 适配四张表
1. **准则映射 (gaap_map)**: 同一 metric 三准则字段映射。CAS↔HKFRS/IFRS↔US GAAP (如 政府补助/减值转回/ASC606 收入确认差异)，对账时必须注明口径。
2. **货币与 FX (fx)**: CNY(外管局中间价) / HKD(盯住 USD 7.75–7.85, HKMA) / USD(Fed H.10)。BS 即期 vs IS/CF 均值分离，写入 `fx_rates.csv`。
3. **跨币种折现铁律 (v1.4.0 新增，防 200–300bps 偏差)**: Rf 必须跟**现金流币种（经营币种）**绑定，而非上市币种；H股（人民币经营/港币上市）、ADR（人民币经营/美元上市）二选一并披露 `discount_currency`：(a) `operating`——经营币种折现后按即期转 EV；(b) `listing`——现金流先按远期/平价转上市币种再折。ERP = 基准市场 ERP + 国别风险溢价 CRP（Damodaran 表，写入 `_assumptions.csv`）；拿美债 Rf 折人民币现金流且无 CRP/汇率桥接即判错，阻断 SUCCESS。
4. **折算时点铁律 T=0 (v1.5.0 新增，防终值 FX 剪刀差 8–15%)**: 一律“折现后转换”——经营本币口径完成全部 FCF 预测与折现得 `EV(经营币种)`，在基准日 T=0 按**当期 Spot FX 单点**转上市币种目标价；严禁对未来每年现金流做主观汇率预测后逐年折算（中美/中港利差倒挂下会系统性高估港币/美元目标价）。`fx_rates.csv` 必须记录 `spot_asof + source`，目标价注明 `FX: <pair> <rate> @T=0`。
5. **估值边界 (bounds)**: 成熟/高增长-新兴/困境三档 WACC 与 g，见 `valuation-modeling-skill`；`market` 只决定默认档 (cn 默认成熟+政策溢价备注, hk 默认成熟+AH折价, us 默认成熟+UST 锚)。
6. **欺诈词库 (fraud_lexicon)**: A股 (关联占用/存贷双高/商誉)、港股 (老千股/供股/核数师辞任)、美股 (ASC606/期权费用/collective litigation) 分开维护。

## 附注切分正则 (分市场)
- CN: `五[、,，]\s*\d+` / `附注\d+`；HK: `Note\s*\d+` 中英双语；US: `Item\s*8|Note\s*\d+`。语言路由：中文附注优先中文强抽取，英文优先英文模型 (见 model-tiers)。

## 接口
输入 `{market: cn|hk|us, task}` → 输出所用参数表版本 + 阈值快照 (写入 `_assumptions.csv` 一行 `market_adapter: params/us.yaml@v1.1.0`)。
