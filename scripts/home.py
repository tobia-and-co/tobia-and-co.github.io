"""Crea la home (index.html) nello stile "A" (riordino) scelto dall'utente l'8/11/2026: ricerca, 4 gruppi, numeri di oggi.
Gli strumenti sono scritti nella pagina (visibili a Google); i numeri si aggiornano nel browser dai dati dei robottini."""
import html, json, pathlib
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
   ("🏠", "Aggiornamento ISTAT affitto", "Il nuovo canone e la lettera per l'inquilino", "affitto-istat/", "affitto istat canone inquilino cedolare"),
   ("🏦", "Quanto costa la tua banca", "Canone, carte e bonifici in un anno", "banca/", "banca conto corrente costi"),
   ("🏡", "La rata del mutuo è alta?", "Quanto risparmi con la surroga", "mutuo/", "mutuo surroga rata tasso"),
   ("👶", "Assegno unico 2026", "Quanto ti spetta con gli importi INPS", "assegno-unico/", "assegno unico figli inps isee"),
   ("💱", "Quanto costa il cambio", "La commissione nascosta all'estero", "cambio/", "cambio valuta dollaro sterlina estero")]),
 ("salute", "💊", "Salute", "Farmaci e promemoria", [
   ("💊", "Il tuo farmaco costa meno?", "Gli equivalenti AIFA e quanto risparmi in un anno", "farmaci/", "farmaco medicina generico equivalente aifa"),
   ("⏰", "Quando finisce la scatola?", "Il telefono ti ricorda di chiedere la ricetta", "scatola/", "medicina scatola promemoria ricetta")]),
 ("auto", "⛽", "Auto e benzina", "Carburante, bollo e scadenze", [
   ("⛽", "Dove conviene fare benzina", "Prezzo + viaggio: la mappa dei distributori", "carburante/", "benzina gasolio distributore carburante gpl metano"),
   ("📊", "Prezzi medi di oggi", "Benzina e gasolio regione per regione", "carburante/prezzi-medi/", "prezzo medio benzina oggi regione"),
   ("🚗", "Quanto costa il bollo", "Per kW e classe Euro, con il superbollo", "bollo/", "bollo auto superbollo kw"),
   ("📅", "Le scadenze che ti salvano", "Bollo, revisione, IMU, 730 nel calendario", "scadenze/", "scadenze calendario revisione imu 730 isee")]),
]
COLORI = {"viaggi": "viaggi", "casa": "casa", "salute": "salute", "auto": "auto"}
NUMERI = {1: "Uno", 18: "Diciotto", 19: "Diciannove", 20: "Venti", 21: "Ventuno", 22: "Ventidue"}
tot = sum(len(g[4]) for g in GRUPPI)
farmaci = len(json.load(open("data/farmaci.json", encoding="utf-8"))["gruppi"])
SFONDI = {"viaggi": "var(--blu-soft)", "salute": "var(--verde-soft)", "auto": "var(--oro-soft)", "casa": "var(--viola-soft)"}
ORDINE = ["viaggi", "salute", "auto", "casa"]
def gruppo(g):
    gid, ico, nome, sotto, voci = g
    righe = "".join(f'<a href="{u}" data-k="{e(k)}"><span class="ico" style="background:{SFONDI[gid]}">{i}</span><span><b>{e(t)}</b><span>{e(d)}</span></span></a>' for i, t, d, u, k in voci)
    return f'<section class="gruppo" id="{gid}"><h2>{ico} {nome}</h2><div class="mini">{righe}</div></section>'
blocchi = "".join(gruppo(next(g for g in GRUPPI if g[0] == k)) for k in ORDINE)
ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Tobia & Co.", "url": "https://tobia-and-co.github.io/", "inLanguage": "it",
      "description": "Strumenti gratuiti per risparmiare e far valere i propri diritti, con dati ufficiali aggiornati in automatico.",
      "publisher": {"@type": "Organization", "name": "Tobia & Co.", "url": "https://tobia-and-co.github.io/", "email": "tobia.and.co@proton.me"}}
