"""Rita la Farmacista, parte 2: da data/farmaci.json crea una pagina per ogni principio attivo
(farmaci/<nome>/index.html), la sitemap.xml e la lista degli indirizzi per IndexNow."""
import json, re, html, pathlib, shutil, unicodedata, datetime

SITO = "https://tobia-and-co.pages.dev"
d = json.load(open("data/farmaci.json", encoding="utf-8"))
oggi = datetime.date.today().isoformat()

def slug(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:80]

def eur(x):
    return "—" if x is None else f"{x:.2f}".replace(".", ",") + " €"

e = lambda s: html.escape(s, quote=True)

per_principio = {}
for g in d["gruppi"]:
    per_principio.setdefault(g["p"], []).append(g)

base = pathlib.Path("farmaci")
for vecchia in base.iterdir():
    if vecchia.is_dir():
        shutil.rmtree(vecchia)

indirizzi = [SITO + "/", SITO + "/scadenze/", SITO + "/farmaci/", SITO + "/diario/", SITO + "/sostieni/", SITO + "/scatola/", SITO + "/bolletta/", SITO + "/mutuo/", SITO + "/banca/", SITO + "/cambio/", SITO + "/bollo/", SITO + "/assegno-unico/", SITO + "/carburante/", SITO + "/carburante/prezzi-medi/", SITO + "/bagaglio/", SITO + "/treno/", SITO + "/agenti/", SITO + "/squadra/", SITO + "/affitto-istat/", SITO + "/tasse-aeroportuali/"] + [SITO + "/carburante/" + c.name + "/" for c in sorted(pathlib.Path("carburante").iterdir()) if c.is_dir() and c.name not in ("leaflet", "prezzi-medi")] + [SITO + "/" + t for t in (json.load(open("data/tratte.json")) if pathlib.Path("data/tratte.json").exists() else [])] + [SITO + "/" + t["percorso"] for t in json.load(open("data/voli_testi.json", encoding="utf-8")).values()] + [SITO + "/" + t for t in (json.load(open("data/compagnie.json")) if pathlib.Path("data/compagnie.json").exists() else [])]
elenco = []
for principio, gruppi in sorted(per_principio.items(), key=lambda x: slug(x[0])):
    s = slug(principio)
    marche = []
    for g in gruppi:
        for f in g["f"]:
            nome = f[0].title()
            if nome not in marche and not nome.lower().startswith(principio.lower()[:5]):
                marche.append(nome)
    marche_tit = ", ".join(marche[:3])
    titolo = f"{principio}: farmaci equivalenti e prezzi" + (f" ({marche_tit})" if marche_tit else "")
    massimo = max((f[4] or 0) for g in gruppi for f in g["f"])
    descr = (f"{principio}"
             + (f" ({', '.join(marche[:5])})" if marche else "")
             + f": confronta i prezzi delle {sum(len(g['f']) for g in gruppi)} confezioni equivalenti"
             + (f" e risparmia fino a {eur(massimo)} a confezione" if massimo else "")
             + ". Dati ufficiali AIFA al " + d["prezzi_al"] + ".")
    blocchi = []
    def riga(f):
        return (f'<tr><td><b>{e(f[0])}</b><div class="sub">{e(f[1])} · {e(f[2])}</div></td>'
                f'<td class="prezzo">{eur(f[3])}<div class="sub">'
                + (f'<span class="extra">+{eur(f[4])}</span>' if f[4] else '<span class="zero">✓ nessuna differenza</span>')
                + "</div></td></tr>")
    for g in gruppi:
        care = sorted([f for f in g["f"] if f[4]], key=lambda f: -(f[4] or 0))
        zero = [f for f in g["f"] if not f[4]]
        html_care = f'<table>{"".join(riga(f) for f in care)}</table>' if care else '<p class="zero">✓ Tutte le confezioni costano uguale: nessuna differenza da pagare.</p>'
        html_zero = (f'<details class="gen"><summary>✓ {len(zero)} equivalent{"e" if len(zero)==1 else "i"} senza differenza da pagare ›</summary>'
                     f'<table>{"".join(riga(f) for f in zero)}</table></details>') if zero and care else (f'<table>{"".join(riga(f) for f in zero)}</table>' if zero else "")
        risparmio = f'<div><span class="sub">Risparmi fino a</span><b class="extra">{eur(max(f[4] for f in care))}</b></div>' if care else ''
        m = re.match(r"\s*(\d+)\s*UNITA", g["c"])
        unita = int(m.group(1)) if m else 0
        anno = (f'<p class="anno">💶 Se ne prendi una al giorno, con un equivalente senza differenza risparmi fino a <b>{eur(max(f[4] for f in care) * 365 / unita)}</b> all\'anno.</p>'
                if care and unita >= 5 else '')
        blocchi.append(f'<div class="card"><h2 style="margin-top:0;font-size:19px">{e(g["c"])}</h2>'
                       f'<div class="riassunto"><div><span class="sub">Rimborsato fino a</span><b>{eur(g["r"])}</b></div>'
                       f'<div><span class="sub">Equivalenti senza differenza</span><b class="zero">{len(zero)}</b></div>{risparmio}</div>'
                       + (f'<p class="sub" style="margin:4px 0 0">Marche che costano di più (la differenza la paghi tu):</p>' if care else '')
                       + anno + html_care + html_zero + '</div>')
    pagina = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)} | Tobia & Co.</title>
