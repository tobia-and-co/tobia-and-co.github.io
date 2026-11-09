"""Benny: prezzi medi dei carburanti per regione (dai file data/carburanti/<PROV>.json), storico giornaliero
in data/carburanti/storico.json e pagina statica carburante/prezzi-medi/ (leggibile anche da motori e assistenti AI)."""
import datetime, html, json, pathlib, re, statistics

REGIONI = {
 "Abruzzo": "AQ CH PE TE", "Basilicata": "MT PZ", "Calabria": "CS CZ KR RC VV", "Campania": "AV BN CE NA SA",
 "Emilia-Romagna": "BO FC FE MO PC PR RA RE RN", "Friuli-Venezia Giulia": "GO PN TS UD", "Lazio": "FR LT RI RM VT",
 "Liguria": "GE IM SP SV", "Lombardia": "BG BS CO CR LC LO MB MI MN PV SO VA", "Marche": "AN AP FM MC PU", "Molise": "CB IS",
 "Piemonte": "AL AT BI CN NO TO VB VC", "Puglia": "BA BR BT FG LE TA", "Sardegna": "CA NU OR SS SU", "Sicilia": "AG CL CT EN ME PA RG SR TP",
 "Toscana": "AR FI GR LI LU MS PI PO PT SI", "Trentino-Alto Adige": "BZ TN", "Umbria": "PG TR", "Valle d'Aosta": "AO",
 "Veneto": "BL PD RO TV VE VI VR"}
PROV_REG = {p: r for r, ps in REGIONI.items() for p in ps.split()}
TIPI = {"B": "Benzina", "D": "Gasolio", "G": "GPL", "M": "Metano"}
UNITA = {"B": "€/l", "D": "€/l", "G": "€/l", "M": "€/kg"}
D = pathlib.Path("data/carburanti")
indice = json.load(open(D / "indice.json", encoding="utf-8"))
data = re.search(r"\d{4}-\d{2}-\d{2}", indice["aggiornato"]).group()

def media(valori):
    if not valori: return None
    med = statistics.median(valori)
    buoni = [v for v in valori if 0.8 * med < v < 1.2 * med]   # scarta i prezzi quasi certamente sbagliati
    return round(sum(buoni) / len(buoni), 3) if buoni else None

per = {r: {t: [] for t in TIPI} for r in REGIONI}; naz = {t: [] for t in TIPI}
for prov, *_ in indice["province"]:
    f = D / f"{prov}.json"
    if not f.exists(): continue
    for v in json.load(open(f, encoding="utf-8"))["impianti"]:
        for t, (prezzo, self_) in v[7].items():
            if t not in TIPI or (t in "BD" and not self_): continue   # benzina e gasolio: prezzo self service
            naz[t].append(prezzo)
            if prov in PROV_REG: per[PROV_REG[prov]][t].append(prezzo)
oggi = {"data": data, "italia": {t: media(naz[t]) for t in TIPI},
        "regioni": {r: {t: media(per[r][t]) for t in TIPI} for r in REGIONI},
        "distributori": {t: len(naz[t]) for t in TIPI}}

