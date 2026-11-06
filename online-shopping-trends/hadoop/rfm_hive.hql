-- Hive version of the RFM query (run on a Hadoop/Hive cluster)
CREATE EXTERNAL TABLE IF NOT EXISTS transactions (
  InvoiceNo STRING, StockCode STRING, Description STRING, Quantity INT,
  InvoiceDate TIMESTAMP, UnitPrice DOUBLE, CustomerID STRING, Country STRING)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
STORED AS TEXTFILE LOCATION '/user/hive/online_retail'
TBLPROPERTIES ("skip.header.line.count"="1");

CREATE TABLE rfm AS
SELECT CustomerID,
       DATEDIFF('2011-12-10', MAX(InvoiceDate)) AS Recency,
       COUNT(DISTINCT InvoiceNo)                AS Frequency,
       ROUND(SUM(Quantity * UnitPrice), 2)      AS Monetary
FROM transactions
WHERE CustomerID IS NOT NULL AND CustomerID != ''
  AND InvoiceNo NOT LIKE 'C%' AND Quantity > 0 AND UnitPrice > 0
GROUP BY CustomerID;
