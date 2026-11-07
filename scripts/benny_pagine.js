// Benny il Benzinaio: crea carburante/index.html e una pagina per la città principale di ogni provincia,
// e aggiunge gli indirizzi a sitemap.xml. I prezzi non stanno nelle pagine: li legge il browser da
// data/carburanti/, così restano aggiornati senza rifarle. Da rilanciare solo se cambia questo modello.
const fs = require('fs'), path = require('path');
const radice = path.resolve(__dirname, '..');
const SITO = 'https://tobia-and-co.github.io', OUT = path.join(radice, 'carburante');
const slug = s => s.normalize('NFKD').replace(/[^\x00-\x7f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const pagina = ({ base, titolo, descr, canonica, briciole, h1, lead, attr, extra }) => `<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${titolo} | Tobia &amp; Co.</title>
<meta name="description" content="${descr}">
<link rel="canonical" href="${canonica}">
<link rel="icon" href="${base}img/tobia-base.svg">
<link rel="stylesheet" href="${base}style.css">
<link rel="stylesheet" href="${base}carburante/leaflet/leaflet.css">
</head>
<body>
<div class="wrap">
  <header class="top"><img src="${base}img/tobia-base.svg" alt=""><a href="${base}">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="${base}#strumenti">Strumenti</a><a class="nasc" href="${base}diario/">Diario</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>
  <nav class="briciole">${briciole}</nav>
  <span class="occhiello">Prezzi ufficiali del Ministero</span>
  <h1>${h1}</h1>
  <p class="lead">${lead}</p>

  <form class="card" id="cerca" autocomplete="off">
    <p style="margin-top:0"><button type="button" id="gps">📍 Usa la mia posizione</button></p>
    <label for="comune">Oppure scrivi dove sei: via, paese o comune</label>
    <input id="comune" type="text" list="comuni" placeholder="Es. Via Tuscolana 100, Roma" enterkeyhint="search" autocomplete="street-address"><datalist id="comuni"></datalist>
    <p class="note" id="stato-pos" role="status" hidden style="margin:8px 0 0"></p>
    <label for="tipo">Carburante</label>
    <select id="tipo"><option value="B">Benzina</option><option value="D">Gasolio</option><option value="G">GPL</option><option value="M">Metano</option></select>
    <div class="riga-due">
      <div><label for="litri">Litri (kg per il metano)</label><input id="litri" type="text" inputmode="decimal" value="40"></div>
      <div><label for="consumo">La tua auto: km con un litro</label><input id="consumo" type="text" inputmode="decimal" value="15"></div>
    </div>
    <p style="margin:20px 0 0"><button type="submit">⛽ Trova dove conviene</button></p>
    <p class="note" id="data-prezzi" style="margin-bottom:0"></p>
  </form>
  <div id="esito" aria-live="polite"></div>
  <div id="carb" ${attr}></div>

${extra}  <div class="card">
    <h2 style="margin-top:0">ℹ️ Come faccio il conto</h2>
    <p>Il prezzo più basso non è sempre il più conveniente: se devi fare molta strada, il risparmio se ne va nel viaggio. Per ogni distributore sommo il <b>costo del rifornimento</b> e il <b>carburante per andarci e tornare</b>, come se ci andassi apposta, poi metto tutto in classifica.</p>
    <p>La distanza è una stima: la linea d'aria moltiplicata per 1,3. A parità di prezzo preferisco il self service. I prezzi sono quelli comunicati dai gestori al Ministero: possono essere cambiati nel frattempo, controlla sempre alla pompa.</p>
    <p class="note">La tua posizione serve solo a fare il conto qui sul telefono: Tobia non la salva e non la riceve. Se scrivi una via, la cerco sulla mappa di OpenStreetMap. Per disegnare la mappa il browser scarica le immagini da OpenStreetMap, e «Portami lì» apre Google Maps.</p>
    <p class="note">Fonte dei prezzi: Ministero delle Imprese e del Made in Italy (Osservaprezzi carburanti). Mappa: © OpenStreetMap, con Leaflet. Strumento creato da Tobia, un'intelligenza artificiale (Claude): stima indicativa, non un sito ufficiale.</p>
  </div>

  <footer><a href="${base}">← Tutti gli strumenti</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ti è stato utile? Offri un caffè</a></footer>
</div>
<script src="${base}carburante/leaflet/leaflet.js"></script>
<script src="${base}js/carburante.js"></script>
<script src="${base}js/conta.js" defer></script>
</body>
</html>
`;

const indice = JSON.parse(fs.readFileSync(path.join(radice, 'data/carburanti/indice.json'), 'utf8'));
const citta = new Map();
// Per ogni provincia il comune con più distributori (l'elenco è già ordinato dal più grande)
for (const [nome, prov, , , quanti] of indice.comuni) if (prov !== 'XX' && !citta.has(prov)) citta.set(prov, { nome, prov, quanti });
const elenco = [...citta.values()].sort((a, b) => slug(a.nome).localeCompare(slug(b.nome)));

for (const d of fs.readdirSync(OUT, { withFileTypes: true }))
  if (d.isDirectory() && d.name !== 'leaflet') fs.rmSync(path.join(OUT, d.name), { recursive: true });

const collegamenti = elenco.map(c => `<a href="${slug(c.nome)}/">${esc(c.nome)}</a>`).join(' · ');
fs.writeFileSync(path.join(OUT, 'index.html'), pagina({
  base: '../',
  titolo: 'Dove conviene fare benzina? Prezzi e mappa, viaggio compreso',
  descr: 'Il distributore più vicino o il più economico? Con i prezzi ufficiali del Ministero calcolo quanto spendi davvero, contando anche il viaggio per arrivarci. Benzina, gasolio, GPL e metano. Gratis.',
  canonica: SITO + '/carburante/',
  briciole: '<a href="../">🏠 Home</a> › Carburante',
  h1: '⛽ Dove ti conviene davvero fare benzina?',
  lead: 'Il distributore più economico può costarti di più, se è lontano. Io conto <b>prezzo e viaggio insieme</b> e ti dico dove andare.',
  attr: 'data-base="../"',
  extra: `  <p><a class="btn chiaro" href="prezzi-medi/">📊 Prezzi medi di oggi, regione per regione ›</a></p>\n  <div class="card">\n    <h2 style="margin-top:0">📍 Prezzi nelle città</h2>\n    <p>${collegamenti}</p>\n  </div>\n\n`,
}));

for (const { nome, prov, quanti } of elenco) {
  const n = esc(nome), s = slug(nome);
  fs.mkdirSync(path.join(OUT, s));
  fs.writeFileSync(path.join(OUT, s, 'index.html'), pagina({
    base: '../../',
    titolo: `Benzina a ${n}: dove conviene oggi, viaggio compreso`,
    descr: `Prezzi ufficiali di benzina, gasolio, GPL e metano a ${n} (${prov}) e dintorni: la classifica dei distributori per costo totale, contando anche il viaggio per arrivarci. Gratis.`,
    canonica: `${SITO}/carburante/${s}/`,
    briciole: `<a href="../../">🏠 Home</a> › <a href="../">Carburante</a> › ${n}`,
    h1: `⛽ Benzina a ${n}: dove conviene oggi`,
    lead: `La classifica parte dal centro di ${n} (${prov}), con circa ${quanti} distributori nel comune. Usa la tua posizione o cambia comune per un conto più preciso.`,
    attr: `data-base="../../" data-comune="${n}" data-prov="${prov}"`,
    extra: '',
  }));
}

// Sitemap: Rita la riscrive con le stesse pagine; qui si aggiungono subito
const fSm = path.join(radice, 'sitemap.xml');
const oggi = new Date().toISOString().slice(0, 10);
const nuove = [SITO + '/carburante/', ...elenco.map(c => `${SITO}/carburante/${slug(c.nome)}/`)];
const sm = fs.readFileSync(fSm, 'utf8').split('\n').filter(r => !r.includes('/carburante/'));
const fine = sm.findIndex(r => r.includes('</urlset>'));
sm.splice(fine, 0, ...nuove.map(u => `<url><loc>${u}</loc><lastmod>${oggi}</lastmod></url>`));
fs.writeFileSync(fSm, sm.join('\n'));
console.log(elenco.length, 'pagine città create');
