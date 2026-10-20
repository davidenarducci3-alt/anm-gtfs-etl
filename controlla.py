import pandas as pd


def leggi(nome):
    return pd.read_csv(f"dati/{nome}.txt", dtype=str)


agency = leggi("agency")
routes = leggi("routes")
trips = leggi("trips")
stops = leggi("stops")
stop_times = leggi("stop_times")
cal = leggi("calendar_dates")

print("DUPLICATI SULLE CHIAVI PRIMARIE")
print("routes.route_id:", routes["route_id"].duplicated().sum())
print("trips.trip_id:", trips["trip_id"].duplicated().sum())
print("stops.stop_id:", stops["stop_id"].duplicated().sum())
print("stop_times (trip_id, stop_sequence):",
      stop_times.duplicated(["trip_id", "stop_sequence"]).sum())

print("\nCHIAVI ESTERNE SENZA CORRISPONDENZA")
print("routes.agency_id non in agency:",
      (~routes["agency_id"].isin(agency["agency_id"])).sum())
print("trips.route_id non in routes:",
      (~trips["route_id"].isin(routes["route_id"])).sum())
print("trips.service_id non in calendar_dates:",
      (~trips["service_id"].isin(cal["service_id"])).sum())
print("stop_times.trip_id non in trips:",
      (~stop_times["trip_id"].isin(trips["trip_id"])).sum())
print("stop_times.stop_id non in stops:",
      (~stop_times["stop_id"].isin(stops["stop_id"])).sum())

print("\nRANGE DATE calendar_dates:", cal["date"].min(), "->", cal["date"].max())

print("\nTIPI DI LINEA (route_type):")
print(routes["route_type"].value_counts().to_string())

print("\nORARI >= 24:00 in stop_times:",
      (stop_times["arrival_time"].str[:2].astype(int) >= 24).sum())
