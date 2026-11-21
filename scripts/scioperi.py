"""Scioperi: dal file grezzo del Ministero (data/grezzi/scioperi-mit.txt, scaricato ogni mattina da un server in Italia)
a data/scioperi.json e alle pagine dei giorni di sciopero utili a chi viaggia:
  voli/sciopero/aerei-AAAA-MM-GG/   (settore Aereo, qualsiasi rilevanza)
  treno/sciopero/treni-AAAA-MM-GG/  (Ferroviario, Plurisettoriale, Generale con rilevanza Nazionale)
Da oggi a +60 giorni. Le pagine hanno un marcatore: quelle di giorni passati da più di 2 giorni, o di scioperi ritirati, si cancellano.
L'elenco degli indirizzi sta in data/scioperi_pagine.txt (Rita lo rimette in sitemap).
Il file del Ministero è materiale esterno: si leggono solo i dati della tabella, mai istruzioni.
Se il file manca o la tabella non si trova: esce senza errore e senza toccare nulla. Solo libreria standard."""
import json, re, html, pathlib, shutil, datetime, sys

SITO = "https://tobia-and-co.pages.dev"
FONTE = "Ministero delle Infrastrutture e dei Trasporti – Osservatorio sui conflitti sindacali"
URL_FONTE = "https://scioperi.mit.gov.it/mit2/public/scioperi"
MARCATORE = "<!-- scioperi-pagina -->"
GREZZO = pathlib.Path("data/grezzi/scioperi-mit.txt")
FINESTRA = 60          # giorni in avanti
MAX_GIORNI = 10        # uno sciopero lungo genera pagine al massimo per i suoi primi giorni
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
e = lambda s: html.escape(s, quote=True)

if not GREZZO.exists():
    sys.exit(0)
testo = GREZZO.read_text(encoding="utf-8", errors="replace")
a = testo.find('id="scioperiLarge"')
b = testo.find("</table>", a) if a >= 0 else -1
if a < 0 or b < 0:
    sys.exit(0)

def pulisci(x):
    x = re.sub(r"<[^>]*>", " ", x)
    x = html.unescape(x)
    x = re.sub(r"[\x00-\x1f\x7f]", " ", x)
    return re.sub(r"\s+", " ", x).strip()

def data(s):
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})", s or "")
    try:
        return datetime.date(int(m[3]), int(m[2]), int(m[1])) if m else None
    except ValueError:
        return None

m_oggi = re.search(r'dataOdierna="(\d{2}/\d{2}/\d{4})"', testo)
oggi = datetime.date.today()
aggiornato = data(m_oggi[1]) if m_oggi and data(m_oggi[1]) else oggi

