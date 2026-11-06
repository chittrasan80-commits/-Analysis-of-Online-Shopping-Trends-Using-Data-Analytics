#!/usr/bin/env bash
# Simulates Hadoop Streaming locally: map -> sort (shuffle) -> reduce.
# On a real cluster:  hadoop jar hadoop-streaming.jar -input ... -output ... -mapper mapper.py -reducer reducer.py
set -e
CSV=${1:-data/online_retail_sample.csv}
mkdir -p output
export REF_DATE=${REF_DATE:-$(python3 -c "import pandas as pd;d=pd.read_csv('$CSV',usecols=['InvoiceDate']).InvoiceDate.max();print((pd.Timestamp(d)+pd.Timedelta(days=1)).date())")}
echo -e "CustomerID\tRecency\tFrequency\tMonetary" > output/rfm_mapreduce.tsv
cat "$CSV" | python3 hadoop/mapper.py | sort -k1,1 | python3 hadoop/reducer.py >> output/rfm_mapreduce.tsv
echo "MapReduce RFM rows: $(($(wc -l < output/rfm_mapreduce.tsv)-1))"; head -4 output/rfm_mapreduce.tsv
