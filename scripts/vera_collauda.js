// Vera la Collaudatrice: apre il sito come un telefono e cerca errori.
// Controlla: link interni rotti, errori JavaScript, pagine più larghe dello schermo,
// immagini che non si caricano, presenza del link "Home" in cima.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const radice = path.resolve(__dirname, '..');
const server = http.createServer((req, res) => {
  let f = path.join(radice, decodeURIComponent(req.url.split('?')[0]));
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end('404'); }
  const tipi = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png' };
  res.writeHead(200, { 'Content-Type': tipi[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(8811);

(async () => {
  const farmaci = fs.readdirSync(path.join(radice, 'farmaci')).filter(d => fs.statSync(path.join(radice, 'farmaci', d)).isDirectory());
  const campione = farmaci.sort(() => Math.random() - 0.5).slice(0, 15).map(d => `/farmaci/${d}/`);
  const voli = Object.values(JSON.parse(fs.readFileSync(path.join(radice, 'data/voli_testi.json'), 'utf8'))).map(t => '/' + t.percorso);
  const tratte = JSON.parse(fs.readFileSync(path.join(radice, 'data/tratte.json'), 'utf8')).sort(() => Math.random() - 0.5).slice(0, 5).map(t => '/' + t);
  const pagine = [...tratte, '/', '/scadenze/', '/farmaci/', '/diario/', '/sostieni/', '/scatola/', '/bolletta/', '/mutuo/', '/banca/', '/cambio/', '/bollo/', '/assegno-unico/', '/carburante/', '/bagaglio/', '/voli/compagnia/', '/voli/compagnia/ryanair/', '/voli/sciopero/', '/tasse-aeroportuali/', '/carburante/roma/', '/carburante/milano/', ...voli, ...campione];
  const browser = await chromium.launch();
  const problemi = [];
  for (const url of pagine) {
    const page = await browser.newPage({ viewport: { width: 375, height: 800 } });
    page.on('pageerror', e => problemi.push(`${url}: errore JavaScript: ${e.message}`));
    page.on('requestfailed', r => problemi.push(`${url}: non si carica ${r.url()}`));
    page.on('response', r => { if (r.status() >= 400 && r.url().startsWith('http://localhost')) problemi.push(`${url}: ${r.status()} per ${r.url().replace('http://localhost:8811', '')}`); });
    await page.goto('http://localhost:8811' + url, { waitUntil: 'networkidle' });
    const esito = await page.evaluate(() => ({
      larga: document.documentElement.scrollWidth > window.innerWidth + 1,
      haHome: location.pathname === '/' || !!document.querySelector('nav.briciole a'),
      link: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(h => !/^(https?:|mailto:|#)/.test(h)),
      titolo: document.title,
    }));
    if (esito.larga) problemi.push(`${url}: la pagina è più larga dello schermo del telefono`);
    if (!esito.haHome) problemi.push(`${url}: manca il link per tornare alla Home`);
    if (!esito.titolo) problemi.push(`${url}: manca il titolo`);
    for (const h of esito.link) {
      const assoluto = new URL(h, 'http://localhost:8811' + url).pathname;
      let f = path.join(radice, decodeURIComponent(assoluto));
      if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
      if (!fs.existsSync(f)) problemi.push(`${url}: link rotto verso ${h}`);
    }
    await page.close();
  }
  await browser.close(); server.close();
  const unici = [...new Set(problemi)];
  fs.writeFileSync(path.join(radice, 'data/collaudo.json'), JSON.stringify({ data: new Date().toISOString().slice(0, 10), pagine_controllate: pagine.length, problemi: unici }, null, 2));
  console.log(`Pagine controllate: ${pagine.length}. Problemi: ${unici.length}`);
  unici.forEach(p => console.log(' - ' + p));
  process.exit(unici.length ? 1 : 0);
})();