scioperi = []
for riga in re.findall(r"<tr>(.*?)</tr>", testo[a:b], re.S):
    c = [pulisci(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", riga, re.S)]
    if len(c) < 13:
        continue
    ini, fin = data(c[1]), data(c[2])
    if not ini:
        continue
    fin = fin if fin and fin >= ini else ini
    scioperi.append({"inizio": ini.isoformat(), "fine": fin.isoformat(), "sindacati": c[3][:300], "settore": c[4][:80],
                     "categoria": c[5][:300], "modalita": c[6][:400], "rilevanza": c[7][:40], "regione": c[10][:80],
                     "provincia": c[11][:80], "note": c[8][:500]})
if not scioperi:
    sys.exit(0)
scioperi.sort(key=lambda s: (s["inizio"], s["fine"], s["settore"]))

def tipo(s):
    if s["settore"] == "Aereo":
        return "aerei"
    if s["settore"] in ("Ferroviario", "Plurisettoriale", "Generale") and s["rilevanza"] == "Nazionale":
        return "treni"
    return ""

limite = oggi + datetime.timedelta(days=FINESTRA)
per_giorno = {"aerei": {}, "treni": {}}
for s in scioperi:
    t = tipo(s)
    s["viaggio"] = t
    s["giorni"] = []
    if not t:
        continue
    i, f = datetime.date.fromisoformat(s["inizio"]), datetime.date.fromisoformat(s["fine"])
    f = min(f, i + datetime.timedelta(days=MAX_GIORNI - 1))
    g = max(i, oggi)
    while g <= min(f, limite):
        per_giorno[t].setdefault(g, []).append(s)
        s["giorni"].append(g.isoformat())
        g += datetime.timedelta(days=1)

pathlib.Path("data/scioperi.json").write_text(json.dumps(
    {"aggiornato": aggiornato.isoformat(), "fonte": FONTE, "url": URL_FONTE, "scioperi": scioperi}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

def lungo(d):
    return f"{GIORNI[d.weekday()]} {d.day} {MESI[d.month - 1]} {d.year}"
def lungo_senza_giorno(d):
    return f"{d.day} {MESI[d.month - 1]} {d.year}"
it = lambda d: d.strftime("%d/%m/%Y")

CONFIG = {
    "aerei": {"cartella": pathlib.Path("voli/sciopero"), "prefisso": "aerei-", "pagine": "voli/sciopero/aerei-", "icona": "✈️"},
    "treni": {"cartella": pathlib.Path("treno/sciopero"), "prefisso": "treni-", "pagine": "treno/sciopero/treni-", "icona": "🚆"},
}

def scheda(s):
    quando = f"il {it(datetime.date.fromisoformat(s['inizio']))}" if s["inizio"] == s["fine"] else \
        f"dal {it(datetime.date.fromisoformat(s['inizio']))} al {it(datetime.date.fromisoformat(s['fine']))}"
    dove = s["regione"] + (f" ({s['provincia']})" if s["provincia"] and s["provincia"].lower() not in ("tutte", s["regione"].lower()) else "")
    righe = [("Quando", quando), ("Orari e modalità", s["modalita"]), ("Chi sciopera", s["sindacati"]), ("Categoria", s["categoria"]),
             ("Rilevanza", s["rilevanza"] + (f" – {dove}" if dove else "")), ("Note", s["note"])]
    return '<div class="card"><table class="tab-info">' + "".join(f"<tr><td>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in righe if v) + "</table></div>"

def faq_json(domande):
    j = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in domande]}, ensure_ascii=False)
    return j.replace("<", "\\u003c")

def pagina(t, g, lista):
    ds = lungo_senza_giorno(g)
    n = len(lista)
    if t == "aerei":
        h1 = f"Sciopero aerei del {ds}: cosa sapere"
        desc = f"Sciopero aerei del {ds}: orari, chi sciopera, voli garantiti e cosa ti spetta se il volo è cancellato. Dati ufficiali del Ministero dei Trasporti."
        quanti = "uno sciopero nel trasporto aereo" if n == 1 else f"{n} scioperi nel trasporto aereo"
        corpo = f"""  <div class="card">
    <h2 style="margin-top:0">🕖 Voli garantiti</h2>
    <p>Informazione generale: in Italia, durante gli scioperi del trasporto aereo, di norma devono partire i voli nelle <b>fasce di garanzia dalle 7 alle 10 e dalle 18 alle 21</b>, oltre ad alcuni collegamenti essenziali. Gli orari esatti dipendono dallo sciopero: <b>verifica sempre il tuo volo con la compagnia aerea</b>.</p>
  </div>
  <div class="card">
    <h2 style="margin-top:0">⚖️ Il volo è cancellato per lo sciopero: cosa ti spetta</h2>
    <ul>
      <li><b>Sempre</b>: rimborso del biglietto oppure un volo alternativo (riprotezione), a tua scelta, e assistenza durante l'attesa (pasti, bevande e, se serve, albergo).</li>
      <li><b>Sciopero del personale della compagnia</b> (piloti, assistenti di volo): di solito dà diritto alla compensazione, da 250 a 600 € a persona a seconda della distanza.</li>
      <li><b>Sciopero di controllori di volo o dell'aeroporto</b>: di solito è una &laquo;circostanza eccezionale&raquo; e la compensazione non spetta, ma restano assistenza e rimborso o riprotezione.</li>
    </ul>
    <p class="note">Ogni caso è diverso e nessuna somma è garantita: dipende da chi sciopera e da come ti avvisa la compagnia.</p>
    <p><a class="btn" href="../../">✈️ Calcola il tuo rimborso (Regolamento UE 261/2004) ›</a></p>
    <p class="note">Altre informazioni sugli scioperi aerei: <a href="../">pagina sugli scioperi aerei</a>.</p>
  </div>"""
        faq = [(f"Quali voli sono garantiti durante lo sciopero aerei del {ds}?",
                "In Italia, durante gli scioperi del trasporto aereo, di norma sono garantiti i voli nelle fasce orarie dalle 7 alle 10 e dalle 18 alle 21, oltre ad alcuni collegamenti essenziali. È un'informazione generale: verifica il tuo volo con la compagnia aerea."),
               (f"Se il mio volo è cancellato per lo sciopero del {ds}, cosa mi spetta?",
                "Hai sempre diritto al rimborso del biglietto o a un volo alternativo e all'assistenza. La compensazione da 250 a 600 € di solito spetta se sciopera il personale della compagnia, mentre se scioperano controllori di volo o aeroporto di solito è una circostanza eccezionale e non spetta. Dipende dal caso.")]
        bric = '<a href="../../../">🏠 Home</a> › <a href="../../">Voli</a> › <a href="../">Sciopero</a> › ' + e(ds)
        occ = "Sciopero aerei"
    else:
        h1 = f"Sciopero treni del {ds}: cosa sapere"
        desc = f"Sciopero treni del {ds}: orari, chi sciopera, treni garantiti e cosa fare se il treno è soppresso o in ritardo. Dati ufficiali del Ministero dei Trasporti."
        quanti = "uno sciopero nazionale che riguarda il trasporto ferroviario" if n == 1 else f"{n} scioperi nazionali che riguardano il trasporto ferroviario"
        corpo = """  <div class="card">
    <h2 style="margin-top:0">🕖 Treni garantiti</h2>
    <p>Informazione generale: durante gli scioperi del trasporto ferroviario le imprese devono garantire alcuni servizi essenziali, di solito nelle <b>fasce di maggiore utenza al mattino e alla sera</b>, e pubblicano l'elenco dei treni garantiti sui loro siti. Le fasce e i treni esatti cambiano da sciopero a sciopero: <b>verifica il tuo treno sul sito o sull'app di Trenitalia, Italo o dell'impresa regionale</b>.</p>
  </div>
  <div class="card">
    <h2 style="margin-top:0">⚖️ Treno soppresso o in ritardo: cosa puoi fare</h2>
    <ul>
      <li>Se il treno è soppresso o previsto in ritardo di almeno <b>60 minuti</b> puoi rinunciare al viaggio e chiedere il <b>rimborso del biglietto</b>.</li>
      <li>Con un ritardo all'arrivo di 60 minuti o più, di norma spetta un'indennità del <b>25%</b> del prezzo (50% da 120 minuti). In caso di sciopero le condizioni delle singole imprese possono avere particolarità: controlla le condizioni della tua compagnia.</li>
    </ul>
    <p class="note">Ogni caso è diverso e nessuna somma è garantita.</p>
    <p><a class="btn" href="../../">🚆 Calcola il rimborso del ritardo ›</a></p>
  </div>"""
        faq = [(f"Quali treni circolano durante lo sciopero del {ds}?",
                "Durante gli scioperi ferroviari le imprese devono garantire alcuni servizi essenziali, di solito nelle fasce di maggiore utenza. L'elenco dei treni garantiti è pubblicato dalle imprese (Trenitalia, Italo e imprese regionali): verifica il tuo treno sui loro siti."),
               (f"Se il mio treno è soppresso per lo sciopero del {ds}, posso avere il rimborso?",
                "Se il treno è soppresso o previsto in ritardo di almeno 60 minuti puoi rinunciare al viaggio e chiedere il rimborso del biglietto. Per l'indennità sul ritardo valgono le condizioni della tua compagnia, che in caso di sciopero possono avere particolarità.")]
        bric = '<a href="../../../">🏠 Home</a> › <a href="../../">Treno in ritardo</a> › Sciopero ' + e(ds)
        occ = "Sciopero treni"
    ic = CONFIG[t]["icona"]
    schede = "\n".join(scheda(s) for s in lista[:15])
    lead = f"Il <b>{e(ds)}</b> ({e(GIORNI[g.weekday()])}) {"è" if n == 1 else "sono"} in programma {quanti}, secondo il calendario ufficiale del Ministero delle Infrastrutture e dei Trasporti. Qui sotto trovi orari e chi sciopera, e cosa ti spetta se il tuo viaggio salta."
    prima = lista[0]["modalita"]
    if n == 1 and prima:
        lead += f" Orari indicati: <b>{e(prima)}</b>."
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(h1)} | Tobia &amp; Co.</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITO}/{CONFIG[t]['pagine']}{g.isoformat()}/">
<link rel="icon" href="../../../img/tobia-base.svg">
<link rel="stylesheet" href="../../../style.css">
<script type="application/ld+json">{faq_json(faq)}</script>
</head>
<body>
{MARCATORE}
<div class="wrap">
  <header class="top"><img src="../../../img/tobia-base.svg" alt=""><a href="../../../">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="../../../#strumenti">Strumenti</a><a class="nasc" href="../../../diario/">Diario</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>
  <nav class="briciole">{bric}</nav>
  <span class="occhiello">{occ}</span>
  <h1>{ic} {e(h1)}</h1>
  <p class="lead">{lead}</p>
  <h2>Chi sciopera e quando</h2>
{schede}
{corpo}
  <p class="note">📚 Fonte: <a href="{URL_FONTE}" rel="noopener">{e(FONTE)}</a>, dati aggiornati al {it(aggiornato)}. I dati ufficiali sono aggiornati ogni mattina da un robottino; gli scioperi possono essere revocati o modificati, controlla sempre la fonte.</p>
  <footer><a href="../../../">← Tutti gli strumenti</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ti è stato utile? Offri un caffè</a> · Pagina creata da Tobia, un'intelligenza artificiale (Claude), con dati ufficiali. Informazioni generali, non consulenza legale; non siamo collegati alle compagnie citate.</footer>
