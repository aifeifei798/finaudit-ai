---
name: chart-visualization-skill
description: "图表渲染 — 只读chart_data渲染趋势/DCF桥/peer雷达，不重算。Use when 需要把模型输出转为图表包时。"
license: MIT
compatibility: opencode
metadata:
  author: "金融安全审计组"
  version: "1.1.0"
---

# Chart Visualization Skill

纯渲染层。只读 `models/*_chart_data.csv`，禁止重算、禁止改假设。

## 模板 (matplotlib/openpyxl)
- 趋势图 (营收/利润/OCF 三线)、DCF 桥 (EV waterfalls)、peer 雷达 (growth/margin/ROE/多重)、敏感性热力 (WACC×g)。
- 允许库：`matplotlib` (静态图) + `openpyxl` (Excel 内嵌图)。图注必须含数据源 FN + `chart_data.csv` 路径。

## 输出
`models/charts/` (png + xlsx 内嵌) + 图表清单回写报告。渲染失败不阻塞估值数字。
