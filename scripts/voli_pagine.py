"""Crea le pagine del calcolatore voli nelle 5 lingue da data/voli_testi.json."""
import html, json, pathlib

SITO = "https://tobia-and-co.pages.dev"
TESTI = json.load(open("data/voli_testi.json", encoding="utf-8"))
NOMI = {"it": "Italiano", "en": "English", "es": "Español", "fr": "Français", "de": "Deutsch"}
e = lambda s: html.escape(s, quote=True)

for lingua, T in TESTI.items():
    base = "../" * T["percorso"].count("/")
    altre = " · ".join(f'<a href="{base}{TESTI[l]["percorso"]}" hreflang="{l}">{NOMI[l]}</a>' for l in TESTI if l != lingua)
    alternate = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{SITO}/{TESTI[l]["percorso"]}">' for l in TESTI)
    opz = lambda chiavi: "".join(f'<option value="{v}">{e(T[k])}</option>' for v, k in chiavi)
    pagina = f"""<!doctype html>
<html lang="{lingua}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(T['title'])} | Tobia & Co.</title>
<meta name="description" content="{e(T['description'])}">
<link rel="canonical" href="{SITO}/{T['percorso']}">
{alternate}
<link rel="icon" href="{base}img/tobia-base.svg">
<link rel="stylesheet" href="{base}style.css">
</head>
<body>
<div class="wrap">
  <header class="top"><img src="{base}img/tobia-base.svg" alt=""><a href="{base}">Tobia &amp; Co.</a><nav class="menu"><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ko-fi</a></nav></header>
  <nav class="briciole"><a href="{base}">🏠 {e(T['home'])}</a> › {e(T['sezione'])}</nav>
  <span class="occhiello">{e(T['occhiello'])}</span>
  <h1>{e(T['h1'])}</h1>
  <p class="lead">{e(T['lead'])}</p>

  <form class="card" id="modulo" autocomplete="off">
    <label for="da">{e(T['da'])}</label>
    <input id="da" placeholder="{e(T['segnaposto'])}"><div id="da-lista" class="lista"></div>
    <label for="a">{e(T['a'])}</label>
    <input id="a" placeholder="{e(T['segnaposto'])}"><div id="a-lista" class="lista"></div>
    <label class="check"><input type="checkbox" id="ue" checked> {e(T['ue'])}</label>
    <label for="evento">{e(T['evento'])}</label>
    <select id="evento">{opz([('ritardo','e_ritardo'),('cancellato','e_cancellato'),('negato','e_negato')])}</select>
    <div id="box-ritardo"><label for="ritardo">{e(T['ritardo'])}</label>
    <select id="ritardo">{opz([('4','r_4'),('3','r_3'),('2','r_2'),('0','r_0')])}</select></div>
    <div id="box-avviso" hidden><label for="avviso">{e(T['avviso'])}</label>
    <select id="avviso">{opz([('0','a_0'),('7','a_7'),('14','a_14')])}</select></div>
    <label for="causa">{e(T['causa'])}</label>
    <select id="causa">{opz([('tecnico','c_tecnico'),('sciopero','c_sciopero'),('meteo','c_meteo'),('atc','c_atc'),('sicurezza','c_sicurezza')])}</select>
    <p style="margin-top:20px"><button type="submit">✈️ {e(T['calcola'])}</button></p>
  </form>
  <div id="esito"></div>

  <p class="note">📚 <a href="{T['fonte_url']}" rel="noopener">{e(T['fonte'])}</a></p>
  <p class="note">🌍 {e(T['lingue'])}: {altre}</p>
  <footer><a href="{base}">← Tobia &amp; Co.</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ko-fi</a> · {e(T['avvertenza'])}</footer>
</div>
<script>window.T={json.dumps(T, ensure_ascii=False)};window.BASE="{base}";</script>
<script src="{base}js/voli.js" defer></script>
<script src="{base}js/conta.js" defer></script>
</body>
</html>
"""
    cartella = pathlib.Path(T["percorso"])
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / "index.html").write_text(pagina, encoding="utf-8")
print("pagine voli:", ", ".join(T["percorso"] for T in TESTI.values()))

