"""Download the real UCI Online Retail dataset -> data/online_retail.csv
(needs internet; run on your own machine)."""
import io, zipfile, urllib.request, pandas as pd
URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(URL).read()))
name = [n for n in z.namelist() if n.endswith(".xlsx")][0]
df = pd.read_excel(z.open(name))
df.to_csv("data/online_retail.csv", index=False)
print("saved", len(df), "rows")
