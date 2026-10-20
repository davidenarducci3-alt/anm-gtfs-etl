-- 1. Le 10 linee con più corse
SELECT r.route_short_name AS linea, r.tipo_linea, COUNT(*) AS corse
FROM trips t
JOIN routes r ON r.route_id = t.route_id
GROUP BY r.route_id, r.route_short_name, r.tipo_linea
ORDER BY corse DESC
LIMIT 10;

-- 2. Linee e corse per tipo di mezzo
SELECT r.tipo_linea, COUNT(DISTINCT r.route_id) AS linee, COUNT(t.trip_id) AS corse
FROM routes r
LEFT JOIN trips t ON t.route_id = r.route_id
GROUP BY r.tipo_linea
ORDER BY corse DESC;

-- 3. Le 10 fermate con più passaggi
SELECT s.stop_name AS fermata, COUNT(*) AS passaggi
FROM stop_times st
JOIN stops s ON s.stop_id = st.stop_id
GROUP BY s.stop_id, s.stop_name
ORDER BY passaggi DESC
LIMIT 10;

-- 4. Corse con almeno un passaggio dopo la mezzanotte, per tipo di mezzo
SELECT r.tipo_linea, COUNT(DISTINCT st.trip_id) AS corse_notturne
FROM stop_times st
JOIN trips t ON t.trip_id = st.trip_id
JOIN routes r ON r.route_id = t.route_id
WHERE st.oltre_mezzanotte = 1
GROUP BY r.tipo_linea
ORDER BY corse_notturne DESC;

-- 5. Verifica: valori di exception_type in calendar_dates
SELECT exception_type, COUNT(*) AS righe
FROM calendar_dates
GROUP BY exception_type;

-- 6. Le 10 linee con più corse programmate nel periodo
SELECT r.route_short_name AS linea, r.tipo_linea,
       COUNT(*) AS corse_programmate
FROM trips t
JOIN routes r ON r.route_id = t.route_id
JOIN calendar_dates c ON c.service_id = t.service_id
WHERE c.exception_type = 1
GROUP BY r.route_id, r.route_short_name, r.tipo_linea
ORDER BY corse_programmate DESC
LIMIT 10;
