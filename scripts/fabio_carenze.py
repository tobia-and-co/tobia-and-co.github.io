"""Fabio il Farmacista: scarica l'elenco ufficiale AIFA dei medicinali carenti e lo salva in data/carenze.json.
Il link al file si cerca ogni volta nella pagina AIFA (può cambiare). Se qualcosa va storto esce con errore
e NON tocca il file già presente."""
import csv, datetime, io, json, pathlib, re, sys, urllib.parse, urllib.request

PAGINA = "https://www.aifa.gov.it/farmaci-carenti"
# se nella pagina non si trova nessun link, si provano questi (da verificare se AIFA cambia sito)
RISERVA = ["https://www.aifa.gov.it/documents/20142/847339/Elenco_medicinali_carenti.csv",
           "https://www.aifa.gov.it/documents/20142/847339/Elenco_medicinali_carenti.xlsx"]
UA = "Mozilla/5.0 (Tobia & Co.; tobia-and-co.pages.dev)"
USCITA = pathlib.Path(__file__).resolve().parent.parent / "data" / "carenze.json"

# nome del campo -> parole che possono comparire nell'intestazione della colonna
CAMPI = [("nome", ["denominazione", "nome medicinale", "medicinale", "specialit", "nome"]),
         ("principio", ["principio attivo", "principio", "sostanza"]),
         ("confezione", ["confezione", "descrizione", "aic", "codice"]),
         ("titolare", ["titolare", "ditta", "azienda"]),
         ("inizio", ["data inizio", "inizio", "dal"]),
         ("fine", ["fine presunta", "presunta", "data fine", "fine", "ripresa"]),
         ("motivo", ["motivazion", "motivo", "causa", "ragion"]),
         ("suggerimenti", ["suggerimenti", "alternativ", "equivalent", "note"])]

def scarica(url):
    r = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(r, timeout=60) as x:
        return x.read(), x.headers.get("Content-Type", "")

def testo(b):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass

def trova_link(html):
    link = []
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html, re.I):
        u = urllib.parse.urljoin(PAGINA, m.group(1).replace("&amp;", "&"))
        if re.search(r"\.(csv|xlsx?)(\?|$)", u, re.I) and re.search(r"carent|carenz|shortage", urllib.parse.unquote(u), re.I):
            link.append(u)
    link.sort(key=lambda u: (not re.search(r"\.csv", u, re.I), "medicinal" not in u.lower()))   # meglio csv
    return link

COLONNE = []

def norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()

def mappa(intest):
    """Per ogni campo cerca la colonna con l'intestazione più somigliante."""
    h = [norm(x).lower() for x in intest]
    m, usate = {}, set()
    for campo, chiavi in CAMPI:
        for k in chiavi:
            i = next((i for i, c in enumerate(h) if k in c and i not in usate), None)
            if i is not None:
                m[campo] = i; usate.add(i); break
    return m

def righe_csv(b):
    t = testo(b)
    sep = max([";", ",", "\t"], key=lambda s: t[:3000].count(s))
    return list(csv.reader(io.StringIO(t), delimiter=sep))

def righe_xlsx(b):
    import openpyxl  # solo se il file è Excel
    ws = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True).active
    return [["" if c is None else (c.strftime("%d/%m/%Y") if hasattr(c, "strftime") else str(c)) for c in r] for r in ws.iter_rows(values_only=True)]

def data(s):
    s = norm(s)
    m = re.match(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    return m.group(0) if m else s

def estrai(righe):
    # l'intestazione è la prima riga con almeno 3 celle piene che somiglia a una intestazione
    for n, r in enumerate(righe[:15]):
        m = mappa(r)
        if "nome" in m and len(m) >= 3:
            break
    else:
        raise SystemExit("Non trovo l'intestazione delle colonne nel file AIFA")
    out = []
    global COLONNE
    COLONNE = [norm(x) for x in righe[n]]
    for r in righe[n + 1:]:
        if not any(norm(c) for c in r):
            continue
        v = {c: norm(r[i]) if i < len(r) else "" for c, i in m.items()}
        if not v.get("nome") and not v.get("principio"):
            continue
        for c in ("inizio", "fine"):
            if c in v:
                v[c] = data(v[c])
        out.append({c: v.get(c, "") for c, _ in CAMPI})
    return out

def main():
    try:
        html = testo(scarica(PAGINA)[0])
        urls = trova_link(html) or RISERVA
    except Exception as e:
        print("Pagina AIFA non raggiungibile:", e, file=sys.stderr)
        urls = RISERVA
    ultimo = None
    for u in urls:
        try:
            b, _ = scarica(u)
            righe = righe_xlsx(b) if re.search(r"\.xlsx?(\?|$)", u, re.I) else righe_csv(b)
            carenze = estrai(righe)
            if carenze:
                ultimo = (u, carenze); break
        except BaseException as e:
            print("Provato", u, "->", e, file=sys.stderr)
    if not ultimo:
        print("Nessun file AIFA scaricato: lascio il vecchio data/carenze.json", file=sys.stderr)
        sys.exit(1)
    u, carenze = ultimo
    nuovo = {"aggiornato": datetime.date.today().isoformat(), "fonte": u, "pagina": PAGINA, "colonne": COLONNE, "carenze": carenze}
    # non riscrivere se i dati sono uguali (evita commit inutili col solo cambio di data)
    try:
        vecchio = json.loads(USCITA.read_text(encoding="utf-8"))
        if vecchio.get("carenze") == carenze and vecchio.get("fonte") == u and vecchio.get("colonne") == COLONNE:
            print("Nessun cambiamento:", len(carenze), "righe"); return
    except Exception:
        pass
    USCITA.write_text(json.dumps(nuovo, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(carenze), "farmaci carenti salvati da", u)

if __name__ == "__main__":
    main()
