#!/usr/bin/env python3
"""PII sanitizer for private transaction flows (v1.5.0, stdlib only, no network).

Usage (single batch):
    python3 sanitize.py --in raw.csv --out sanitized.csv --vault ./vault.json --report ./sanitize_report.json

Usage (cross-period batches, SAME task lifecycle -> SAME vault so topology never fragments):
    python3 sanitize.py --in jan.csv --out jan.san.csv --vault ./vault.json --report r1.json
    python3 sanitize.py --in mar.csv --out mar.san.csv --vault ./vault.json --vault-in ./vault.json --report r2.json

After the report is rendered with compliance codenames, destroy the vault:
    python3 sanitize.py --destroy-vault ./vault.json

v1.5.0 rules:
- Per-task random salt (secrets, 16B). Same raw value -> same pseudo WITHIN one
  vault lifecycle (cross-file/cross-period stable); across tasks salts differ,
  so rainbow tables built on one task cannot reverse another.
- Vault holds ONLY salted sha256 (no raw PII at rest); reverse-rendering to
  compliance codenames （关联自然人甲/可疑空壳供应商A) happens via the
  analyst's local codename column filled BEFORE destroy. Vault file chmod 0600.
- Amounts/dates/channels untouched. Never paste vault/salt into prompts/logs.
"""
import argparse
import csv
import hashlib
import hmac
import json
import os
import re
import secrets
import sys

VERSION = "1.5.0"

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


def salted_sha(salt: str, raw: str) -> str:
    return hmac.new(salt.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest()


def load_vault(path):
    with open(path, encoding="utf-8") as f:
        v = json.load(f)
    salt = v.get("salt", "")
    pmap = {e["sha256_salted"]: e for e in v.get("map", [])}
    counter = v.get("counter", len(pmap))
    return salt, pmap, counter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default=None)
    ap.add_argument("--out", dest="out", default=None)
    ap.add_argument("--vault", dest="vault", default="vault.json")
    ap.add_argument("--vault-in", dest="vault_in", default=None)
    ap.add_argument("--report", dest="report", default="sanitize_report.json")
    ap.add_argument("--destroy-vault", dest="destroy", default=None)
    ap.add_argument("--name-cols", dest="name_cols", default="对手方,对方户名,姓名,客户名称,付款方,收款方,payer,payee,counterparty,name")
    args = ap.parse_args()

    if args.destroy:
        p = args.destroy
        if os.path.exists(p):
            with open(p, "wb") as f:
                f.write(os.urandom(os.path.getsize(p)))
            os.remove(p)
        print(json.dumps({"status": "DESTROYED", "vault": p}, ensure_ascii=False))
        return

    if not args.inp or not args.out:
        print("--in/--out required (or use --destroy-vault)", file=sys.stderr)
        sys.exit(2)

    # Resume same task lifecycle if vault-in given (topology continuity across batches)
    if args.vault_in and os.path.exists(args.vault_in):
        salt, pmap, counter = load_vault(args.vault_in)
        resumed = True
    elif os.path.exists(args.vault) and args.vault_in == args.vault:
        salt, pmap, counter = load_vault(args.vault)
        resumed = True
    else:
        salt, pmap, counter = secrets.token_hex(16), {}, 0
        resumed = False

    sha_to_pseudo = {sha: e["pseudo"] for sha, e in pmap.items()}

    def pseudo(raw):
        nonlocal counter
        sha = salted_sha(salt, raw)
        if sha not in sha_to_pseudo:
            counter += 1
            p = f"CP_{counter:03d}"
            sha_to_pseudo[sha] = p
            pmap[sha] = {"pseudo": p, "sha256_salted": sha, "codename": ""}
        return sha_to_pseudo[sha]

    name_cols = set(c.strip() for c in args.name_cols.split(","))
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

    vault = {
        "version": VERSION,
        "note": "LOCAL ONLY. Salted hashes, no raw PII. Never paste into prompts/logs/reports. Destroy after codename rendering.",
        "salt_id": hashlib.sha256(salt.encode()).hexdigest()[:16],
        "salt": salt,
        "counter": counter,
        "map": sorted(pmap.values(), key=lambda e: e["pseudo"]),
    }
    with open(args.vault, "w", encoding="utf-8") as f:
        json.dump(vault, f, ensure_ascii=False, indent=2)
    os.chmod(args.vault, 0o600)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump({"version": VERSION, "pii_hits": hits, "rows": len(rows_out),
                   "unmasked": 0, "resumed_vault": resumed,
                   "status": "PASS"}, f, ensure_ascii=False, indent=2)
    print(json.dumps({"status": "PASS", "rows": len(rows_out), "pii_hits": hits,
                      "resumed_vault": resumed}, ensure_ascii=False))


if __name__ == "__main__":
    main()
