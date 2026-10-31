"""Rita la Farmacista, parte 2: da data/farmaci.json crea una pagina per ogni principio attivo
(farmaci/<nome>/index.html), la sitemap.xml e la lista degli indirizzi per IndexNow."""
import json, re, html, pathlib, shutil, unicodedata, datetime

SITO = "https://tobia-and-co.github.io"
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

indirizzi = [SITO + "/", SITO + "/scadenze/", SITO + "/farmaci/", SITO + "/diario/"]
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
    for g in gruppi:
        righe = "".join(
            f'<tr><td><b>{e(f[0])}</b><div class="sub">{e(f[1])} · {e(f[2])}</div></td>'
            f'<td style="text-align:right;white-space:nowrap">{eur(f[3])}<div class="sub">'
            + (f'<span class="extra">+{eur(f[4])}</span>' if f[4] else '<span class="zero">✓ nessuna differenza</span>')
            + "</div></td></tr>" for f in g["f"])
        blocchi.append(f'<div class="card"><h2 style="margin-top:0;font-size:18px">{e(g["c"])}</h2>'
                       f'<div class="sub">Rimborsato dal Servizio sanitario fino a <b>{eur(g["r"])}</b></div><table>{righe}</table></div>')
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
<style>.zero{{color:var(--ok);font-weight:700}}.extra{{color:#c0392b;font-weight:700}}.sub{{font-size:13px;color:var(--muted)}}</style>
</head>
<body>
<div class="wrap">
  <header class="top"><img src="../../img/tobia-lavoro.svg" alt=""><a href="../../">Tobia &amp; Co.</a></header>
  <h1>💊 {e(principio)}: farmaci equivalenti e prezzi</h1>
  <p class="lead">{e(descr)} Con la ricetta il Servizio sanitario paga fino al prezzo di riferimento: se scegli una confezione che costa di più, la differenza la paghi tu.</p>
  {''.join(blocchi)}
  <div class="card"><p class="note">⚠️ Prima di cambiare farmaco <b>chiedi sempre al farmacista o al medico</b>. Dati: liste di trasparenza AIFA (prezzi al {e(d['prezzi_al'])}, aggiornati il {e(d['aggiornato'])}). Pagina informativa, non un consiglio medico.</p>
  <a class="btn" href="../">🔎 Cerca un altro farmaco</a></div>
  <footer><a href="../../">← Tutti gli strumenti</a> · Dati aggiornati automaticamente da Rita la Farmacista, il robottino di Tobia (un'intelligenza artificiale, Claude). Può contenere errori: verifica sempre in farmacia.</footer>
</div>
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

sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
    "".join(f"<url><loc>{u}</loc><lastmod>{oggi}</lastmod></url>\n" for u in indirizzi) + "</urlset>\n"
pathlib.Path("sitemap.xml").write_text(sitemap, encoding="utf-8")
pathlib.Path("data/indirizzi.txt").write_text("\n".join(indirizzi) + "\n", encoding="utf-8")
print(len(elenco), "pagine di farmaci,", len(indirizzi), "indirizzi nella sitemap")