<meta name="description" content="{e(descr)}">
<link rel="canonical" href="{SITO}/farmaci/{s}/">
<link rel="icon" href="../../img/tobia-base.svg">
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<div class="wrap">
  <header class="top"><img src="../../img/tobia-base.svg" alt=""><a href="../../">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="../../#strumenti">Strumenti</a><a class="nasc" href="../../diario/">Diario</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>
  <nav class="briciole"><a href="../../">🏠 Home</a> › <a href="../">Farmaci</a> › {e(principio)}</nav>
  <span class="occhiello">💊 Farmaci equivalenti</span>
  <h1>{e(principio)}: equivalenti e prezzi</h1>
  <p class="lead">{e(descr)} Con la ricetta il Servizio sanitario paga fino al prezzo di riferimento: se scegli una confezione che costa di più, la differenza la paghi tu.</p>
  {''.join(blocchi)}
  <div class="card"><p class="note">⚠️ Prima di cambiare farmaco <b>chiedi sempre al farmacista o al medico</b>. Dati: liste di trasparenza AIFA (prezzi al {e(d['prezzi_al'])}, aggiornati il {e(d['aggiornato'])}). Pagina informativa, non un consiglio medico.</p>
  <div class="azioni"><a class="btn" href="../">🔎 Cerca un altro farmaco</a><a class="btn chiaro" href="../../scatola/">⏰ Promemoria: quando finisce la scatola</a></div></div>
  <footer><a href="../../">← Tutti gli strumenti</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ti è stato utile? Offri un caffè</a> · Dati aggiornati automaticamente da Rita la Farmacista, il robottino di Tobia (un'intelligenza artificiale, Claude). Può contenere errori: verifica sempre in farmacia.</footer>
</div>
<script src="../../js/conta.js" defer></script>
</body>
</html>
"""
    (base / s).mkdir(parents=True, exist_ok=True)
    (base / s / "index.html").write_text(pagina, encoding="utf-8")
    indirizzi.append(f"{SITO}/farmaci/{s}/")
    elenco.append((principio, s, marche[:4]))

# elenco di tutti i principi attivi in fondo alla pagina di ricerca
voci = "".join(f'<li><a href="{s}/">{e(p)}</a>' + (f' <span class="note">({e(", ".join(m))})</span>' if m else "") + "</li>" for p, s, m in elenco)
pag = pathlib.Path("farmaci/index.html")
testo = pag.read_text(encoding="utf-8")
testo = re.sub(r"<!-- ELENCO -->.*?<!-- /ELENCO -->", lambda _: f'<!-- ELENCO --><div class="card"><h2 style="margin-top:0">📚 Tutti i farmaci</h2><ul>{voci}</ul></div><!-- /ELENCO -->', testo, flags=re.S)
pag.write_text(testo, encoding="utf-8")

indirizzi = list(dict.fromkeys(indirizzi))   # niente doppioni
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
    "".join(f"<url><loc>{u}</loc><lastmod>{oggi}</lastmod></url>\n" for u in indirizzi) + "</urlset>\n"
pathlib.Path("sitemap.xml").write_text(sitemap, encoding="utf-8")
pathlib.Path("data/indirizzi.txt").write_text("\n".join(indirizzi) + "\n", encoding="utf-8")
print(len(elenco), "pagine di farmaci,", len(indirizzi), "indirizzi nella sitemap")
