import sqlite3

import pandas as pd

with open("queries.sql", encoding="utf-8") as f:
    blocchi = [b.strip() for b in f.read().split(";") if b.strip()]

conn = sqlite3.connect("anm.db")
for blocco in blocchi:
    titolo = blocco.splitlines()[0].lstrip("- ").strip()
    print("\n" + "=" * 60)
    print(titolo)
    print(pd.read_sql_query(blocco, conn).to_string(index=False))
conn.close()
