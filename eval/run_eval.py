#!/usr/bin/env python3
"""Golden 回归跑批骨架 (v1.9.0, stdlib only).
Reads eval/golden_benchmark.yaml (minimal subset parser), replays each case via
the audit command in batch-autonomous mode, scores verdicts, enforces gates.
NOTE: case execution is orchestrated by the agent runtime (opencode run audit);
this script aggregates `workspace/targets/<T>_<P>/pipeline-state.json` verdicts.
Usage: python3 eval/run_eval.py --suite eval/golden_benchmark.yaml
"""
import argparse
import csv
import json
import pathlib
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--suite", default="eval/golden_benchmark.yaml")
ap.add_argument("--workspace", default="workspace/targets")
ap.add_argument("--out", default="eval/last_eval_report.json")
args = ap.parse_args()

text = pathlib.Path(args.suite).read_text(encoding="utf-8")
gates = {"recall_min": 0.92, "false_alarm_max": 0.08}
m = re.search(r"recall_min:\s*([\d.]+)", text)
if m:
    gates["recall_min"] = float(m.group(1))
m = re.search(r"false_alarm_max:\s*([\d.]+)", text)
if m:
    gates["false_alarm_max"] = float(m.group(1))

cases = []
for line in text.splitlines():
    mm = re.match(r"\s*-\s*\{([^}]*)\}", line)
    if not mm:
        continue
    # normalize: re groups -> (quoted, bare)
    row = {}
    for k, q, b in re.findall(r"(\w+):\s*(?:\"([^\"]*)\"|([^,}]+))", mm.group(1)):
        row[k] = (q if q else b.strip())
    if "ticker" in row and "label" in row:
        cases.append(row)

def verdict_of(ticker, period):
    p = pathlib.Path(args.workspace) / f"{ticker}_{period}" / "pipeline-state.json"
    if not p.exists():
        return "MISSING"
    st = json.loads(p.read_text(encoding="utf-8"))
    un = st.get("unresolved_discrepancies", []) or []
    rp = st.get("risk_penalty", {}) or {}
    if un or rp.get("tier"):
        return "fraud"
    return "clean"

tp = fp = fn = tn = missing = 0
rows = []
for c in cases:
    v = verdict_of(c["ticker"], c.get("period", ""))
    rows.append({**c, "verdict": v})
    if v == "MISSING":
        missing += 1
    elif c["label"] == "fraud" and v == "fraud":
        tp += 1
    elif c["label"] == "fraud":
        fn += 1
    elif v == "fraud":
        fp += 1
    else:
        tn += 1

recall = tp / (tp + fn) if (tp + fn) else 0.0
far = fp / (fp + tn) if (fp + tn) else 0.0
report = {"gates": gates, "recall": round(recall, 4), "false_alarm": round(far, 4),
          "tp": tp, "fn": fn, "fp": fp, "tn": tn, "missing": missing,
          "pass": recall >= gates["recall_min"] and far <= gates["false_alarm_max"] and missing == 0,
          "rows": rows}
pathlib.Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: report[k] for k in ("recall", "false_alarm", "pass", "missing")}, ensure_ascii=False))
sys.exit(0 if report["pass"] else 1)