# ---- Pagine delle tratte più cercate (italiano) ----
import math, re, unicodedata
AER = {a[0]: a for a in json.load(open("data/aeroporti.json", encoding="utf-8"))}
CITTA_IT = {"FCO": "Roma", "MXP": "Milano", "LIN": "Milano Linate", "BGY": "Bergamo", "NAP": "Napoli", "VCE": "Venezia",
            "BLQ": "Bologna", "CTA": "Catania", "PMO": "Palermo", "BRI": "Bari", "CAG": "Cagliari", "TRN": "Torino",
            "FLR": "Firenze", "PSA": "Pisa"}
DEST = {"JFK": "New York", "LHR": "Londra", "CDG": "Parigi", "BCN": "Barcellona", "MAD": "Madrid", "AMS": "Amsterdam",
        "FRA": "Francoforte", "MUC": "Monaco di Baviera", "ATH": "Atene", "LIS": "Lisbona", "DXB": "Dubai", "IST": "Istanbul",
        "BRU": "Bruxelles", "VIE": "Vienna", "PRG": "Praga", "BER": "Berlino", "DUB": "Dublino", "CPH": "Copenaghen",
        "ZRH": "Zurigo", "TFS": "Tenerife", "MIA": "Miami", "BKK": "Bangkok", "CUN": "Cancún", "GRU": "San Paolo"}
PARTENZE = ["FCO", "MXP", "NAP", "VCE", "BLQ", "CTA", "PMO", "BRI", "BGY", "TRN"]
INTERNE = [("FCO", "CTA"), ("FCO", "PMO"), ("LIN", "FCO"), ("LIN", "NAP"), ("MXP", "CTA"), ("MXP", "PMO"), ("LIN", "BRI"),
           ("FCO", "CAG"), ("BLQ", "CTA"), ("VCE", "NAP"), ("TRN", "NAP"), ("BGY", "PMO"), ("PSA", "CTA"), ("FLR", "CTA")]
UE_PAESI = set('AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE IS NO CH LI'.split())

def km(p, q):
    r = math.pi / 180
    x = math.sin((q[4]-p[4])*r/2)**2 + math.cos(p[4]*r)*math.cos(q[4]*r)*math.sin((q[5]-p[5])*r/2)**2
    return round(2 * 6371 * math.asin(math.sqrt(x)))
def slug(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

T = TESTI["it"]
tratte = [(d, a) for d in PARTENZE for a in DEST] + INTERNE
nomi = {**CITTA_IT, **DEST}
elenco = []
for da, a in tratte:
    if da not in AER or a not in AER: continue
    d = km(AER[da], AER[a]); intra = AER[a][3] in UE_PAESI
    importo = 250 if d <= 1500 else (400 if d <= 3500 or intra else 600)
    nda, na = nomi[da], nomi[a]
    perc = f"voli/{slug(nda)}-{slug(na)}/"
    titolo = f"Volo {nda} – {na} in ritardo o cancellato? Ti spettano fino a {importo} €"
    descr = (f"Il volo da {nda} ({da}) a {na} ({a}) è di circa {d:,} km".replace(",", ".") +
             f": con più di 3 ore di ritardo all'arrivo, una cancellazione o l'imbarco negato ti spettano fino a {importo} € a persona (Regolamento UE 261/2004). Calcolalo e chiedilo con la lettera pronta.")
    extra = ("Sui voli oltre i 3.500 km, se il ritardo all'arrivo è tra 3 e 4 ore l'importo si dimezza (300 €)." if importo == 600 else "")
    pagina = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)} | Tobia & Co.</title>
