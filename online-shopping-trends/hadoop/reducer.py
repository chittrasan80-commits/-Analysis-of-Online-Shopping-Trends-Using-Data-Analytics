#!/usr/bin/env python3
"""Hadoop Streaming reducer: Recency, Frequency, Monetary per customer.
Set REF_DATE (YYYY-MM-DD) in the environment."""
import sys, os
from datetime import date
ref = date.fromisoformat(os.environ.get("REF_DATE", "2011-12-10"))
cur, invs, last, money = None, set(), None, 0.0
def flush():
    if cur is not None:
        print(f"{cur}\t{(ref-last).days}\t{len(invs)}\t{money:.2f}")
for line in sys.stdin:
    cid, val = line.rstrip("\n").split("\t")
    inv, d, amt = val.split(",")
    if cid != cur:
        flush(); cur, invs, last, money = cid, set(), None, 0.0
    d = date.fromisoformat(d)
    last = d if last is None or d > last else last
    invs.add(inv); money += float(amt)
flush()
