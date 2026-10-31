"""Rita la Farmacista: scarica dal sito AIFA la lista di trasparenza dei farmaci equivalenti
e la trasforma in data/farmaci.json per la pagina "Il tuo farmaco costa meno?"."""
import csv, io, json, re, sys, urllib.request, urllib.parse, datetime

PAGINA = "https://www.aifa.gov.it/it/liste-dei-farmaci"
RISERVA = "https://www.aifa.gov.it/documents/20142/825643/Lista_farmaci_equivalenti.csv"
UA = {"User-Agent": "Mozilla/5.0 (Tobia & Co.; tobia-and-co.github.io)"}

def leggi(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()

url = RISERVA
try:
    html = leggi(PAGINA).decode("utf-8", "replace")
    for href in re.findall(r'href="([^"]+)"', html):
        if "lista_farmaci_equivalenti" in href.lower() and ".csv" in href.lower():
            url = urllib.parse.urljoin(PAGINA, href.replace("&amp;", "&")); break
except Exception as e:
    print("pagina AIFA non raggiungibile, uso il link di riserva:", e)

grezzo = leggi(url)
try:
    testo = grezzo.decode("utf-8")
except UnicodeDecodeError:
    testo = grezzo.decode("cp1252")
righe = list(csv.reader(io.StringIO(testo), delimiter=";"))
intest = [c.strip() for c in righe[0]]
col = {nome: i for i, nome in enumerate(intest)}
col_prezzo = next(i for i, c in enumerate(intest) if c.lower().startswith("prezzo pubblico"))
data_prezzi = intest[col_prezzo].replace("Prezzo Pubblico", "").strip()

def euro(s):
    s = re.sub(r"[^0-9,]", "", s or "").replace(",", ".")
    return round(float(s), 2) if s else None

gruppi = {}
for r in righe[1:]:
    if len(r) < len(intest):
        continue
    g = r[col["Codice gruppo equivalenza"]].strip()
    gr = gruppi.setdefault(g, {"p": r[col["Principio attivo"]].strip(),
                               "c": r[col["Confezione di riferimento"]].strip(),
                               "r": euro(r[col["Prezzo riferimento SSN"]]), "f": []})
    gr["f"].append([r[col["Farmaco"]].strip(), r[col["Confezione"]].replace('"', '').strip(),
                    r[col["Ditta"]].strip(), euro(r[col_prezzo]), euro(r[col["Differenza"]])])
for gr in gruppi.values():
    gr["f"].sort(key=lambda x: (x[3] is None, x[3]))

uscita = {"fonte": url, "prezzi_al": data_prezzi,
          "aggiornato": datetime.date.today().isoformat(), "gruppi": list(gruppi.values())}
with open("data/farmaci.json", "w", encoding="utf-8") as f:
    json.dump(uscita, f, ensure_ascii=False, separators=(",", ":"))
print(len(gruppi), "gruppi di farmaci equivalenti, prezzi al", data_prezzi)
sys.exit(0 if gruppi else 1)
