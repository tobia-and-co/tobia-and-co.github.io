"""Fabio il Farmacista, parte 2: da data/carenze.json crea una pagina per ogni farmaco carente
(farmaci/carenti/<nome>/index.html), cancella quelle dei farmaci non più carenti,
scrive l'elenco in data/carenti_pagine.txt e lo mette in sitemap.xml / data/indirizzi.txt.
Rita (rita_pagine.py) legge data/carenti_pagine.txt, così non le cancella dalla sitemap."""
import json, re, html, pathlib, shutil, unicodedata, datetime

SITO = "https://tobia-and-co.pages.dev"
MARCATORE = "<!-- fabio-pagina -->"
d = json.load(open("data/carenze.json", encoding="utf-8"))
base = pathlib.Path("farmaci/carenti")
e = lambda s: html.escape(s, quote=True)

def slug(s):   # stesso metodo di rita_pagine.py
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:80]

def dt(s):
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s or "")
    return f"{m[3]}/{m[2]}/{m[1]}" if m else (s or "")

def titolo(n):   # ABIOCLAV -> Abioclav
    return re.sub(r" (E|Di|Da|Con|Per|In) ", lambda m: m[0].lower(), n.title()) if n.isupper() else n

gruppi = {}
for r in d["carenze"]:
    if not r.get("nome"):
        continue
    s = slug(r["nome"])
    if s:
        gruppi.setdefault(s, []).append(r)

def unici(righe, k):
    out = []
    for r in righe:
        v = (r.get(k) or "").strip()
        if v and v not in out:
            out.append(v)
    return out

agg = d.get("aggiornato", "")
fonte = d.get("pagina", "https://www.aifa.gov.it/farmaci-carenti")
indirizzi = []
for s, righe in sorted(gruppi.items()):
    nome = titolo(righe[0]["nome"])
    inizi = sorted(r["inizio"] for r in righe if r.get("inizio"))
    fini = [r.get("fine") for r in righe]
    fine = max(fini) if fini and all(fini) else ""
    motivi = unici(righe, "motivo")
    sugg = unici(righe, "suggerimenti")
    principi = unici(righe, "principio")
    risposta = "Sì, secondo l'AIFA: carente" + (f" dal <b>{dt(inizi[0])}</b>" if inizi else "") \
        + (f", fine prevista <b>{dt(fine)}</b>" if fine else ", data di fine non indicata") + "."
    risposta_txt = re.sub(r"<[^>]+>", "", risposta)
    motivo_txt = ("Motivo: " + "; ".join(m.lower() if i else m for i, m in enumerate(motivi)) + ".") if motivi else ""
    cosa = "".join(f"<li>{e(t)}</li>" for t in sugg) or "<li>L'AIFA non indica un suggerimento specifico per questo farmaco.</li>"
    link_pr = ""
    for p in principi:
        sp = slug(p)
        if sp and (pathlib.Path("farmaci") / sp / "index.html").exists():
            link_pr += f'<p><a class="btn chiaro" href="../../{sp}/">💊 Altri farmaci con lo stesso principio attivo ({e(p.title())}) e i prezzi</a></p>'
    righe_t = "".join(
        f"<tr><td>{e(r.get('confezione',''))}</td><td>{e(r.get('titolare',''))}</td><td>{e(dt(r.get('inizio','')))}</td><td>{e(dt(r.get('fine','')) or '—')}</td></tr>"
        for r in sorted(righe, key=lambda r: r.get("confezione", "")))
    descr = f"{nome} è carente? " + risposta_txt + (" " + motivo_txt if motivo_txt else "") + " Cosa fare, secondo l'AIFA."
    descr = descr[:300]
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f"{nome} è carente?", "acceptedAnswer": {"@type": "Answer", "text": risposta_txt + (" " + motivo_txt if motivo_txt else "")}},
        {"@type": "Question", "name": f"Cosa posso fare se non trovo {nome}?", "acceptedAnswer": {"@type": "Answer", "text":
            " ".join(sugg[:2]) + " Chiedi al medico o al farmacista prima di cambiare farmaco." if sugg else "Chiedi al medico o al farmacista un medicinale equivalente con lo stesso principio attivo: non cambiare farmaco da solo."}}]}
    pagina = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(nome)} è carente? Lista AIFA | Tobia & Co.</title>
