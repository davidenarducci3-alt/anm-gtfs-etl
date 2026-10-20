# Requisiti e risultati

Questo documento collega una domanda di business ai dati disponibili, alla regola di calcolo
usata, al risultato e ai limiti di interpretazione. Le query sono in `queries.sql`.

## RQ-01: quali linee registrano il maggior numero di corse nel periodo analizzato?

**Domanda aziendale**
Quali linee del servizio ANM hanno il maggior numero di corse nel periodo coperto dal feed?

**Dato necessario**
- identificativo e nome breve della linea (`routes`)
- corse della linea (`trips`)
- giorni in cui ogni corsa è attiva (`calendar_dates`, collegata a `trips` tramite `services`)
- periodo di riferimento: dal 02/10/2023 al 31/12/2023 (91 giorni)

**Regola di calcolo**
Una *corsa programmata* è una coppia (corsa, data di servizio) in cui il servizio della corsa
è attivo in quella data (`exception_type = 1`). Il valore di una linea è il numero di corse
programmate di tutte le sue corse nel periodo.
- ogni direzione di una linea è una corsa distinta;
- una corsa che supera la mezzanotte è conteggiata nella data di servizio di inizio;
- il feed non contiene sospensioni: tutte le 2.054 date hanno `exception_type = 1`.

```sql
SELECT r.route_short_name AS linea, r.tipo_linea,
       COUNT(*) AS corse_programmate
FROM trips t
JOIN routes r ON r.route_id = t.route_id
JOIN calendar_dates c ON c.service_id = t.service_id
WHERE c.exception_type = 1
GROUP BY r.route_id, r.route_short_name, r.tipo_linea
ORDER BY corse_programmate DESC
LIMIT 10;
```

**Risultato**

| Posizione | Linea | Tipo | Corse programmate |
|---|---|---|---|
| 1 | ALIB | Bus | 21.931 |
| 2 | L2 | Metropolitana | 20.974 |
| 3 | L1 | Metropolitana | 19.523 |
| 4-7 (pari merito) | F1, F2, F3, F4 | Funicolare | 16.562 ciascuna |
| 8 | 151 | Bus | 14.342 |
| 9 | R6 | Bus | 13.823 |
| 10 | NC | Bus | 13.666 |

Controllo di coerenza: le 4 funicolari hanno 728 corse definite nel feed (182 ciascuna).
Il periodo dura 91 giorni e 182 x 91 = 16.562, quindi le funicolari risultano attive tutti i giorni.

**Perché la regola conta.** Contare soltanto le corse definite nel feed (le righe di `trips`)
dà una classifica diversa: ALIB (723), L2 (650) e L1 (635) restano nelle prime tre posizioni,
ma le funicolari non compaiono tra le prime dieci (182 corse definite ciascuna) e compaiono invece
140, 169, R2 e C16, che non sono nelle prime dieci per corse programmate. La differenza
è che le corse definite non dicono in quanti giorni ogni corsa è attiva.

**Limiti**
- Il feed è un orario *programmato*: non registra le corse effettivamente svolte,
  né ritardi o soppressioni.
- Copre solo tre mesi del 2023: non rappresenta altri periodi dell'anno né gli orari attuali.
- Conta le corse, non la capacità, i passeggeri o la lunghezza del percorso:
  una corsa di funicolare e una di bus pesano allo stesso modo. Il risultato non è
  quindi una misura completa dell'offerta di servizio né un confronto tra tipi di mezzo.
- Il calendario è ricavato solo da `calendar_dates` (il feed non contiene `calendar.txt`).
- Il nome della linea è `route_short_name`: il nome esteso è mancante per 104 linee su 110.
