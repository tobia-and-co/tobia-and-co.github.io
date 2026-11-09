"""Benny: report mensile dei prezzi dei carburanti, scritto in automatico da data/carburanti/storico.json.
Per ogni mese COMPLETO (prima del mese UTC corrente) con almeno 5 giorni di dati crea carburante/report/<AAAA-MM>/index.html,
poi l'archivio carburante/report/index.html e l'elenco data/carburanti/report.json (usato dalla sitemap)."""
import datetime, html, json, pathlib

SITO = "https://tobia-and-co.pages.dev"
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
TIPI = {"B": "Benzina", "D": "Gasolio", "G": "GPL", "M": "Metano"}
UNITA = {"B": "€/l", "D": "€/l", "G": "€/l", "M": "€/kg"}
D = pathlib.Path("data/carburanti")
R = pathlib.Path("carburante/report")
e = lambda s: html.escape(str(s), quote=True)
num = lambda x, d=3: ("–" if x is None else f"{x:.{d}f}".replace(".", ","))
nome_mese = lambda ym: f"{MESI[int(ym[5:]) - 1]} {ym[:4]}"
dmy = lambda d: datetime.date.fromisoformat(d).strftime("%d/%m/%Y")
media = lambda v: (sum(v) / len(v)) if v else None

storico = json.load(open(D / "storico.json", encoding="utf-8")) if (D / "storico.json").exists() else []
mese_corrente = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m")
mesi = {}
for g in storico:
    mesi.setdefault(g["data"][:7], []).append(g)
completi = sorted(m for m, gg in mesi.items() if m < mese_corrente and len(gg) >= 5)

HEAD = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titolo} | Tobia &amp; Co.</title>
<meta name="description" content="{descr}">
<link rel="canonical" href="{canon}">
<link rel="icon" href="{up}img/tobia-base.svg">
<link rel="stylesheet" href="{up}style.css">
{extra}</head>
<body>
<div class="wrap">
  <header class="top"><img src="{up}img/tobia-base.svg" alt=""><a href="{up}">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="{up}#strumenti">Strumenti</a><a class="nasc" href="{up}diario/">Diario</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>
