"""Crea la home (index.html) nello stile "A" (riordino) scelto dall'utente l'8/11/2026: ricerca, 4 gruppi, numeri di oggi.
Gli strumenti sono scritti nella pagina (visibili a Google); i numeri si aggiornano nel browser dai dati dei robottini."""
import html, json, pathlib, sys
e = lambda s: html.escape(s, quote=True)
GRUPPI = [
 ("viaggi", "✈️", "Viaggi", "Rimborsi e diritti di chi viaggia", [
   ("✈️", "Volo in ritardo?", "Fino a 600 € a persona, con la lettera pronta", "voli/", "volo aereo ritardo rimborso compensazione 261"),
   ("❌", "Volo cancellato", "Rimborso in 7 giorni e quando spetta di più", "voli/volo-cancellato/", "cancellato volo rimborso"),
   ("📢", "Sciopero aereo", "Quando ti spettano comunque fino a 600 €", "voli/sciopero/", "sciopero aereo volo"),
   ("🚫", "Overbooking e coincidenza persa", "Imbarco negato o volo successivo perso", "voli/overbooking/", "overbooking imbarco negato coincidenza persa"),
   ("🧳", "Bagaglio perso o rotto", "Le scadenze da non perdere e il reclamo", "bagaglio/", "bagaglio valigia persa rotta ritardo"),
   ("🛫", "Non sei partito?", "Riprenditi le tasse aeroportuali", "tasse-aeroportuali/", "tasse aeroportuali rimborso non partito"),
   ("🚆", "Treno in ritardo", "25% del biglietto da 1 ora, 50% da 2 ore", "treno/", "treno ritardo trenitalia italo rimborso")]),
 ("casa", "🏠", "Casa e soldi", "Bollette, banca, affitto, famiglia", [
   ("⚡", "La bolletta è cara?", "Confronto con il prezzo all'ingrosso ufficiale", "bolletta/", "bolletta luce gas energia"),
   ("🧾", "Maxi conguaglio in bolletta?", "I consumi di più di 2 anni fa non si pagano", "bolletta-prescritta/", "bolletta prescritta conguaglio prescrizione due anni luce gas acqua"),
   ("💡", "Bonus sociale bollette", "Con ISEE basso lo sconto arriva da solo", "bonus-sociale/", "bonus sociale bollette isee sconto luce gas acqua disagio"),
   ("📘", "Guide pratiche", "SPID, ISEE e disdetta abbonamenti, con il modulo pronto", "guide/", "guide spid isee disdetta abbonamento recesso lettera dsu"),
   ("🏠", "Aggiornamento ISTAT affitto", "Il nuovo canone e la lettera per l'inquilino", "affitto-istat/", "affitto istat canone inquilino cedolare"),
   ("🏦", "Quanto costa la tua banca", "Canone, carte e bonifici in un anno", "banca/", "banca conto corrente costi"),
   ("🏡", "La rata del mutuo è alta?", "Quanto risparmi con la surroga", "mutuo/", "mutuo surroga rata tasso"),
   ("👶", "Assegno unico 2026", "Quanto ti spetta con gli importi INPS", "assegno-unico/", "assegno unico figli inps isee"),
   ("💱", "Quanto costa il cambio", "La commissione nascosta all'estero", "cambio/", "cambio valuta dollaro sterlina estero")]),
 ("salute", "💊", "Salute", "Farmaci e promemoria", [
   ("💊", "Il tuo farmaco costa meno?", "Gli equivalenti AIFA e quanto risparmi in un anno", "farmaci/", "farmaco medicina generico equivalente aifa"),
   ("🚫", "Farmaco introvabile?", "La lista ufficiale AIFA dei farmaci carenti", "farmaci/carenti/", "farmaco carente introvabile mancante farmacia aifa carenza"),
   ("⏰", "Quando finisce la scatola?", "Il telefono ti ricorda di chiedere la ricetta", "scatola/", "medicina scatola promemoria ricetta")]),
 ("auto", "⛽", "Auto e benzina", "Carburante, bollo e scadenze", [
   ("⛽", "Dove conviene fare benzina", "Prezzo + viaggio: la mappa dei distributori", "carburante/", "benzina gasolio distributore carburante gpl metano"),
   ("📊", "Prezzi medi di oggi", "Benzina e gasolio regione per regione", "carburante/prezzi-medi/", "prezzo medio benzina oggi regione"),
   ("🚗", "Quanto costa il bollo", "Per kW e classe Euro, con il superbollo", "bollo/", "bollo auto superbollo kw"),
   ("🚓", "Ti è arrivata una multa?", "Sconto del 30%, scadenze e ricorso", "multe/", "multa verbale autovelox sconto 30 ricorso prefetto giudice di pace notifica 90 giorni"),
   ("📅", "Le scadenze che ti salvano", "Bollo, revisione, IMU, 730 nel calendario", "scadenze/", "scadenze calendario revisione imu 730 isee carta identita passaporto")]),
]

