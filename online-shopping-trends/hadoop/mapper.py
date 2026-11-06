#!/usr/bin/env python3
"""Hadoop Streaming mapper: CSV line -> CustomerID <TAB> invoice,date,amount"""
import sys, csv
for r in csv.reader(sys.stdin):
    if not r or r[0] == "InvoiceNo": continue
    try:
        inv, qty, date, price, cid = r[0], int(r[3]), r[4], float(r[5]), r[6]
    except (ValueError, IndexError):
        continue
    if not cid or inv.startswith("C") or qty <= 0 or price <= 0: continue
    print(f"{cid.split('.')[0]}\t{inv},{date[:10]},{qty*price:.2f}")