"""
FOOT = """  <footer><a href="{up}">← Tutti gli strumenti</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ti è stato utile? Offri un caffè</a></footer>
</div>
<script src="{up}js/conta.js" defer></script>
</body>
</html>
"""

def grafico(giorni, tipo, colore):
    """Piccolo grafico a linea in SVG (nessuna libreria): media giornaliera in Italia."""
    pts = [(g["data"], g["italia"].get(tipo)) for g in giorni if g["italia"].get(tipo) is not None]
    if len(pts) < 2: return ""
    W, H, L, Rr, T, B = 320, 150, 44, 10, 12, 24
    vals = [v for _, v in pts]; lo, hi = min(vals), max(vals)
    if hi - lo < 0.01: lo, hi = lo - 0.005, hi + 0.005
    pad = (hi - lo) * 0.1; lo -= pad; hi += pad
    n = len(pts)
    x = lambda i: L + (W - L - Rr) * i / (n - 1)
    y = lambda v: T + (H - T - B) * (hi - v) / (hi - lo)
    linea = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, (_, v) in enumerate(pts))
    guide = "".join(f'<line x1="{L}" x2="{W - Rr}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="gr-g"/><text x="{L - 5}" y="{y(v) + 4:.1f}" text-anchor="end" class="gr-t">{num(v)}</text>' for v in (lo + pad, (lo + hi) / 2, hi - pad))
    asse = (f'<text x="{L}" y="{H - 6}" class="gr-t">{pts[0][0][8:]}/{pts[0][0][5:7]}</text>'
            f'<text x="{W - Rr}" y="{H - 6}" text-anchor="end" class="gr-t">{pts[-1][0][8:]}/{pts[-1][0][5:7]}</text>')
    desc = f"Andamento giornaliero del prezzo medio di {TIPI[tipo].lower()} in Italia, da {num(pts[0][1])} a {num(pts[-1][1])} €/l"
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(desc)}" style="width:100%;height:auto;display:block">'
            f'{guide}{asse}<polyline points="{linea}" fill="none" stroke="{colore}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{x(n - 1):.1f}" cy="{y(pts[-1][1]):.1f}" r="3.5" fill="{colore}"/></svg>')

def pagina_mese(ym, giorni):
    giorni = sorted(giorni, key=lambda g: g["data"])
    ms = nome_mese(ym)
    # medie, minimi e massimi dell'Italia
    st = {}
    for t in TIPI:
        serie = [(g["data"], g["italia"].get(t)) for g in giorni if g["italia"].get(t) is not None]
        if not serie: continue
        vals = [v for _, v in serie]
        mn = min(serie, key=lambda s: s[1]); mx = max(serie, key=lambda s: s[1])
        primo, ultimo = serie[0], serie[-1]
        st[t] = dict(media=media(vals), mn=mn, mx=mx, primo=primo, ultimo=ultimo,
                     cent=(ultimo[1] - primo[1]) * 100, perc=(ultimo[1] - primo[1]) / primo[1] * 100)
    if "B" not in st or "D" not in st: return None
    regioni = sorted({r for g in giorni for r in g["regioni"]})
    rm = {t: {r: media([g["regioni"][r][t] for g in giorni if g["regioni"].get(r, {}).get(t) is not None]) for r in regioni} for t in "BD"}
    ordine = {t: sorted((r for r in regioni if rm[t][r] is not None), key=lambda r: rm[t][r]) for t in "BD"}
    ng = len(giorni)
    def variaz(s, d):
        segno = "+" if s["cent"] > 0.05 else ("−" if s["cent"] < -0.05 else "")
        return f'{segno}{num(abs(s["cent"]), 1)} cent ({segno}{num(abs(s["perc"]), 2)}%)'
    def verbo(s):
        if abs(s["cent"]) < 0.05: return "è rimasto praticamente fermo"
        return ("è salito" if s["cent"] > 0 else "è sceso") + f' di {num(abs(s["cent"]), 1)} centesimi'
    b, d = st["B"], st["D"]
    ob, od = ordine["B"], ordine["D"]
    riassunto = (f"A {ms} la benzina self è costata in media {num(b['media'])} €/l in Italia e il gasolio self {num(d['media'])} €/l (media di {ng} giorni di rilevazione). "
                 f"Dal {dmy(b['primo'][0])} al {dmy(b['ultimo'][0])} il prezzo medio della benzina {verbo(b)} e quello del gasolio {verbo(d)}. "
                 f"La benzina è stata in media più economica in {ob[0]} ({num(rm['B'][ob[0]])} €/l) e più cara in {ob[-1]} ({num(rm['B'][ob[-1]])} €/l); "
                 f"per il gasolio la regione più economica è stata {od[0]} ({num(rm['D'][od[0]])} €/l) e la più cara {od[-1]} ({num(rm['D'][od[-1]])} €/l).")
    righe = "".join(
        f'<tr><td>{TIPI[t]}{" (self)" if t in "BD" else ""}<br><span class="note">min {num(s["mn"][1])} ({dmy(s["mn"][0])[:5]})<br>max {num(s["mx"][1])} ({dmy(s["mx"][0])[:5]})</span></td><td class="prezzo">{num(s["media"])} {UNITA[t]}</td>'
        f'<td><span class="{"extra" if s["cent"] > 0.05 else ("zero" if s["cent"] < -0.05 else "note")}">{variaz(s, d)}</span></td></tr>'
        for t, s in st.items())
    def classifica(t):
        n = len(ordine[t]); r = ""
        for i, nome in enumerate(ordine[t]):
            evid = i < 3 or i >= n - 3
            stile = ' style="background:var(--verde-soft)"' if i < 3 else (' style="background:var(--rosso-soft)"' if i >= n - 3 else "")
            r += f'<tr{stile}><td>{i + 1}. {"<b>" if evid else ""}{e(nome)}{"</b>" if evid else ""}</td><td class="prezzo">{num(rm[t][nome])}</td></tr>'
        return r
    tre = lambda t, lista: ", ".join(e(x) for x in lista)
    css = ("<style>.gr-g{stroke:var(--line);stroke-width:1}.gr-t{fill:var(--muted);font:10px Inter,system-ui,sans-serif}"
           ".rp td{padding:8px 4px;font-size:15px}.rp{width:100%}.rp-scroll{overflow-x:auto}</style>\n")
    canon = f"{SITO}/carburante/report/{ym}/"
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": f"Prezzi dei carburanti in Italia, {ms}",
          "description": f"Prezzi medi giornalieri di benzina, gasolio, GPL e metano in Italia e nelle regioni nel mese di {ms}, elaborati dai prezzi comunicati dai distributori al Ministero delle Imprese e del Made in Italy (MIMIT).",
          "url": canon, "temporalCoverage": f"{giorni[0]['data']}/{giorni[-1]['data']}", "dateModified": giorni[-1]["data"], "inLanguage": "it", "isAccessibleForFree": True,
          "creator": {"@type": "Organization", "name": "Tobia & Co.", "url": SITO + "/"},
          "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITO + "/data/carburanti/storico.json"}]}
    extra = css + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>\n"
    titolo = f"Report carburanti di {ms}: prezzi medi di benzina e gasolio"
    out = HEAD.format(titolo=e(titolo), descr=e(riassunto), canon=canon, up="../../../", extra=extra)
    out += f"""  <nav class="briciole"><a href="../../../">🏠 Home</a> › <a href="../../">Carburante</a> › <a href="../">Report</a> › {ms}</nav>
  <span class="occhiello">Report mensile · dati ufficiali MIMIT</span>
  <h1>📊 Report carburanti di {ms}</h1>
  <p class="lead">{e(riassunto)}</p>
  <div class="card">
    <h2 style="margin-top:0">🇮🇹 Italia, mese per mese</h2>
    <div class="rp-scroll"><table class="rp"><tr><td>Carburante, giorno più basso e più alto</td><td class="prezzo">Media del mese</td><td>Dal primo all'ultimo giorno</td></tr>{righe}</table></div>
    <p class="note">Medie dei prezzi giornalieri, {ng} giorni di rilevazione ({dmy(giorni[0]['data'])} – {dmy(giorni[-1]['data'])}). Benzina e gasolio: prezzo self service.</p>
  </div>
  <div class="card"><h2 style="margin-top:0">⛽ Andamento della benzina</h2>{grafico(giorni, 'B', 'var(--blu)')}<p class="note">Prezzo medio giornaliero in Italia, €/l.</p></div>
  <div class="card"><h2 style="margin-top:0">🛢️ Andamento del gasolio</h2>{grafico(giorni, 'D', 'var(--oro)')}<p class="note">Prezzo medio giornaliero in Italia, €/l.</p></div>
  <div class="card"><h2 style="margin-top:0">⛽ Benzina self per regione</h2>
    <p class="note">Media del mese, dalla più economica. In verde le 3 più economiche: {tre('B', ob[:3])}. In rosso le 3 più care: {tre('B', ob[-3:])}.</p>
    <table class="rp">{classifica('B')}</table></div>
  <div class="card"><h2 style="margin-top:0">🛢️ Gasolio self per regione</h2>
    <p class="note">Media del mese, dalla più economica. In verde le 3 più economiche: {tre('D', od[:3])}. In rosso le 3 più care: {tre('D', od[-3:])}.</p>
    <table class="rp">{classifica('D')}</table></div>
  <a class="btn blu" href="../../">🗺️ Dove conviene fare benzina oggi ›</a>
  <p><a href="../../prezzi-medi/">Prezzi medi di oggi, regione per regione ›</a> · <a href="../">Tutti i report mensili ›</a></p>
  <div class="card">
    <h2 style="margin-top:0">📎 Come citare questi dati</h2>
    <p>Puoi usare questi numeri, anche in articoli e servizi giornalistici, citando la fonte con un link a questa pagina:</p>
    <p><b>Fonte: Tobia &amp; Co., elaborazione su dati MIMIT (Osservaprezzi carburanti), report di {ms} — <a href="{canon}">{canon}</a></b></p>
    <p class="note">Dati aperti: <a href="../../../data/carburanti/storico.json">storico giornaliero in JSON</a>.</p>
  </div>
  <div class="card">
    <h2 style="margin-top:0">ℹ️ Fonte e metodo</h2>
    <p>Dati ufficiali del Ministero delle Imprese e del Made in Italy (MIMIT), elaborati da Tobia &amp; Co. Ogni giorno si fa la media dei prezzi comunicati dai distributori, scartando quelli palesemente sbagliati; il report è la media di quelle medie giornaliere. Il testo di riepilogo è scritto in automatico dai numeri.</p>
    <p class="note">Calcolo di Tobia, un'intelligenza artificiale (Claude): stima indicativa, non un dato ufficiale del Ministero.</p>
  </div>
