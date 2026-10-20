from pathlib import Path

import pandas as pd

DATI = Path("dati")
TABELLE = ["agency", "routes", "trips", "stops", "stop_times", "calendar_dates"]


def extract() -> dict:
    """Legge i file GTFS come testo e restituisce un DataFrame per tabella."""
    return {nome: pd.read_csv(DATI / f"{nome}.txt", dtype=str) for nome in TABELLE}