<meta name="description" content="{e(descr)}">
<link rel="canonical" href="{SITO}/farmaci/carenti/{s}/">
<link rel="icon" href="../../../img/tobia-base.svg">
<link rel="stylesheet" href="../../../style.css">
<script type="application/ld+json">{json.dumps(faq, ensure_ascii=False).replace("</", "<\\/")}</script>
<style>.tab{{overflow-x:auto}}.tab table{{font-size:.8em}}.tab td,.tab th{{padding:6px 3px}}.tab td:nth-child(2){{min-width:85px}}.tab td:nth-child(1),.tab td:nth-child(3),.tab td:nth-child(4),.tab th{{white-space:nowrap}}</style>
</head>
<body>
{MARCATORE}
<div class="wrap">
  <header class="top"><img src="../../../img/tobia-base.svg" alt=""><a href="../../../">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="../../../#strumenti">Strumenti</a><a class="nasc" href="../../../diario/">Diario</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>
  <nav class="briciole"><a href="../../../">🏠 Home</a> › <a href="../../">Farmaci</a> › <a href="../">Farmaci carenti</a> › {e(nome)}</nav>
  <span class="occhiello">🚫 Farmaco carente</span>
  <h1>{e(nome)} è carente?</h1>
  <p class="lead">{risposta}{" " + e(motivo_txt) if motivo_txt else ""}</p>
  <div class="card"><h2 style="margin-top:0;font-size:19px">Cosa fare</h2>
  <ul>{cosa}</ul>
  <p><b>Chiedi al medico o al farmacista prima di cambiare farmaco.</b></p>
  {link_pr}</div>
  <div class="card"><h2 style="margin-top:0;font-size:19px">Confezioni interessate</h2>
  <div class="tab"><table><tr><th>Codice AIC</th><th>Titolare</th><th>Inizio</th><th>Fine</th></tr>{righe_t}</table></div></div>
  <div class="card"><p class="note">Fonte: <a href="{e(fonte)}" rel="noopener">elenco dei medicinali carenti dell'AIFA</a>, aggiornato <span class="agg-aifa">ogni mattina</span><script>fetch("../../../data/carenze_data.json",{{cache:"no-store"}}).then(r=>r.json()).then(j=>{{var m=/(\\d{{4}})-(\\d{{2}})-(\\d{{2}})/.exec(j.aggiornato||"");if(m)document.querySelector(".agg-aifa").textContent="il "+ +m[3]+"/"+(+m[2])+"/"+m[1]}}).catch(()=>{{}})</script>. Pagina creata da un programma automatico (Fabio, il robottino di Tobia & Co.); non sostituisce il medico e può contenere errori.</p>
  <div class="azioni"><a class="btn" href="../">🔎 Cerca un altro farmaco carente</a></div></div>
  <footer><a href="../../../">← Tutti gli strumenti</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ti è stato utile? Offri un caffè</a> · Dati aggiornati automaticamente da Fabio il Farmacista, il robottino di Tobia (un'intelligenza artificiale, Claude). Non collegato ad AIFA.</footer>
</div>
<script src="../../../js/conta.js" defer></script>
</body>
</html>
"""
    (base / s).mkdir(parents=True, exist_ok=True)
    (base / s / "index.html").write_text(pagina, encoding="utf-8")
    indirizzi.append(f"{SITO}/farmaci/carenti/{s}/")

# pulizia: via le pagine generate da me che non sono più nella lista
tolte = 0
for c in base.iterdir():
    f = c / "index.html"
    if c.is_dir() and c.name not in gruppi and f.exists() and MARCATORE in f.read_text(encoding="utf-8"):
        shutil.rmtree(c); tolte += 1

pathlib.Path("data/carenze_data.json").write_text(json.dumps({"aggiornato": agg}), encoding="utf-8")
pathlib.Path("data/carenti_pagine.txt").write_text("\n".join(indirizzi) + "\n", encoding="utf-8")

# sitemap e indirizzi per IndexNow: togli le vecchie pagine carenti e metti le attuali
rx = re.compile(r"/farmaci/carenti/[^/<\s]+/")
oggi = datetime.date.today().isoformat()
sm = pathlib.Path("sitemap.xml")
if sm.exists():
    righe_sm = [l for l in sm.read_text(encoding="utf-8").splitlines() if not rx.search(l)]
    nuove = [f"<url><loc>{u}</loc><lastmod>{oggi}</lastmod></url>" for u in indirizzi]
    righe_sm = righe_sm[:-1] + nuove + righe_sm[-1:]   # prima di </urlset>
    sm.write_text("\n".join(righe_sm) + "\n", encoding="utf-8")
ind = pathlib.Path("data/indirizzi.txt")
if ind.exists():
    ok = [l for l in ind.read_text(encoding="utf-8").split() if not rx.search(l)]
    ind.write_text("\n".join(ok + indirizzi) + "\n", encoding="utf-8")
print(len(indirizzi), "pagine di farmaci carenti,", tolte, "tolte")
