# Analysis of Online Shopping Trends Using Data Analytics
CCS334 Big Data Analytics mini project — E-commerce customer segmentation (RFM + K-Means) on the UCI Online Retail dataset. Supports **SDG 8** (Decent Work & Economic Growth).

## What it does
1. **Cleans** transactions (removes cancellations, guest checkouts, bad prices/quantities)
2. **Trend analysis**: monthly revenue, hour-of-day and weekday patterns, top products, top countries
3. **RFM via SQL** (`sql/rfm.sql`) — Recency, Frequency, Monetary per customer
4. **Big Data layer**: the same RFM as a Hadoop Streaming **MapReduce** job (`hadoop/`) and a **Hive** query (`hadoop/rfm_hive.hql`)
5. **K-Means segmentation** (k picked by silhouette score) -> Champions / Potential loyalists / Lapsed, with revenue share per segment

## Run it
```bash
pip install -r requirements.txt
python data/generate_sample.py      # synthetic data, same schema (default)
# python data/download_real.py      # OR real UCI data -> data/online_retail.csv (auto-preferred)
python src/analysis.py              # charts + CSVs + summary in output/
./run_hadoop_local.sh               # MapReduce RFM (map | sort | reduce) -> output/rfm_mapreduce.tsv
```
On GitHub: push the repo, open **Actions -> Run analysis**; results are uploaded as the `results` artifact.

## On a real Hadoop cluster
```bash
hdfs dfs -put data/online_retail.csv /user/hive/online_retail/
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files hadoop/mapper.py,hadoop/reducer.py -mapper mapper.py -reducer reducer.py \
  -input /user/hive/online_retail -output /user/out/rfm
hive -f hadoop/rfm_hive.hql
```

## Structure
`data/` datasets & generators · `sql/` RFM query · `hadoop/` MapReduce + Hive · `src/analysis.py` pipeline · `output/` results · `.github/workflows/run.yml` CI

## Tools
Python, pandas, scikit-learn, matplotlib, SQL (SQLite/Hive), Hadoop Streaming. Power BI: import `output/customer_segments.csv`.

> Note: the bundled sample is synthetic so the repo runs anywhere; run `download_real.py` and re-run for your real results before submitting.
