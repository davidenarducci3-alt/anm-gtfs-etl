import logging

import pandas as pd

log = logging.getLogger(__name__)

TIPI_LINEA = {"0": "Tram", "1": "Metropolitana", "2": "Treno", "3": "Bus", "7": "Funicolare"}

LAT_MIN, LAT_MAX = 40.0, 41.5
LON_MIN, LON_MAX = 13.5, 15.0


def orario_in_secondi(serie: pd.Series) -> pd.Series:
    """Converte 'HH:MM:SS' (anche oltre le 24:00) in secondi dalla mezzanotte."""
    parti = serie.str.strip().str.split(":", expand=True).astype(int)
    return parti[0] * 3600 + parti[1] * 60 + parti[2]


def transform_agency(df):
    return df[["agency_id", "agency_name", "agency_url"]].copy()


def transform_routes(df):
    out = df[["route_id", "agency_id", "route_short_name", "route_type"]].copy()
    out["tipo_linea"] = out["route_type"].map(TIPI_LINEA).fillna("Altro")
    out["route_type"] = out["route_type"].astype(int)
    return out


def transform_trips(df):
    out = df[["trip_id", "route_id", "service_id", "direction_id", "wheelchair_accessible"]].copy()
    out["direction_id"] = pd.to_numeric(out["direction_id"]).astype("Int64")
    out["wheelchair_accessible"] = pd.to_numeric(out["wheelchair_accessible"]).astype("Int64")
    return out


def transform_stops(df):
    out = df[["stop_id", "stop_name", "stop_lat", "stop_lon"]].copy()
    out["stop_name"] = out["stop_name"].str.strip()
    out["stop_lat"] = pd.to_numeric(out["stop_lat"], errors="coerce")
    out["stop_lon"] = pd.to_numeric(out["stop_lon"], errors="coerce")
    valide = out["stop_lat"].between(LAT_MIN, LAT_MAX) & out["stop_lon"].between(LON_MIN, LON_MAX)
    scartate = int((~valide).sum())
    if scartate:
        log.warning("stops: %d fermate scartate per coordinate non valide", scartate)
    return out[valide]


def transform_stop_times(df):
    out = df[["trip_id", "stop_id", "stop_sequence", "arrival_time", "departure_time"]].copy()
    out["stop_sequence"] = out["stop_sequence"].astype(int)
    out["arrivo_sec"] = orario_in_secondi(out["arrival_time"])
    out["partenza_sec"] = orario_in_secondi(out["departure_time"])
    out["oltre_mezzanotte"] = (out["arrivo_sec"] >= 86400).astype(int)
    return out


def transform_calendar_dates(df):
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
    out["exception_type"] = out["exception_type"].astype(int)
    return out.rename(columns={"date": "data_servizio"})


def transform(grezzi: dict) -> dict:
    """Pulisce tutte le tabelle e restituisce un dizionario di DataFrame."""
    t = {
        "agency": transform_agency(grezzi["agency"]),
        "routes": transform_routes(grezzi["routes"]),
        "trips": transform_trips(grezzi["trips"]),
        "stops": transform_stops(grezzi["stops"]),
        "stop_times": transform_stop_times(grezzi["stop_times"]),
        "calendar_dates": transform_calendar_dates(grezzi["calendar_dates"]),
    }

    # Se qualche fermata e' stata scartata, togliamo anche i suoi orari
    prima = len(t["stop_times"])
    t["stop_times"] = t["stop_times"][t["stop_times"]["stop_id"].isin(t["stops"]["stop_id"])]
    scartati = prima - len(t["stop_times"])
    if scartati:
        log.warning("stop_times: %d righe scartate (fermata non valida)", scartati)

    return t
