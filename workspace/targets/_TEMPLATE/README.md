# Target Sandbox Template

Canonical layout (v1.1.0):

```text
workspace/targets/{TICKER}_{PERIOD}/
  raw/                        # 原始 PDF/XBRL/xlsx，命名 YYYYMMDD_source_doctype.pdf
  extracted/
    financial_statements/     # BS/IS/CF 结构化 CSV+JSON
    notes_debt/ notes_revenue/ related_parties/ management_discussion/ audit_opinion/
    fx_rates.csv
    _bibliography.csv         # FN 文献表 (citation-engine)
    _reconciliation_log.csv   # 重述对账 (multi-doc)
    _assumptions.csv
    _peers.csv
  models/                     # Python 脚本 + run_log.jsonl + MODEL_MAP.md + xlsx
  pipeline-state.json         # 幂等状态机 (见本目录示例)
```

Legacy `workspace/raw|extracted|models/` 只读兼容，新任务禁止写入。
Peer 公共库: `workspace/peer_benchmarks/{INDUSTRY}/peers.csv`。
签收: `workspace/reviews/{TICKER}_{PERIOD}_prevaluation.md` + `*_challenge_log.csv`。
