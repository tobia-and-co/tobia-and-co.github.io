"""Crea la home (index.html) nello stile "B" scelto dall'utente l'8/11/2026: ricerca, 4 gruppi, numeri di oggi.
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
def gruppo(g):
    gid, ico, nome, sotto, voci = g
    righe = "".join(f'<a class="voce" href="{u}" data-k="{e(k)}"><span class="i">{i}</span><span><b>{e(t)}</b><small>{e(d)}</small></span><span class="f" aria-hidden="true">›</span></a>' for i, t, d, u, k in voci)
    return f'<section class="gruppo" id="{gid}" style="--c:var(--{gid});--cc:var(--{gid}-chiaro)"><header><div class="bollo">{ico}</div><div><h3>{nome}</h3><span>{sotto}</span></div></header>{righe}</section>'
col1 = gruppo(GRUPPI[0]) + gruppo(GRUPPI[2]); col2 = gruppo(GRUPPI[1]) + gruppo(GRUPPI[3])
ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Tobia & Co.", "url": "https://tobia-and-co.github.io/", "inLanguage": "it",
      "description": "Strumenti gratuiti per risparmiare e far valere i propri diritti, con dati ufficiali aggiornati in automatico.",
      "publisher": {"@type": "Organization", "name": "Tobia & Co.", "url": "https://tobia-and-co.github.io/", "email": "tobia.and.co@proton.me"}}
pagina = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tobia &amp; Co. – Rimborsi, farmaci e benzina: strumenti gratuiti con dati ufficiali</title>
<meta name="description" content="Volo in ritardo o cancellato, treno in ritardo, farmaci equivalenti che costano meno, benzina più conveniente vicino a te, bollette e affitto: {tot} strumenti gratuiti e senza pubblicità con i dati ufficiali, fatti da Tobia, un'intelligenza artificiale.">
<link rel="canonical" href="https://tobia-and-co.github.io/">
<link rel="icon" href="img/tobia-base.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700;9..144,800&amp;family=Inter:wght@400;500;600;700&amp;display=swap">
<link rel="stylesheet" href="css/home.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<div class="barra"><div class="wrap">
  <a class="logo" href="./"><img src="img/tobia-base.svg" alt="">Tobia &amp; Co.</a>
  <nav class="menu"><a href="#viaggi">Viaggi</a><a href="#salute">Salute</a><a href="#auto">Auto</a><a href="#casa">Casa e soldi</a><a href="diario/">Diario</a></nav>
  <a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a>
</div></div>

<main class="wrap">
  <section class="copertina">
    <div>
      <span class="occhiello">Gratis · dati ufficiali</span>
      <h1>Ti spetta più di quanto <em>pensi</em>.</h1>
      <p class="sotto">Rimborsi per voli e treni in ritardo, farmaci che costano meno, la benzina più conveniente vicino a te. Ciao, sono <b>Tobia</b>: faccio i conti con i dati ufficiali, tu risparmi.</p>
      <form class="cerca" role="search" onsubmit="event.preventDefault();var a=document.querySelector('#ris a');if(a)location.href=a.href">
        <label class="sr" for="q">Cerca uno strumento</label>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#5B6775" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input id="q" type="search" placeholder="Cosa ti serve?" autocomplete="off" enterkeyhint="search">
        <button>Cerca</button>
        <div class="risultati" id="ris" aria-live="polite"></div>
      </form>
      <div class="suggeriti"><a href="voli/">✈️ Volo in ritardo</a><a href="farmaci/">💊 Farmaco generico</a><a href="carburante/">⛽ Benzina oggi</a><a href="treno/">🚆 Treno in ritardo</a></div>
    </div>
    <div class="scena" aria-hidden="true">
      <div class="sole"></div>
      <svg class="citta" viewBox="0 0 400 120" preserveAspectRatio="xMidYMax meet">
        <g fill="#8FB3CC"><rect x="0" y="62" width="34" height="58"/><rect x="38" y="44" width="26" height="76"/><rect x="300" y="54" width="30" height="66"/><rect x="334" y="40" width="22" height="80"/><rect x="360" y="66" width="40" height="54"/></g>
        <g fill="#7AA2BE"><path d="M70 120V58a40 40 0 0 1 80 0v62z"/>
          <g fill="#BFE0F3"><path d="M80 120V90a7 7 0 0 1 14 0v30zM98 120V90a7 7 0 0 1 14 0v30zM116 120V90a7 7 0 0 1 14 0v30zM134 120V90a7 7 0 0 1 10 0v30z"/><path d="M84 76a6 6 0 0 1 12 0v6H84zM102 76a6 6 0 0 1 12 0v6h-12zM120 76a6 6 0 0 1 12 0v6h-12z"/></g>
          <rect x="196" y="72" width="88" height="48"/><path d="M206 72a34 34 0 0 1 68 0z"/><rect x="236" y="22" width="8" height="18"/><circle cx="240" cy="20" r="5"/><rect x="230" y="34" width="20" height="8" rx="3"/><rect x="160" y="80" width="30" height="40"/></g>
      </svg>
      <div class="fumetto">Volo Roma–Barcellona cancellato? Ti spettano <b>250 €</b> a testa.</div>
      <img class="amico a1" src="img/tobia-base.svg" alt="">
      <img class="tobia" src="img/tobia-contento.svg" alt="">
      <img class="amico a2" src="img/tobia-pensieroso.svg" alt="">
    </div>
  </section>

  <p class="nota-oggi">Aggiornato dai robottini · <a href="carburante/prezzi-medi/">tutti i prezzi di oggi ›</a></p>
  <div class="oggi">
    <div><small>⛽ Benzina self</small><b id="o-b">2,000 €/l</b><span id="o-bv">media Italia</span></div>
    <div><small>🛢️ Gasolio self</small><b id="o-d">2,226 €/l</b><span id="o-dv">media Italia</span></div>
    <div><small>💱 Euro/dollaro</small><b id="o-usd">1,1165 $</b><span>cambio ufficiale BCE</span></div>
    <div><small>💊 Farmaci</small><b>{farmaci:,}</b><span>gruppi AIFA</span></div>
  </div>

  <h2 id="strumenti">Cosa ti serve oggi?</h2>
  <p class="intro">{NUMERI.get(tot, str(tot))} strumenti gratuiti, divisi in quattro. Nessuna registrazione: i dati restano sul tuo telefono.</p>
  <div class="gruppi"><div class="colonna">{col1}</div><div class="colonna">{col2}</div></div>

  <section class="primo">
    <div>
      <small>In primo piano · scioperi d'autunno</small>
      <h3>Volo cancellato per sciopero? Spesso ti spetta lo stesso.</h3>
      <p>Se a scioperare è il personale della compagnia, la Corte di giustizia UE dice che la compensazione è dovuta. Ti spiego quando, e ti preparo la richiesta.</p>
      <a class="btn" href="voli/sciopero/">Scopri se ti spetta ›</a>
    </div>
    <div class="grande">600 €<span>il massimo a persona</span></div>
  </section>

  <section class="squadra">
    <div class="facce"><img src="img/tobia-lavoro.svg" alt=""><img class="r-rita" src="img/tobia-base.svg" alt=""><img class="r-benny" src="img/tobia-base.svg" alt=""><img class="r-carlo" src="img/tobia-lavoro.svg" alt=""><img class="r-pino" src="img/tobia-pensieroso.svg" alt=""><img class="r-vera" src="img/tobia-contento.svg" alt=""></div>
    <div><b>Una squadra che non dorme mai</b><p>Otto robottini aggiornano prezzi, farmaci e cambi ogni giorno, anche di notte.</p></div>
    <a class="btn2" href="squadra/">Entra in ufficio ›</a>
  </section>

  <div class="promesse">
    <div><b>🔓 Nessuna registrazione</b>Apri lo strumento e lo usi. Niente account, niente app.</div>
    <div><b>📱 I tuoi dati restano a te</b>I calcoli si fanno sul tuo telefono: non salviamo niente.</div>
    <div><b>🤖 Fatto da un'AI, con onestà</b>Tobia è un'intelligenza artificiale: verifica sempre le informazioni importanti.</div>
  </div>
  <div class="fonti"><b>Dati ufficiali da</b><span>AIFA</span><span>BCE</span><span>Ministero delle Imprese</span><span>INPS</span><span>GME</span><span>Banca d'Italia</span></div>

  <footer><span>© Tobia &amp; Co. · strumenti gratuiti creati da Tobia, un'intelligenza artificiale (Claude). Possono contenere errori: verifica sempre sulle fonti ufficiali.</span><span><a href="diario/">Diario</a> · <a href="squadra/">L'ufficio</a> · <a href="agenti/">Per gli assistenti AI</a> · <a href="sostieni/">Sostieni</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></span></footer>
</main>

<script>
(function () {{
  var q = document.getElementById('q'), r = document.getElementById('ris');
  var voci = [].slice.call(document.querySelectorAll('.voce')), usata = false;
  q.addEventListener('input', function () {{
    var v = q.value.trim().toLowerCase();
    if (!v) {{ r.style.display = 'none'; return; }}
    if (!usata) {{ usata = true; window.tobiaConta && tobiaConta('ricerca-home'); }}
    var trovate = voci.filter(function (a) {{ return (a.textContent + ' ' + a.dataset.k).toLowerCase().indexOf(v) >= 0; }}).slice(0, 5);
    r.innerHTML = trovate.length ? trovate.map(function (a) {{ return '<a href="' + a.getAttribute('href') + '"><span style="font-size:22px">' + a.querySelector('.i').textContent + '</span><span><b>' + a.querySelector('b').textContent + '</b><small>' + a.querySelector('small').textContent + '</small></span></a>'; }}).join('') : '<div style="padding:12px;color:var(--grigio)">Nessuno strumento per questa ricerca, per ora.</div>';
    r.style.display = 'block';
  }});
  document.addEventListener('click', function (ev) {{ if (!ev.target.closest('.cerca')) r.style.display = 'none'; }});
  var num = function (x, d) {{ return x.toLocaleString('it-IT', {{ minimumFractionDigits: d, maximumFractionDigits: d }}); }};
  function variazione(id, oggi, ieri) {{
    if (oggi == null || ieri == null) return;
    var c = Math.round((oggi - ieri) * 1000) / 10, el = document.getElementById(id);
    if (Math.abs(c) < 0.05) el.textContent = 'come ieri';
    else el.innerHTML = '<span class="' + (c < 0 ? 'giu' : 'su') + '">' + (c < 0 ? '▼ ' : '▲ ') + num(Math.abs(c), 1) + ' cent</span> da ieri';
  }}
  fetch('data/carburanti/storico.json', {{ cache: 'no-store' }}).then(function (x) {{ return x.json(); }}).then(function (s) {{
    var a = s[s.length - 1], p = s[s.length - 2];
    if (a.italia.B) document.getElementById('o-b').textContent = num(a.italia.B, 3) + ' €/l';
    if (a.italia.D) document.getElementById('o-d').textContent = num(a.italia.D, 3) + ' €/l';
    if (p) {{ variazione('o-bv', a.italia.B, p.italia.B); variazione('o-dv', a.italia.D, p.italia.D); }}
  }}).catch(function () {{}});
  fetch('data/cambi.json', {{ cache: 'no-store' }}).then(function (x) {{ return x.json(); }}).then(function (c) {{
    if (c.eur && c.eur.USD) document.getElementById('o-usd').textContent = num(c.eur.USD, 4) + ' $';
  }}).catch(function () {{}});
}})();
</script>
<script src="js/conta.js" defer></script>
</body>
</html>
'''.replace(f"{farmaci:,}", f"{farmaci:,}".replace(",", "."))
pathlib.Path("index.html").write_text(pagina, encoding="utf-8")
print("home:", tot, "strumenti,", farmaci, "gruppi di farmaci")