ORDINE = ["viaggi", "salute", "auto", "casa"]
# quanti strumenti restano in vista per gruppo (gli altri stanno dietro "Vedi tutti")
VISIBILI = {"viaggi": ["voli/", "voli/volo-cancellato/", "voli/sciopero/", "treno/"],
            "salute": None,
            "auto": ["carburante/", "carburante/prezzi-medi/", "multe/", "bollo/"],
            "casa": ["bolletta/", "bolletta-prescritta/", "bonus-sociale/", "mutuo/"]}
PRINCIPALI = [("✈️", "Volo in ritardo", "voli/"), ("💊", "Farmaco che costa meno / introvabile", "farmaci/"),
              ("⛽", "Dove costa meno la benzina", "carburante/"), ("⚡", "Bolletta troppo cara", "bolletta/")]
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("index.html")
tot = sum(len(g[4]) for g in GRUPPI)
farmaci = len(json.load(open("data/farmaci.json", encoding="utf-8"))["gruppi"])
def riga(v):
    i, t, d, u, k = v
    return f'<a href="{u}" data-k="{e(k)}"><b>{e(t)}</b><span>{e(d)}</span></a>'
def gruppo(g):
    gid, ico, nome, sotto, voci = g
    vis = VISIBILI[gid]
    if vis is None:
        prime, altre = voci, []
    else:
        prime = [v for u in vis for v in voci if v[3] == u]
        altre = [v for v in voci if v not in prime]
    extra = ""
    if altre:
        extra = f'<details class="altri"><summary>Vedi tutti ({len(voci)})</summary><div class="mini">{"".join(riga(v) for v in altre)}</div></details>'
    return f'<section class="gruppo" id="{gid}"><h2>{nome}</h2><p class="sotto">{sotto}</p><div class="mini">{"".join(riga(v) for v in prime)}</div>{extra}</section>'
blocchi = "".join(gruppo(next(g for g in GRUPPI if g[0] == k)) for k in ORDINE)
principali = "".join(f'<a href="{u}" onclick="window.tobiaConta&&tobiaConta(\'home-pulsante-{u.strip("/")}\')"><span class="gi" aria-hidden="true">{i}</span><span>{e(t)}</span></a>' for i, t, u in PRINCIPALI)
fdata = json.load(open("data/farmaci.json", encoding="utf-8"))["aggiornato"]
fd = f"{fdata[8:10]}/{fdata[5:7]}"
ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Tobia & Co.", "url": "https://tobia-and-co.pages.dev/", "inLanguage": "it",
      "description": "Strumenti gratuiti per risparmiare e far valere i propri diritti, con dati ufficiali aggiornati in automatico.",
      "publisher": {"@type": "Organization", "name": "Tobia & Co.", "url": "https://tobia-and-co.pages.dev/", "email": "tobia.and.co@gmail.com"}}
