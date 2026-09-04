# Peer Benchmarks

公共可比公司库，按行业分目录：

```text
workspace/peer_benchmarks/{INDUSTRY}/peers.csv
```

字段: `ticker,name,revenue,ebitda_margin,mktcap,source,asof`。
目标快照每次复制到 `workspace/targets/{TICKER}_{PERIOD}/extracted/_peers.csv` 并记录 `peer_screen_log.csv` (IQR 剔除留痕)。
