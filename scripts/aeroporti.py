"""Crea data/aeroporti.json dagli open data di OurAirports: solo aeroporti con voli di linea e codice IATA."""
import csv, json, sys, urllib.request, io
URL = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"
src = sys.argv[1] if len(sys.argv) > 1 else None
testo = open(src, encoding="utf-8").read() if src else urllib.request.urlopen(URL, timeout=120).read().decode("utf-8")
uscita = []
for r in csv.DictReader(io.StringIO(testo)):
    if r["scheduled_service"] != "yes" or not r["iata_code"] or r["type"] not in ("large_airport", "medium_airport", "small_airport"):
        continue
    uscita.append([r["iata_code"], r["name"], r["municipality"], r["iso_country"],
                   round(float(r["latitude_deg"]), 3), round(float(r["longitude_deg"]), 3),
                   {"large_airport": 3, "medium_airport": 2}.get(r["type"], 1)])
uscita.sort(key=lambda a: -a[6])
json.dump(uscita, open("data/aeroporti.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(uscita), "aeroporti")