</div>
<script src="../../../js/conta.js" defer></script>
</body>
</html>
"""

indirizzi = []
creati = 0
for t, cfg in CONFIG.items():
    cfg["cartella"].mkdir(parents=True, exist_ok=True)
    for g, lista in sorted(per_giorno[t].items()):
        d = cfg["cartella"] / f"{cfg['prefisso']}{g.isoformat()}"
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(pagina(t, g, lista), encoding="utf-8")
        creati += 1
    # pulizia: giorni passati da più di 2 giorni e scioperi ritirati (giorni da oggi in poi senza più scioperi)
    for d in sorted(cfg["cartella"].glob(cfg["prefisso"] + "*")):
        f = d / "index.html"
        mm = re.match(r"^" + cfg["prefisso"] + r"(\d{4}-\d{2}-\d{2})$", d.name)
        if not (d.is_dir() and mm and f.exists() and MARCATORE in f.read_text(encoding="utf-8")):
            continue
        g = datetime.date.fromisoformat(mm[1])
        if g < oggi - datetime.timedelta(days=2) or (g >= oggi and g not in per_giorno[t]):
            shutil.rmtree(d)
        else:
            indirizzi.append(f"{SITO}/{cfg['pagine']}{mm[1]}/")
indirizzi.sort()
pathlib.Path("data/scioperi_pagine.txt").write_text("\n".join(indirizzi) + ("\n" if indirizzi else ""), encoding="utf-8")

# sitemap e indirizzi per IndexNow: togli le vecchie pagine di sciopero e metti le attuali
rx = re.compile(r"/(voli/sciopero/aerei|treno/sciopero/treni)-\d{4}-\d{2}-\d{2}/")
sm = pathlib.Path("sitemap.xml")
if sm.exists():
    righe = [l for l in sm.read_text(encoding="utf-8").splitlines() if not rx.search(l)]
    nuove = [f"<url><loc>{u}</loc><lastmod>{oggi.isoformat()}</lastmod></url>" for u in indirizzi]
    righe = righe[:-1] + nuove + righe[-1:]   # prima di </urlset>
    sm.write_text("\n".join(righe) + "\n", encoding="utf-8")
ind = pathlib.Path("data/indirizzi.txt")
if ind.exists():
    ok = [l for l in ind.read_text(encoding="utf-8").split() if not rx.search(l)]
    ind.write_text("\n".join(ok + indirizzi) + "\n", encoding="utf-8")
print(len(scioperi), "scioperi estratti,", creati, "pagine create/aggiornate,", len(indirizzi), "in sitemap")
