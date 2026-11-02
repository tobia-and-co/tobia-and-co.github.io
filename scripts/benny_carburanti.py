"""Benny il Benzinaio: scarica ogni mattina dal Ministero (Osservaprezzi carburanti) anagrafica e prezzi
di tutti i distributori e li divide per provincia in data/carburanti/<PROV>.json."""
import csv, io, json, math, pathlib, re, sys, unicodedata, urllib.request, datetime

BASI = ["https://www.mimit.gov.it/images/exportCSV/", "https://mimit.gov.it/images/exportCSV/", "https://www.mise.gov.it/images/exportCSV/"]
UA = {"User-Agent": "Mozilla/5.0 (Tobia & Co.; tobia-and-co.github.io)"}
OUT = pathlib.Path("data/carburanti"); OUT.mkdir(parents=True, exist_ok=True)

def leggi(nome):
    import time
    for tentativo in range(2):
        for base in BASI:
            try:
                return urllib.request.urlopen(urllib.request.Request(base + nome, headers=UA), timeout=60).read().decode("utf-8", "replace")
            except Exception as e:
                print("non raggiungibile:", base + nome, e)
        time.sleep(20)
    sys.exit(2)

def scarica(nome):
    testo = leggi(nome)
    righe = testo.splitlines()
    estrazione = righe[0]
    sep = "|" if righe[1].count("|") > righe[1].count(";") else ";"
    return estrazione, list(csv.reader(io.StringIO("\n".join(righe[1:])), delimiter=sep, quotechar='"'))

estr_a, anagrafica = scarica("anagrafica_impianti_attivi.csv")
estr_p, prezzi = scarica("prezzo_alle_8.csv")
print(estr_a, "|", estr_p, "|", len(anagrafica), "impianti,", len(prezzi), "prezzi")
print("intestazioni:", anagrafica[0], prezzi[0])

def num(s):
    try: return float(str(s).replace(",", "."))
    except ValueError: return None

# carburante: chiave breve -> parole del nome ufficiale
TIPI = {"B": "benzina", "D": "gasolio", "G": "gpl", "M": "metano"}
oggi = datetime.date.today()
P = {}
for r in prezzi[1:]:
    if len(r) < 5: continue
    idi, desc, prezzo, self_, data = r[0].strip(), r[1].strip().lower(), num(r[2]), r[3].strip(), r[4].strip()
    tipo = next((k for k, v in TIPI.items() if desc == v), None)
    if not tipo or not prezzo or not (0.3 < prezzo < 5): continue
    try:
        d = datetime.datetime.strptime(data[:10], "%d/%m/%Y").date()
        if (oggi - d).days > 8: continue          # prezzi vecchi: scartati
    except ValueError:
        pass
    s = self_ == "1"
    vecchio = P.setdefault(idi, {}).get(tipo)
    if vecchio is None or (s and not vecchio[1]) or (s == vecchio[1] and prezzo < vecchio[0]):
        P[idi][tipo] = (round(prezzo, 3), s)

province, comuni = {}, {}
for r in anagrafica[1:]:
    if len(r) < 10: continue
    idi = r[0].strip()
    lat, lon = num(r[8]), num(r[9])
    if idi not in P or not lat or not lon or not (35 < lat < 48 and 6 < lon < 19): continue
    prov = r[7].strip().upper() or "XX"
    marchio = r[2].strip() or "Pompe bianche"
    nome = r[4].strip().title()
    voce = [idi, marchio, nome, r[5].strip().title(), r[6].strip().title(), round(lat, 5), round(lon, 5),
            {k: [v[0], 1 if v[1] else 0] for k, v in P[idi].items()}]
    province.setdefault(prov, []).append(voce)
    c = comuni.setdefault((r[6].strip().title(), prov), [0, 0, 0]); c[0] += lat; c[1] += lon; c[2] += 1

indice = []
for prov, lista in province.items():
    json.dump({"aggiornato": estr_p, "impianti": lista}, open(OUT / f"{prov}.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    la = sum(v[5] for v in lista) / len(lista); lo = sum(v[6] for v in lista) / len(lista)
    indice.append([prov, round(la, 3), round(lo, 3), len(lista)])
elenco_comuni = sorted([[n, p, round(a / k, 4), round(b / k, 4), k] for (n, p), (a, b, k) in comuni.items()], key=lambda x: -x[4])
json.dump({"aggiornato": estr_p, "province": indice, "comuni": elenco_comuni},
          open(OUT / "indice.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
tot = sum(len(v) for v in province.values())
print(tot, "distributori con prezzi in", len(province), "province,", len(elenco_comuni), "comuni")
sys.exit(0 if tot > 5000 else 1)
