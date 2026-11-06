"""Generate a synthetic dataset with the same schema as UCI Online Retail.
Used so the project runs anywhere (e.g. GitHub Actions) without a download.
For the real data run: python data/download_real.py
"""
import numpy as np, pandas as pd
rng = np.random.default_rng(42)
N_CUST = 2500
countries = ["United Kingdom"]*80 + ["Germany"]*5 + ["France"]*5 + ["EIRE"]*3 + ["Spain"]*2 + ["Netherlands"]*2 + ["India"]*3
products = [(f"P{1000+i}", f"PRODUCT {i}", round(float(rng.lognormal(1.0, 0.7)), 2)) for i in range(300)]

# three hidden behaviour groups so clustering has real structure
groups = rng.choice(["loyal", "regular", "lapsed"], N_CUST, p=[.15, .45, .40])
rows, inv = [], 536000
for cid in range(12000, 12000 + N_CUST):
    g = groups[cid - 12000]
    n_orders = {"loyal": rng.integers(10, 30), "regular": rng.integers(2, 8), "lapsed": rng.integers(1, 3)}[g]
    window = 365 if g != "lapsed" else 200
    country = str(rng.choice(countries))
    for _ in range(n_orders):
        day = int(rng.integers(0, window))
        if g != "lapsed" and rng.random() < 0.25:   # seasonality: Sep-Nov peak
            day = int(rng.integers(270, 335))
        date = pd.Timestamp("2010-12-01") + pd.Timedelta(days=day, hours=int(rng.integers(8, 20)),
                                                          minutes=int(rng.integers(0, 60)))
        inv += 1
        for _ in range(int(rng.integers(1, 9))):
            code, desc, price = products[int(rng.integers(0, len(products)))]
            qty = int(rng.integers(1, 12 if g != "loyal" else 30))
            rows.append([str(inv), code, desc, qty, date, price, cid, country])
df = pd.DataFrame(rows, columns=["InvoiceNo","StockCode","Description","Quantity","InvoiceDate","UnitPrice","CustomerID","Country"])
# dirty data like the real set: cancellations and guest checkouts
canc = df.sample(frac=0.02, random_state=1).copy()
canc["InvoiceNo"] = "C" + canc["InvoiceNo"]; canc["Quantity"] = -canc["Quantity"]
guest = df.sample(frac=0.05, random_state=2).copy(); guest["CustomerID"] = np.nan
df = pd.concat([df, canc, guest]).sort_values("InvoiceDate")
df.to_csv("data/online_retail_sample.csv", index=False)
print("rows:", len(df), "customers:", df.CustomerID.nunique())
