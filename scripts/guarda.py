import pandas as pd

FILES = ["agency", "routes", "trips", "stops", "stop_times", "calendar_dates"]

for nome in FILES:
    df = pd.read_csv(f"dati/{nome}.txt", dtype=str)
    print("=" * 60)
    print(nome, "->", df.shape[0], "righe,", df.shape[1], "colonne")
    print("Colonne:", list(df.columns))
    print(df.head(3).to_string())
    print("Valori mancanti per colonna:")
    mancanti = df.isna().sum()
    print(mancanti[mancanti > 0].to_string() if mancanti.sum() > 0 else "nessuno")
