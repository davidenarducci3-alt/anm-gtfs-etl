import sqlite3


def test_nessuna_violazione_chiavi_esterne():
    conn = sqlite3.connect("anm.db")
    conn.execute("PRAGMA foreign_keys = ON")
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    conn.close()
