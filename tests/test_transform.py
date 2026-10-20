import pandas as pd

from etl.transform import (
    orario_in_secondi,
    transform_calendar_dates,
    transform_routes,
    transform_stops,
)


def test_orario_normale():
    serie = pd.Series(["16:20:00", "00:00:05"])
    assert orario_in_secondi(serie).tolist() == [58800, 5]


def test_orario_oltre_mezzanotte():
    serie = pd.Series(["25:10:00"])
    assert orario_in_secondi(serie).tolist() == [90600]


def test_date_in_formato_iso():
    df = pd.DataFrame({"service_id": ["a"], "date": ["20231002"], "exception_type": ["1"]})
    out = transform_calendar_dates(df)
    assert out["data_servizio"].tolist() == ["2023-10-02"]
    assert out["exception_type"].tolist() == [1]


def test_tipo_linea_leggibile():
    df = pd.DataFrame({
        "route_id": ["1", "2", "3"],
        "agency_id": ["ANM"] * 3,
        "route_short_name": ["C16", "M1", "F1"],
        "route_type": ["3", "1", "7"],
    })
    out = transform_routes(df)
    assert out["tipo_linea"].tolist() == ["Bus", "Metropolitana", "Funicolare"]


def test_scarta_fermate_con_coordinate_non_valide():
    df = pd.DataFrame({
        "stop_id": ["1", "2"],
        "stop_name": [" VERGINI ", "FUORI"],
        "stop_lat": ["40.85", "0"],
        "stop_lon": ["14.25", "0"],
    })
    out = transform_stops(df)
    assert out["stop_id"].tolist() == ["1"]
    assert out["stop_name"].tolist() == ["VERGINI"]