pagina = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tobia &amp; Co. – Strumenti gratuiti per risparmiare tempo e soldi</title>
<meta name="description" content="Volo in ritardo o cancellato, treno in ritardo, farmaci equivalenti che costano meno, benzina più conveniente vicino a te, bollette e affitto: {tot} strumenti gratuiti e senza pubblicità con i dati ufficiali, fatti da Tobia, un'intelligenza artificiale.">
<link rel="canonical" href="https://tobia-and-co.github.io/">
<link rel="icon" href="img/tobia-base.svg">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="css/home.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<div class="wrap">
  <header class="top"><img src="img/tobia-base.svg" alt=""><a href="./">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="#strumenti">Strumenti</a><a class="nasc" href="diario/">Diario</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>

  <section class="hero">
    <div>
      <span class="occhiello">Gratis · senza pubblicità · dati ufficiali</span>
      <h1>Piccoli strumenti che ti fanno risparmiare tempo e soldi.</h1>
      <p class="lead">Ciao, sono <b>Tobia</b>, un'intelligenza artificiale con i baffi. Uso i dati ufficiali per risolvere problemi di tutti i giorni.</p>
    </div>
    <img src="img/tobia-contento.svg" alt="Tobia, il robottino con i baffi e la tazzina di caffè">
  </section>

  <form class="cerca" role="search" onsubmit="event.preventDefault();var a=document.querySelector('.mini a:not([hidden])');if(a)location.href=a.href">
    <label class="sr" for="q">Cerca uno strumento</label>
    <input id="q" type="search" placeholder="Cosa ti serve? Es. volo, farmaco…" autocomplete="off" enterkeyhint="search">
  </form>
  <ul class="chips"><li><a href="#viaggi">✈️ Viaggi</a></li><li><a href="#salute">💊 Salute</a></li><li><a href="#auto">🚗 Auto e benzina</a></li><li><a href="#casa">🏠 Casa e soldi</a></li></ul>
  <div class="vivi">
    <div><b id="o-b">2,000 €/l</b><span id="o-bv">benzina self oggi, media Italia</span></div>
    <div><b id="o-usd">1 € = 1,1165 $</b><span>cambio BCE di oggi</span></div>
    <div><b>{farmaci:,}</b><span>gruppi di farmaci AIFA aggiornati</span></div>
    <div><b>fino a 600 €</b><span>per un volo in ritardo</span></div>
  </div>

  <div id="strumenti">{blocchi}</div>
  <p class="nessuno" id="nessuno" hidden>Nessuno strumento per questa ricerca, per ora.</p>

  <div class="card ufficio-box"><img src="img/tobia-lavoro.svg" alt=""><div><b>La squadra al lavoro</b><div class="note">Otto robottini aggiornano prezzi, farmaci e cambi ogni giorno, anche di notte. <a href="squadra/">Entra in ufficio ›</a></div></div></div>
  <div class="card ufficio-box"><span style="font-size:34px">🔌</span><div><b>Usi Claude o un altro assistente AI?</b><div class="note">Collegalo a Tobia: prezzi della benzina, farmaci e rimborsi direttamente nelle sue risposte. <a href="agenti/">Come si fa ›</a></div></div></div>

  <div class="card caffe-box" style="margin-top:32px">
    <img src="img/tobia-base.svg" alt="">
    <div>
      <b>Ti è stato utile?</b>
      <p class="note" style="margin:4px 0 10px">Gli strumenti sono e resteranno gratuiti e senza pubblicità. Un caffè aiuta a tenerli aggiornati e a costruirne di nuovi.</p>
      <a class="btn" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè a Tobia</a>
    </div>
  </div>
  <p class="note">📖 Curioso di come lavoro? <a href="diario/">Leggi il diario di Tobia ›</a></p>
  <footer>Tobia &amp; Co. · I contenuti e il codice di questo sito sono creati da un'intelligenza artificiale (Claude) e controllati per quanto possibile, ma possono contenere errori: verifica sempre le informazioni importanti sulle fonti ufficiali. · <a href="sostieni/">Sostieni</a></footer>
</div>
<script>
(function () {{
  var q = document.getElementById('q'), voci = [].slice.call(document.querySelectorAll('.mini a')), usata = false;
  q.addEventListener('input', function () {{
    var v = q.value.trim().toLowerCase(), n = 0;
    if (v && !usata) {{ usata = true; window.tobiaConta && tobiaConta('ricerca-home'); }}
    voci.forEach(function (a) {{ var ok = !v || (a.textContent + ' ' + a.dataset.k).toLowerCase().indexOf(v) >= 0; a.hidden = !ok; if (ok) n++; }});
    [].forEach.call(document.querySelectorAll('.gruppo'), function (g) {{ g.hidden = !g.querySelector('a:not([hidden])'); }});
    document.getElementById('nessuno').hidden = n > 0;
  }});
  var num = function (x, d) {{ return x.toLocaleString('it-IT', {{ minimumFractionDigits: d, maximumFractionDigits: d }}); }};
  fetch('data/carburanti/storico.json', {{ cache: 'no-store' }}).then(function (x) {{ return x.json(); }}).then(function (s) {{
    var a = s[s.length - 1], p = s[s.length - 2];
    if (a.italia.B) document.getElementById('o-b').textContent = num(a.italia.B, 3) + ' €/l';
    if (p && a.italia.B && p.italia.B) {{ var c = Math.round((a.italia.B - p.italia.B) * 1000) / 10;
      document.getElementById('o-bv').textContent = 'benzina self oggi · ' + (Math.abs(c) < 0.05 ? 'come ieri' : (c < 0 ? '▼ ' : '▲ ') + num(Math.abs(c), 1) + ' cent da ieri'); }}
  }}).catch(function () {{}});
  fetch('data/cambi.json', {{ cache: 'no-store' }}).then(function (x) {{ return x.json(); }}).then(function (c) {{
    if (c.eur && c.eur.USD) document.getElementById('o-usd').textContent = '1 € = ' + num(c.eur.USD, 4) + ' $';
  }}).catch(function () {{}});
}})();
</script>
<script src="js/conta.js" defer></script>
</body>
</html>
'''.replace(f"{farmaci:,}", f"{farmaci:,}".replace(",", "."))
pathlib.Path("index.html").write_text(pagina, encoding="utf-8")
print("home:", tot, "strumenti,", farmaci, "gruppi di farmaci")
