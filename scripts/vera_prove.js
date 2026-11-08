// Vera prova gli strumenti come una persona vera: compila i campi con valori realistici,
// preme il pulsante e controlla che arrivi un risultato sensato, senza errori.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const radice = path.resolve(__dirname, '..');
const server = http.createServer((req, res) => {
  let f = path.join(radice, decodeURIComponent(req.url.split('?')[0]));
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end('404'); }
  const tipi = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml' };
  res.writeHead(200, { 'Content-Type': tipi[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(8812);
const B = 'http://localhost:8812/';

// strumento: [campi da compilare {selettore: valore}, testo atteso nel risultato]
const PROVE = {
  'bolletta/': [{ '#luce': '0,245', '#gas': '1,05' }, /€/],
  'mutuo/': [{ '#rata': '650', '#tasso': '4,5', '#anni': '20' }, /€/],
  'banca/': [{ '#canone': '6', '#carta': '30' }, /€/],
  'cambio/': [{ '#importo': '100', '#addebito': '95,40' }, /€/],
  'bollo/': [{ '#kw': '70' }, /Circa .* € all'anno/],
  'assegno-unico/': [{ '#isee': '15.000' }, /203,80 €/],
  'treno/': [{ '#prezzo': '59,90', '#ritardo': '75' }, /14,98 €/],
  'tasse-aeroportuali/': [{ '#data': '2026-10-20', '#tasse': '38,20' }, /38,20 €/],
  'affitto-istat/': [{ '#canone': '800', '#var': '2' }, /812,00 €/],
  'bagaglio/': [{ '#atterraggio': '2026-11-03', '#consegna': '2026-11-05', '#spese': 'Spazzolino 8,50' }, /Entro .*2026/],
};

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 375, height: 800 }, acceptDownloads: true });
  await ctx.route(/^https:\/\//, r => r.abort());   // niente servizi esterni durante le prove
  const problemi = [];
  for (const [url, [campi, atteso]] of Object.entries(PROVE)) {
    const p = await ctx.newPage(); const errori = [];
    p.on('pageerror', e => errori.push(e.message));
    await p.goto(B + url); await p.waitForTimeout(500);
    try {
      for (const [sel, val] of Object.entries(campi)) await p.fill(sel, val);
      await p.click('form button[type=submit], form button:not([type=button])');
      await p.waitForTimeout(700);
      const testo = await p.$eval('#esito', e => e.innerText);
      if (!atteso.test(testo)) problemi.push(`${url}: risultato inatteso: "${testo.replace(/\s+/g, ' ').slice(0, 90)}"`);
    } catch (e) { problemi.push(`${url}: la prova non è andata (${e.message.split('\n')[0]})`); }
    errori.forEach(m => problemi.push(`${url}: errore JavaScript: ${m}`));
    await p.close();
  }
  // calcolatore voli su una tratta pronta
  { const p = await ctx.newPage(); await p.goto(B + 'voli/roma-new-york/'); await p.waitForTimeout(1200);
    await p.$eval('#modulo', f => f.requestSubmit()); await p.waitForTimeout(700);
    const t = await p.$eval('#esito', e => e.innerText).catch(() => '');
    if (!/600 €/.test(t)) problemi.push('voli/roma-new-york/: il calcolo non dà 600 €');
    if (!(await p.$('#affiliato'))) problemi.push('voli/: manca il pulsante AirHelp dopo il calcolo');
    await p.close(); }
  // ricerca dei farmaci
  { const p = await ctx.newPage(); await p.goto(B + 'farmaci/'); await p.waitForTimeout(1500);
    await p.fill('input', 'eutirox'); await p.waitForTimeout(1200);
    if (!/Levotiroxina/i.test(await p.evaluate(() => document.body.innerText))) problemi.push('farmaci/: la ricerca di "eutirox" non trova la levotiroxina');
    await p.close(); }
  // calendari scaricabili
  for (const url of ['scadenze/', 'scatola/']) {
    const p = await ctx.newPage(); await p.goto(B + url); await p.waitForTimeout(500);
    if (url === 'scatola/') { for (const i of await p.$$('form input[type=text], form input:not([type])')) if (await i.isVisible()) await i.fill('30').catch(() => {}); }
    const scarico = p.waitForEvent('download', { timeout: 4000 }).catch(() => null);
    await p.click('form button[type=submit], form button:not([type=button])').catch(() => {});
    if (!(await scarico)) problemi.push(`${url}: il calendario non si scarica`);
    await p.close();
  }
  // ricerca della home
  { const p = await ctx.newPage(); await p.goto(B); await p.waitForTimeout(600); await p.fill('#q', 'sciopero'); await p.waitForTimeout(300);
    const v = await p.$$eval('.mini a:not([hidden]) b', a => a.map(x => x.textContent));
    if (!v.some(x => /Sciopero/.test(x))) problemi.push('home: la ricerca di "sciopero" non trova lo strumento');
    await p.close(); }
  await browser.close(); server.close();
  console.log(`Vera (prove degli strumenti): ${Object.keys(PROVE).length + 5} prove. Problemi: ${problemi.length}`);
  problemi.forEach(x => console.log(' - ' + x));
  process.exit(problemi.length ? 1 : 0);
})();