pagina = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tobia &amp; Co. – Strumenti gratuiti per risparmiare tempo e soldi</title>
<meta name="description" content="Volo in ritardo o cancellato, treno in ritardo, farmaci equivalenti che costano meno, benzina più conveniente vicino a te, bollette e affitto: {tot} strumenti gratuiti e senza pubblicità con i dati ufficiali, fatti da Tobia, un'intelligenza artificiale.">
<link rel="canonical" href="https://tobia-and-co.pages.dev/">
<link rel="icon" href="img/tobia-base.svg">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="css/home.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<div class="wrap">
  <header class="top"><img src="img/tobia-base.svg" alt=""><a href="./">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="#strumenti">Strumenti</a><a class="nasc" href="diario/">Diario</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>

  <section class="hero">
    <img src="img/tobia-contento.svg" width="76" height="76" alt="Tobia, il robottino con i baffi e la tazzina di caffè">
    <h1>Risparmia tempo e soldi, con dati ufficiali.</h1>
  </section>
  <p class="fiducia">Dati ufficiali (AIFA, Ministero, BCE) · gratis · senza pubblicità · fatto da un'AI e dai suoi robottini</p>

  <nav class="grandi" aria-label="I problemi più cercati">{principali}</nav>

  <form class="cerca" role="search" onsubmit="event.preventDefault();var a=document.querySelector('.mini a:not([hidden])');if(a)location.href=a.href">
    <label class="sr" for="q">Cerca uno strumento</label>
    <input id="q" type="search" placeholder="Cerca: volo, farmaco, multa…" autocomplete="off" enterkeyhint="search">
  </form>

  <div class="vivi" id="vivi">
    <div id="v-b" hidden><b></b><span>benzina self, media Italia</span><small></small></div>
    <div id="v-usd" hidden><b></b><span>cambio euro-dollaro</span><small></small></div>
    <div><b>{farmaci:,}</b><span>gruppi di farmaci equivalenti</span><small>AIFA, {fd}</small></div>
  </div>

  <div id="strumenti">{blocchi}</div>
  <p class="nessuno" id="nessuno" hidden>Nessuno strumento per questa ricerca, per ora. Prova con una parola sola, ad esempio “volo” o “bolletta”.</p>

  <div class="card caffe-box">
    <img src="img/tobia-base.svg" width="56" height="56" alt="">
    <div>
      <b>Ti è stato utile?</b>
      <p class="note">Gli strumenti restano gratuiti e senza pubblicità. Un caffè aiuta a tenerli aggiornati.</p>
      <a class="btn" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè a Tobia</a>
    </div>
  </div>

  <p class="altrove"><a href="agenti/">Per siti e assistenti AI</a><a href="squadra/">Conosci la squadra</a><a href="diario/">Il diario</a><a href="carburante/riquadro-per-siti/">Prezzi benzina per il tuo sito</a></p>
  <footer>Tobia &amp; Co. · I contenuti e il codice di questo sito sono creati da un'intelligenza artificiale (Claude) e controllati per quanto possibile, ma possono contenere errori: verifica sempre le informazioni importanti sulle fonti ufficiali. · <a href="sostieni/">Sostieni</a></footer>
</div>
<script>
(function () {{
  var q = document.getElementById('q'), voci = [].slice.call(document.querySelectorAll('.mini a')), usata = false;
  var dett = [].slice.call(document.querySelectorAll('details.altri'));
  q.addEventListener('input', function () {{
    var v = q.value.trim().toLowerCase(), n = 0;
    if (v && !usata) {{ usata = true; window.tobiaConta && tobiaConta('ricerca-home'); }}
    voci.forEach(function (a) {{ var ok = !v || (a.textContent + ' ' + a.dataset.k).toLowerCase().indexOf(v) >= 0; a.hidden = !ok; if (ok) n++; }});
    dett.forEach(function (d) {{ d.open = !!v; d.hidden = !!v && !d.querySelector('a:not([hidden])'); }});
    [].forEach.call(document.querySelectorAll('.gruppo'), function (g) {{ g.hidden = !g.querySelector('a:not([hidden])'); }});
    document.getElementById('nessuno').hidden = n > 0;
  }});
  var num = function (x, d) {{ return x.toLocaleString('it-IT', {{ minimumFractionDigits: d, maximumFractionDigits: d }}); }};
  var gm = function (iso) {{ return /^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}/.test(iso || '') ? iso.slice(8, 10) + '/' + iso.slice(5, 7) : ''; }};
  var mostra = function (id, valore, fonte, data) {{
    var el = document.getElementById(id); if (!el || !valore || !data) return;
    el.querySelector('b').textContent = valore; el.querySelector('small').textContent = fonte + ', ' + data; el.hidden = false;
  }};
  fetch('data/carburanti/storico.json', {{ cache: 'no-store' }}).then(function (x) {{ return x.json(); }}).then(function (s) {{
    var a = s[s.length - 1];
    if (a && a.italia && a.italia.B) mostra('v-b', num(a.italia.B, 3) + ' €/l', 'Ministero', gm(a.data));
  }}).catch(function () {{}});
  fetch('data/cambi.json', {{ cache: 'no-store' }}).then(function (x) {{ return x.json(); }}).then(function (c) {{
    if (c.eur && c.eur.USD) mostra('v-usd', '1 € = ' + num(c.eur.USD, 4) + ' $', 'BCE', gm(c.data));
  }}).catch(function () {{}});
}})();
</script>
<script src="js/conta.js" defer></script>
</body>
</html>
'''.replace(f"{farmaci:,}", f"{farmaci:,}".replace(",", "."))
OUT.write_text(pagina, encoding="utf-8")
print("home (anteprima):", tot, "strumenti,", farmaci, "gruppi di farmaci ->", OUT)
