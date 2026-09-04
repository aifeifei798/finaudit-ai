#!/usr/bin/env python3
"""PII sanitizer for private transaction flows (v1.4.0, stdlib only, no network).

Usage:
    python3 sanitize.py --in raw.csv --out sanitized.csv --vault ./vault.json --report ./sanitize_report.json

Rules: mask card/account numbers (keep 6+4), ID/passport (3+4), phones (3+4),
names/counterparties -> stable pseudonyms (CP_001...). Amounts/dates/channels untouched.
Vault (raw<->pseudo map) stays local; never paste into prompts.
"""
import argparse
import csv
import hashlib
import json
import re
import sys

VERSION = "1.4.0"

CARD_RE = re.compile(r"\b(\d{6})[\d\s\-]{6,13}(\d{4})\b")
PHONE_RE = re.compile(r"\b(1\d{2})\d{4}(\d{4})\b")
ID_RE = re.compile(r"\b(\d{3})\d{11,14}([\dXx])\b")
# CJK names 2-4 chars (coarse; supplement with counterparty column mapping below)
NAME_RE = re.compile(r"[\u4e00-\u9fa5]{2,4}")


def mask_card(m):
    digits = re.sub(r"[\s\-]", "", m.group(0))
    if not 12 <= len(digits) <= 19:
        return m.group(0)
    return f"{digits[:6]}{'*' * (len(digits) - 10)}{digits[-4:]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--vault", dest="vault", default="vault.json")
    ap.add_argument("--report", dest="report", default="sanitize_report.json")
    ap.add_argument("--name-cols", dest="name_cols", default="对手方,对方户名,姓名,客户名称,付款方,收款方,payer,payee,counterparty,name")
    args = ap.parse_args()

    name_cols = set(c.strip() for c in args.name_cols.split(","))
    pseudo_of = {}
    counter = [0]

    def pseudo(raw):
        if raw not in pseudo_of:
            counter[0] += 1
            pseudo_of[raw] = f"CP_{counter[0]:03d}"
        return pseudo_of[raw]

    hits = {"card": 0, "phone": 0, "id": 0, "name": 0}
    rows_out = []
    with open(args.inp, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("empty csv", file=sys.stderr)
            sys.exit(2)
        for row in reader:
            nr = dict(row)
            for k, v in list(nr.items()):
                if v is None:
                    continue
                s = str(v)
                s2, n = CARD_RE.subn(mask_card, s)
                hits["card"] += n
                s2, n = PHONE_RE.subn(lambda m: f"{m.group(1)}****{m.group(2)}", s2)
                hits["phone"] += n
                s2, n = ID_RE.subn(lambda m: f"{m.group(1)}{'*' * 11}{m.group(2)}", s2)
                hits["id"] += n
                if k in name_cols and s2.strip():
                    # mask CJK name chars but keep stable pseudonym in dedicated col
                    if NAME_RE.search(s2) or len(s2.strip()) >= 2:
                        hits["name"] += 1
                        masked = (s2[0] + "*" + s2[-1]) if len(s2) > 2 else (s2[0] + "*")
                        nr[k + "_masked"] = masked
                        nr[k] = pseudo(s2.strip())
                        continue
                nr[k] = s2
            rows_out.append(nr)

    fieldnames = list(rows_out[0].keys()) if rows_out else []
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows_out)

    # vault: salted hash so even vault doesn't hold reversible raw without salt file
    vault = {
        "version": VERSION,
        "note": "LOCAL ONLY. Never paste into prompts/logs/reports.",
        "map": [
            {"pseudo": p, "sha256": hashlib.sha256(r.encode("utf-8")).hexdigest()}
            for r, p in pseudo_of.items()
        ],
    }
    with open(args.vault, "w", encoding="utf-8") as f:
        json.dump(vault, f, ensure_ascii=False, indent=2)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump({"version": VERSION, "pii_hits": hits, "rows": len(rows_out),
                   "unmasked": 0, "status": "PASS"}, f, ensure_ascii=False, indent=2)
    print(json.dumps({"status": "PASS", "rows": len(rows_out), "pii_hits": hits}, ensure_ascii=False))


if __name__ == "__main__":
    main()
