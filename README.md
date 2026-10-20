# Pipeline ETL su dati GTFS di ANM Napoli

Pipeline in Python che estrae il feed GTFS dell'Azienda Napoletana Mobilità, lo pulisce
e lo carica in un database relazionale SQLite con chiavi primarie ed esterne verificate.
L'esecuzione è ripetibile (ricrea il database da zero) e la trasformazione è coperta da test.
Il documento `docs/requisiti_e_risultati.md` collega una domanda di business ai dati, alla regola
di calcolo, al risultato e ai limiti di interpretazione.

## Fonte dei dati

Dati aperti del Comune di Napoli (https://dati.comune.napoli.it): feed GTFS `google_transit.zip`
di ANM, con linee, fermate, corse e orari. Il feed copre le date di servizio dal 02/10/2023 al
31/12/2023, quindi fotografa un periodo passato e non gli orari attuali.
I dati non sono inclusi nel repository: va scaricato lo ZIP dal portale e decompresso nella cartella `dati/`.
Per la licenza dei dati fa fede la pagina del dataset sul portale.

## Pipeline

1. **Extract** (`etl/extract.py`): legge i file GTFS come testo, senza lasciare a pandas il compito di indovinare i tipi.
2. **Transform** (`etl/transform.py`): pulizia e conversioni.
3. **Load** (`etl/load.py`): ricrea lo schema in SQLite e carica le tabelle, poi esegue il controllo delle chiavi esterne.

## Qualità dei dati

Controlli fatti prima del caricamento: duplicati sulle chiavi primarie, chiavi esterne senza
corrispondenza, intervallo delle date. Il feed è risultato coerente (nessun duplicato, nessun record orfano).

Trasformazioni applicate:
- rimosse le colonne completamente vuote (`trip_headsign`, `stop_headsign`, `parent_station`, `wheelchair_boarding`) e `route_long_name` (mancante in 104 linee su 110);
- orari convertiti in secondi dalla mezzanotte, con un flag `oltre_mezzanotte`: il GTFS ammette orari oltre le 24:00 (6.127 nel feed) per le corse notturne;
- date convertite dal formato `20231002` a `2023-10-02`;
- aggiunta una colonna leggibile per il tipo di linea (Bus, Metropolitana, Funicolare);
- controllo sulle coordinate delle fermate.

## Schema del database

```
agency <- routes <- trips -> services <- calendar_dates
                     ^
               stop_times -> stops
```

La tabella `services` è stata introdotta per normalizzare: `service_id` si ripete su più date
in `calendar_dates`, quindi non può essere bersaglio di una chiave esterna.

Volumi: 110 linee (104 bus, 2 metropolitane, 4 funicolari), 15.726 corse definite, 2.357 fermate,
399.186 orari di passaggio, 54 servizi, 2.054 date di servizio.

## Esempi di risultati

Dettagli e regole di calcolo in `docs/requisiti_e_risultati.md`; le query sono in `queries.sql`.

- Linee con più corse programmate nel periodo (02/10-31/12/2023): ALIB (21.931), le metropolitane L2 (20.974) e L1 (19.523), poi quattro funicolari a pari merito (16.562 ciascuna).
- Contando solo le corse definite nel feed (senza i giorni di servizio) la classifica cambia: le funicolari escono dalle prime dieci. Per questo nel documento la regola di calcolo è definita esplicitamente.
- Fermata con più passaggi definiti nel feed: Piazzale Tecchio (1.381).
- Corse con passaggi dopo la mezzanotte: 226 bus e 18 della metropolitana.

## Come eseguirlo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# scaricare il feed GTFS e decomprimerlo nella cartella dati/
python main.py
python esegui_query.py
python -m pytest -v
```

I test su database richiedono di aver eseguito prima `python main.py`.

## Stack

Python 3, pandas, SQLite, pytest.