<meta name="description" content="{e(descr)}">
<link rel="canonical" href="{SITO}/{perc}">
<link rel="icon" href="../../img/tobia-base.svg">
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<div class="wrap">
  <header class="top"><img src="../../img/tobia-base.svg" alt=""><a href="../../">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="../../#strumenti">Strumenti</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>
  <nav class="briciole"><a href="../../">🏠 Home</a> › <a href="../">Voli</a> › {e(nda)} – {e(na)}</nav>
  <span class="occhiello">Regolamento UE 261/2004</span>
  <h1>✈️ Volo {e(nda)} – {e(na)} in ritardo?</h1>
  <p class="lead">{e(descr)}</p>
  <div class="card"><div class="riassunto">
    <div><span class="sub">Distanza</span><b>{d:,} km</b></div>
    <div><span class="sub">Ti spettano fino a</span><b class="zero">{importo} €</b></div>
    <div><span class="sub">Ritardo minimo</span><b>3 ore</b></div>
  </div>{f'<p class="note">{e(extra)}</p>' if extra else ''}<p class="note">Vale per i voli che partono dall'Italia con qualsiasi compagnia, e per il ritorno se la compagnia è europea.</p></div>
  <h2>Calcola il tuo caso</h2>
  <form class="card" id="modulo" autocomplete="off">
    <label for="da">{e(T['da'])}</label><input id="da" placeholder="{e(T['segnaposto'])}"><div id="da-lista" class="lista"></div>
    <label for="a">{e(T['a'])}</label><input id="a" placeholder="{e(T['segnaposto'])}"><div id="a-lista" class="lista"></div>
    <label class="check"><input type="checkbox" id="ue" checked> {e(T['ue'])}</label>
    <label for="evento">{e(T['evento'])}</label>
    <select id="evento"><option value="ritardo">{e(T['e_ritardo'])}</option><option value="cancellato">{e(T['e_cancellato'])}</option><option value="negato">{e(T['e_negato'])}</option></select>
    <div id="box-ritardo"><label for="ritardo">{e(T['ritardo'])}</label><select id="ritardo"><option value="4">{e(T['r_4'])}</option><option value="3">{e(T['r_3'])}</option><option value="2">{e(T['r_2'])}</option><option value="0">{e(T['r_0'])}</option></select></div>
    <div id="box-avviso" hidden><label for="avviso">{e(T['avviso'])}</label><select id="avviso"><option value="0">{e(T['a_0'])}</option><option value="7">{e(T['a_7'])}</option><option value="14">{e(T['a_14'])}</option></select></div>
    <label for="causa">{e(T['causa'])}</label>
    <select id="causa"><option value="tecnico">{e(T['c_tecnico'])}</option><option value="sciopero">{e(T['c_sciopero'])}</option><option value="meteo">{e(T['c_meteo'])}</option><option value="atc">{e(T['c_atc'])}</option><option value="sicurezza">{e(T['c_sicurezza'])}</option></select>
    <p style="margin-top:20px"><button type="submit">✈️ {e(T['calcola'])}</button></p>
  </form>
  <div id="esito"></div>
  <p class="note">📚 <a href="{T['fonte_url']}" rel="noopener">{e(T['fonte'])}</a> · <a href="../">Altre tratte e altri casi ›</a></p>
  <footer><a href="../../">← Tobia &amp; Co.</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ko-fi</a> · {e(T['avvertenza'])}</footer>
</div>
<script>window.T={json.dumps(T, ensure_ascii=False)};window.BASE="../../";window.PREFILL={json.dumps([da, a])};</script>
<script src="../../js/voli.js" defer></script>
<script src="../../js/conta.js" defer></script>
</body>
</html>
""".replace(f"{d:,} km", f"{d:,} km".replace(",", "."))
    pathlib.Path(perc).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(perc) / "index.html").write_text(pagina, encoding="utf-8")
    elenco.append((nda, na, perc, importo))
json.dump([p for _, _, p, _ in elenco], open("data/tratte.json", "w"))
# elenco delle tratte in fondo alla pagina italiana dei voli
voci = "".join(f'<li><a href="{p.replace("voli/", "")}">{e(x)} – {e(y)}</a> <span class="note">fino a {i} €</span></li>' for x, y, p, i in elenco)
pag = pathlib.Path("voli/index.html"); t = pag.read_text(encoding="utf-8")
t = t.replace('<p class="note">📚', '<div class="card"><b>🛫 Cerchi la tua compagnia?</b> <a href="compagnia/">Ryanair, ITA Airways, easyJet, Wizz Air e altre 41</a> · <a href="sciopero/">Volo cancellato per sciopero?</a> · <a href="aeroporto/">Il tuo aeroporto</a> · <a href="volo-cancellato/">Volo cancellato</a> · <a href="overbooking/">Overbooking</a> · <a href="coincidenza-persa/">Coincidenza persa</a></div>\n  <p class="note">📚', 1)
t = t.replace('<p class="note">📚', f'<details class="card"><summary><b>🛫 Le tratte più cercate dall\'Italia</b></summary><ul>{voci}</ul></details>\n  <p class="note">📚', 1)
pag.write_text(t, encoding="utf-8")
print(len(elenco), "pagine di tratte")