f_storico = D / "storico.json"
storico = json.load(open(f_storico, encoding="utf-8")) if f_storico.exists() else []
storico = [g for g in storico if g["data"] != data] + [oggi]
storico = sorted(storico, key=lambda g: g["data"])[-400:]
json.dump(storico, open(f_storico, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
json.dump(oggi, open(D / "medie.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- pagina statica ----
e = lambda s: html.escape(str(s), quote=True)
num = lambda x, d=3: ("–" if x is None else f"{x:.{d}f}".replace(".", ","))
def precedente(giorni):
    limite = (datetime.date.fromisoformat(data) - datetime.timedelta(days=giorni)).isoformat()
    vecchi = [g for g in storico if g["data"] <= limite]
    return vecchi[-1] if vecchi else None
ieri, sett = precedente(1), precedente(7)
def var(nuovo, g, chiave, t):
    if not g or nuovo is None: return ""
    vecchio = (g["italia"] if chiave is None else g["regioni"].get(chiave, {})).get(t)
    if vecchio is None: return ""
    d = round((nuovo - vecchio) * 1000) / 1000
    if abs(d) < 0.0005: return '<span class="note">=</span>'
    return f'<span class="{"extra" if d > 0 else "zero"}">{"▲" if d > 0 else "▼"} {num(abs(d))}</span>'
quando = datetime.date.fromisoformat(data).strftime("%d/%m/%Y")
righe_naz = "".join(f'<tr><td>{TIPI[t]}{" (self)" if t in "BD" else ""}</td><td class="prezzo">{num(oggi["italia"][t])} {UNITA[t]}</td><td>{var(oggi["italia"][t], ieri, None, t)}</td><td>{var(oggi["italia"][t], sett, None, t)}</td></tr>' for t in TIPI)
def tabella_reg(t):
    ordine = sorted((r for r in REGIONI if oggi["regioni"][r][t]), key=lambda r: oggi["regioni"][r][t])
    return "".join(f'<tr><td>{i + 1}. {e(r)}</td><td class="prezzo">{num(oggi["regioni"][r][t])}</td><td>{var(oggi["regioni"][r][t], sett, r, t)}</td></tr>' for i, r in enumerate(ordine)), ordine
rb, ob = tabella_reg("B"); rd, od = tabella_reg("D")
b, dd = oggi["italia"]["B"], oggi["italia"]["D"]
riassunto = (f"Il {quando} la benzina self costa in media {num(b)} €/l in Italia e il gasolio self {num(dd)} €/l. "
             f"La benzina è più economica in {ob[0]} ({num(oggi['regioni'][ob[0]]['B'])} €/l) e più cara in {ob[-1]} ({num(oggi['regioni'][ob[-1]]['B'])} €/l).")
ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Prezzi medi dei carburanti in Italia per regione",
      "description": "Media giornaliera dei prezzi self service di benzina e gasolio (e di GPL e metano) per regione, calcolata dai prezzi comunicati dai distributori al Ministero delle Imprese e del Made in Italy.",
      "url": "https://tobia-and-co.pages.dev/carburante/prezzi-medi/", "dateModified": data, "inLanguage": "it", "isAccessibleForFree": True,
      "creator": {"@type": "Organization", "name": "Tobia & Co.", "url": "https://tobia-and-co.pages.dev/"},
      "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": "https://tobia-and-co.pages.dev/data/carburanti/storico.json"}]}
pagina = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prezzo medio benzina e gasolio oggi, regione per regione ({quando}) | Tobia &amp; Co.</title>
<meta name="description" content="{e(riassunto)} Aggiornato ogni giorno con i dati ufficiali del Ministero.">
<link rel="canonical" href="https://tobia-and-co.pages.dev/carburante/prezzi-medi/">
<link rel="icon" href="../../img/tobia-base.svg">
<link rel="stylesheet" href="../../style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<div class="wrap">
  <header class="top"><img src="../../img/tobia-base.svg" alt=""><a href="../../">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="../../#strumenti">Strumenti</a><a class="nasc" href="../../diario/">Diario</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>
  <nav class="briciole"><a href="../../">🏠 Home</a> › <a href="../">Carburante</a> › Prezzi medi</nav>
  <span class="occhiello">Dati ufficiali · aggiornati ogni giorno</span>
  <h1>⛽ Prezzi medi di oggi, regione per regione</h1>
  <p class="lead">{e(riassunto)}</p>
  <div class="card">
    <h2 style="margin-top:0">🇮🇹 Media in Italia</h2>
    <table><tr><td></td><td class="prezzo">Oggi</td><td>da ieri</td><td>in 7 giorni</td></tr>{righe_naz}</table>
    <p class="note">Prezzi del {quando} (estrazione del Ministero), media su {str(format(oggi['distributori']['B'], ',')).replace(',', '.')} distributori per la benzina e {str(format(oggi['distributori']['D'], ',')).replace(',', '.')} per il gasolio. Benzina e gasolio: prezzo self service.</p>
  </div>
  <a class="btn blu" href="../">🗺️ Trova il distributore che ti conviene vicino a te ›</a>
  <div class="card" style="margin-top:20px"><h2 style="margin-top:0">⛽ Benzina self, dalla regione più economica</h2><table>{rb}</table></div>
  <div class="card"><h2 style="margin-top:0">🛢️ Gasolio self, dalla regione più economica</h2><table>{rd}</table></div>
  <div class="card">
    <h2 style="margin-top:0">ℹ️ Come calcolo le medie</h2>
    <p>Ogni mattina scarico i prezzi che i distributori comunicano al Ministero delle Imprese e del Made in Italy (Osservaprezzi carburanti) e faccio la media per regione, scartando i prezzi palesemente sbagliati (molto lontani da quelli della zona). La freccia rossa ▲ indica un aumento, la verde ▼ un calo.</p>
    <p class="note">Dati aperti: <a href="../../data/carburanti/storico.json">storico giornaliero in JSON</a>. Calcolo di Tobia, un'intelligenza artificiale (Claude): stima indicativa, non un dato ufficiale del Ministero.</p>
  </div>
  <footer><a href="../../">← Tutti gli strumenti</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ti è stato utile? Offri un caffè</a></footer>
</div>
<script src="../../js/conta.js" defer></script>
</body>
</html>
"""
out = pathlib.Path("carburante/prezzi-medi"); out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(pagina, encoding="utf-8")
print(riassunto)
