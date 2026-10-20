import logging
import sqlite3
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

DB_PATH = Path("anm.db")

DROP = """
DROP TABLE IF EXISTS stop_times;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS calendar_dates;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS agency;
"""

SCHEMA = """
CREATE TABLE agency (
    agency_id   TEXT PRIMARY KEY,
    agency_name TEXT NOT NULL,
    agency_url  TEXT
);

CREATE TABLE routes (
    route_id         TEXT PRIMARY KEY,
    agency_id        TEXT NOT NULL REFERENCES agency(agency_id),
    route_short_name TEXT NOT NULL,
    route_type       INTEGER NOT NULL,
    tipo_linea       TEXT NOT NULL
);

CREATE TABLE services (
    service_id TEXT PRIMARY KEY
);

CREATE TABLE calendar_dates (
    service_id     TEXT NOT NULL REFERENCES services(service_id),
    data_servizio  TEXT NOT NULL,
    exception_type INTEGER NOT NULL,
    PRIMARY KEY (service_id, data_servizio)
);

CREATE TABLE stops (
    stop_id   TEXT PRIMARY KEY,
    stop_name TEXT NOT NULL,
    stop_lat  REAL NOT NULL,
    stop_lon  REAL NOT NULL
);

CREATE TABLE trips (
    trip_id               TEXT PRIMARY KEY,
    route_id              TEXT NOT NULL REFERENCES routes(route_id),
    service_id            TEXT NOT NULL REFERENCES services(service_id),
    direction_id          INTEGER,
    wheelchair_accessible INTEGER
);

CREATE TABLE stop_times (
    trip_id          TEXT NOT NULL REFERENCES trips(trip_id),
    stop_sequence    INTEGER NOT NULL,
    stop_id          TEXT NOT NULL REFERENCES stops(stop_id),
    arrival_time     TEXT NOT NULL,
    departure_time   TEXT NOT NULL,
    arrivo_sec       INTEGER NOT NULL,
    partenza_sec     INTEGER NOT NULL,
    oltre_mezzanotte INTEGER NOT NULL CHECK (oltre_mezzanotte IN (0, 1)),
    PRIMARY KEY (trip_id, stop_sequence)
);

CREATE INDEX idx_trips_route ON trips(route_id);
CREATE INDEX idx_stop_times_stop ON stop_times(stop_id);
"""


def load(tabelle: dict, db_path: Path = DB_PATH) -> None:
    """Ricrea il database da zero e carica le tabelle pulite."""
    cal = tabelle["calendar_dates"]
    doppie = int(cal.duplicated(["service_id", "data_servizio"]).sum())
    if doppie:
        log.warning("calendar_dates: %d righe duplicate rimosse", doppie)
        cal = cal.drop_duplicates(["service_id", "data_servizio"])

    services = pd.DataFrame({"service_id": cal["service_id"].unique()})

    trips = tabelle["trips"].astype(object)
    trips = trips.where(trips.notna(), None)

    ordine = [
        ("agency", tabelle["agency"]),
        ("routes", tabelle["routes"]),
        ("services", services),
        ("calendar_dates", cal),
        ("stops", tabelle["stops"]),
        ("trips", trips),
        ("stop_times", tabelle["stop_times"]),
    ]

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(DROP + SCHEMA)
        for nome, df in ordine:
            df.to_sql(nome, conn, if_exists="append", index=False, chunksize=50_000)
            log.info("%s: %d righe caricate", nome, len(df))
        conn.commit()

        violazioni = conn.execute("PRAGMA foreign_key_check").fetchall()
        if violazioni:
            log.error("Violazioni di chiavi esterne: %d", len(violazioni))
        else:
            log.info("Controllo chiavi esterne: nessuna violazione")
    finally:
        conn.close()