""" + FOOT.format(up="../../../")
    return out, riassunto

def archivio(elenco):
    if elenco:
        voci = "".join(f'<li><a href="{ym}/">Report carburanti di {nome_mese(ym)}</a><br><span class="note">{e(rias)}</span></li>' for ym, rias in elenco)
        corpo = f'<div class="card"><ul style="padding-left:20px;margin:0">{voci}</ul></div>'
        lead = "Ogni primo del mese un riepilogo dei prezzi di benzina e gasolio del mese appena finito, scritto in automatico dai dati ufficiali."
    else:
        corpo = ('<div class="card"><p>Il primo report (<b>novembre 2026</b>) comparirà qui il <b>1° dicembre 2026</b>: lo scrivo in automatico appena il mese è finito.</p>'
                 '<p>Nel frattempo trovi i prezzi di oggi in <a href="../prezzi-medi/">Prezzi medi regione per regione</a>.</p></div>')
        lead = "Ogni primo del mese un riepilogo dei prezzi di benzina e gasolio del mese appena finito. Il primo arriva il 1° dicembre 2026."
    out = HEAD.format(titolo="Report mensili sui prezzi dei carburanti", descr=e(lead), canon=SITO + "/carburante/report/", up="../../../".replace("../../../", "../../"), extra="")
    out += f"""  <nav class="briciole"><a href="../../">🏠 Home</a> › <a href="../">Carburante</a> › Report</nav>
  <span class="occhiello">Dati ufficiali · un report al mese</span>
  <h1>📊 Report mensili sui carburanti</h1>
  <p class="lead">{e(lead)}</p>
  {corpo}
  <a class="btn blu" href="../">🗺️ Dove conviene fare benzina ›</a>
  <p><a href="../prezzi-medi/">Prezzi medi di oggi, regione per regione ›</a></p>
""" + FOOT.format(up="../../")
    return out

elenco = []
for ym in reversed(completi):
    r = pagina_mese(ym, mesi[ym])
    if not r: continue
    (R / ym).mkdir(parents=True, exist_ok=True)
    (R / ym / "index.html").write_text(r[0], encoding="utf-8")
    elenco.append((ym, r[1]))
R.mkdir(parents=True, exist_ok=True)
(R / "index.html").write_text(archivio(elenco), encoding="utf-8")
json.dump([f"carburante/report/{ym}/" for ym, _ in elenco], open(D / "report.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(elenco), "report mensili")
