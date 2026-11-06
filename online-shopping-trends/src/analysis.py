"""Analysis of Online Shopping Trends Using Data Analytics
clean -> trend analysis -> RFM (SQL) -> KMeans segmentation -> report."""
import os
import sqlite3
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

OUT = "output"; os.makedirs(OUT, exist_ok=True)
path = next(p for p in ["data/online_retail.csv", "data/online_retail_sample.csv"] if os.path.exists(p))
print("Using dataset:", path)

# 1. Load & clean
df = pd.read_csv(path, parse_dates=["InvoiceDate"])
raw = len(df)
df = df.dropna(subset=["Description"])  # no row-dedupe: repeated lines in one invoice are legitimate, and it keeps SQL = MapReduce
sales = df[(~df.InvoiceNo.astype(str).str.startswith("C")) & (df.Quantity > 0) & (df.UnitPrice > 0)].copy()
sales["Revenue"] = sales.Quantity * sales.UnitPrice
print(f"Rows: {raw} raw -> {len(sales)} valid sales")

# 2. Shopping trends
monthly = sales.set_index("InvoiceDate").Revenue.resample("MS").sum()
ax = monthly.plot(marker="o", figsize=(9, 4), title="Monthly revenue"); ax.set_ylabel("Revenue")
plt.tight_layout(); plt.savefig(f"{OUT}/monthly_revenue.png", dpi=120); plt.close()

by_hour = sales.groupby(sales.InvoiceDate.dt.hour).InvoiceNo.nunique()
by_dow = sales.groupby(sales.InvoiceDate.dt.day_name()).Revenue.sum().reindex(
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]).fillna(0)
fig, a = plt.subplots(1, 2, figsize=(11, 4))
by_hour.plot.bar(ax=a[0], title="Orders by hour of day"); by_dow.plot.bar(ax=a[1], title="Revenue by weekday")
plt.tight_layout(); plt.savefig(f"{OUT}/time_patterns.png", dpi=120); plt.close()

sales.groupby("Description").Revenue.sum().nlargest(10).sort_values().plot.barh(
    figsize=(8, 4), title="Top 10 products by revenue")
plt.tight_layout(); plt.savefig(f"{OUT}/top_products.png", dpi=120); plt.close()
top_countries = sales.groupby("Country").Revenue.sum().sort_values(ascending=False)

# 3. RFM using SQL
con = sqlite3.connect(":memory:")
df.assign(InvoiceDate=df.InvoiceDate.dt.strftime("%Y-%m-%d %H:%M:%S")).to_sql("transactions", con, index=False)
ref_date = (df.InvoiceDate.max() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
rfm = pd.read_sql(open("sql/rfm.sql").read(), con, params={"ref_date": ref_date})
print(f"RFM computed for {len(rfm)} customers (ref date {ref_date})")

# 4. KMeans segmentation
X = StandardScaler().fit_transform(np.log1p(rfm[["Recency", "Frequency", "Monetary"]].clip(lower=0)))
scores = {k: silhouette_score(X, KMeans(k, n_init=10, random_state=42).fit_predict(X)) for k in range(2, 7)}
best_k = max(scores, key=scores.get)
print("Silhouette by k:", {k: round(v, 3) for k, v in scores.items()}, "-> k =", best_k)
rfm["Cluster"] = KMeans(best_k, n_init=10, random_state=42).fit_predict(X)

prof = rfm.groupby("Cluster").agg(Customers=("CustomerID", "count"), Recency=("Recency", "mean"),
                                   Frequency=("Frequency", "mean"), Monetary=("Monetary", "mean")).round(1)
def name_segments(p):
    names = {}
    names[p.Monetary.idxmax()] = "Champions / Loyal"
    rest = p.drop(index=list(names))
    names[rest.Recency.idxmax()] = "Lapsed / At risk"
    for c in p.index:
        names.setdefault(c, "Potential loyalists")
    return pd.Series(names)
prof["Segment"] = name_segments(prof)
prof["RevenueShare%"] = (rfm.groupby("Cluster").Monetary.sum() / rfm.Monetary.sum() * 100).round(1)
rfm["Segment"] = rfm.Cluster.map(prof.Segment)
rfm.to_csv(f"{OUT}/customer_segments.csv", index=False)
prof.to_csv(f"{OUT}/segment_profile.csv")

plt.figure(figsize=(7, 5))
for c, g in rfm.groupby("Cluster"):
    plt.scatter(np.log1p(g.Frequency), np.log1p(g.Monetary), s=8, label=f"{c}: {prof.Segment[c]}")
plt.xlabel("log(Frequency)"); plt.ylabel("log(Monetary)"); plt.legend(); plt.title("Customer segments")
plt.tight_layout(); plt.savefig(f"{OUT}/segments.png", dpi=120); plt.close()

# 5. Report
with open(f"{OUT}/summary.md", "w") as f:
    f.write(f"# Results\n\n- Dataset: `{path}`\n- Valid sales rows: {len(sales):,}\n- Customers analysed: {len(rfm):,}\n")
    f.write(f"- Total revenue: {sales.Revenue.sum():,.0f}\n- Peak month: {monthly.idxmax():%b %Y}\n")
    f.write(f"- Top country: {top_countries.index[0]} ({top_countries.iloc[0]/top_countries.sum():.0%} of revenue)\n")
    f.write(f"- Best k (silhouette): {best_k}\n\n## Segment profile\n\n{prof.to_markdown()}\n")
print(open(f"{OUT}/summary.md").read())
