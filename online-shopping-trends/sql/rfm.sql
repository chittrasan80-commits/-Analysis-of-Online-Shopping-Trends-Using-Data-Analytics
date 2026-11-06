-- RFM per customer. Runs in SQLite (used by the Python pipeline); the Hive
-- equivalent is in hadoop/rfm_hive.hql.  :ref_date = day after last invoice.
SELECT
    CAST(CustomerID AS INTEGER)                                        AS CustomerID,
    CAST(julianday(:ref_date) - julianday(date(MAX(InvoiceDate))) AS INTEGER) AS Recency,
    COUNT(DISTINCT InvoiceNo)                                          AS Frequency,
    ROUND(SUM(Quantity * UnitPrice), 2)                                AS Monetary
FROM transactions
WHERE CustomerID IS NOT NULL
  AND InvoiceNo NOT LIKE 'C%'
  AND Quantity > 0 AND UnitPrice > 0
GROUP BY CustomerID;
