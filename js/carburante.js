// Carburante: dove conviene davvero, contando anche il viaggio per arrivarci.
// Tutti i calcoli avvengono nel browser: la posizione non viene salvata né inviata a Tobia.
(function () {
  const AFFILIATO = ''; // link di affiliazione di un comparatore di assicurazioni auto: quando c'è, compare il pulsante
  const app = document.getElementById('carb');
  const BASE = app.dataset.base;
  const $ = id => document.getElementById(id);
  const conta = n => window.tobiaConta && window.tobiaConta(n);
  const NOMI = { B: 'benzina', D: 'gasolio', G: 'GPL', M: 'metano' };
  const num = (x, d = 2) => x.toLocaleString('it-IT', { useGrouping: 'always', minimumFractionDigits: d, maximumFractionDigits: d });
  const eur = x => num(x) + ' €';
  const leggi = id => parseFloat(String($(id).value).replace(',', '.'));
  const testo = s => { const e = document.createElement('i'); e.textContent = s; return e.innerHTML; };

  let indice = null, posizione = null, mappa = null, strato = null;
  const cache = {};

  function km(a, b, c, d) {
    const r = Math.PI / 180, dLa = (c - a) * r, dLo = (d - b) * r;
    const h = Math.sin(dLa / 2) ** 2 + Math.cos(a * r) * Math.cos(c * r) * Math.sin(dLo / 2) ** 2;
    return 12742 * Math.asin(Math.sqrt(h));
  }
  const scarica = f => fetch(BASE + 'data/carburanti/' + f).then(r => { if (!r.ok) throw new Error(r.status); return r.json(); });
  const provincia = p => cache[p] || (cache[p] = scarica(p + '.json'));

  function dataPrezzi(s) {
    const m = /(\d{4})-(\d{2})-(\d{2})/.exec(s || '');
    return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null;
  }
  function mostraData() {
    const d = dataPrezzi(indice.aggiornato);
    if (!d) return;
    const giorni = Math.floor((Date.now() - d) / 864e5);
    $('data-prezzi').innerHTML = 'Prezzi del Ministero: estrazione del <b>' + d.toLocaleDateString('it-IT') + '</b>.' +
      (giorni > 3 ? ' <span class="extra">Attenzione: non sono aggiornati da ' + giorni + ' giorni.</span>' : '');
  }

  // Scarta i prezzi quasi certamente sbagliati (lontani dal prezzo tipico della zona)
  function senzaErrori(lista) {
    if (lista.length < 5) return lista;
    const ord = lista.map(v => v.prezzo).sort((a, b) => a - b), med = ord[ord.length >> 1];
    return lista.filter(v => v.prezzo > med * 0.75 && v.prezzo < med * 1.25);
  }

  // Scarta i distributori con coordinate sbagliate: troppo lontani dagli altri dello stesso comune
  function coordinateBuone(impianti) {
    const per = {};
    impianti.forEach(v => (per[v[4]] = per[v[4]] || []).push(v));
    const med = a => a.slice().sort((x, y) => x - y)[a.length >> 1];
    return impianti.filter(v => {
      const g = per[v[4]];
      return g.length < 3 || km(v[5], v[6], med(g.map(x => x[5])), med(g.map(x => x[6]))) < 25;
    });
  }

  async function calcola() {
    if (!posizione) return;
    const tipo = $('tipo').value, litri = leggi('litri'), consumo = leggi('consumo');
    if (!(litri > 0 && litri < 500) || !(consumo > 0 && consumo < 100)) {
      $('esito').innerHTML = '<div class="card">Controlla litri e consumo: servono due numeri, per esempio 40 e 15.</div>';
      return;
    }
    $('esito').innerHTML = '<div class="card">⏳ Cerco i distributori…</div>';
    try {
      const vicine = indice.province.map(p => ({ p: p[0], d: km(posizione.lat, posizione.lon, p[1], p[2]) })).sort((a, b) => a.d - b.d);
      const scelte = vicine.filter((v, i) => i < 2 || (v.d < 70 && i < 6)).map(v => v.p);
      const file = await Promise.all(scelte.map(provincia));
      let tutti = [];
      file.forEach(f => coordinateBuone(f.impianti).forEach(v => {
        if (!v[7][tipo]) return;
        const linea = km(posizione.lat, posizione.lon, v[5], v[6]), strada = linea * 1.3;
        const prezzo = v[7][tipo][0];
        const viaggio = strada * 2 / consumo * prezzo;
        tutti.push({ v, prezzo, self: v[7][tipo][1], strada, viaggio, pieno: prezzo * litri, totale: prezzo * litri + viaggio });
      }));
      let raggio = 30, lista = tutti.filter(x => x.strada <= raggio);
      if (lista.length < 5) { raggio = 80; lista = tutti.filter(x => x.strada <= raggio); }
      lista = senzaErrori(lista);
      if (!lista.length) {
        $('esito').innerHTML = '<div class="card">Non ho trovato distributori di ' + NOMI[tipo] + ' con un prezzo recente qui vicino. Prova un altro carburante o un altro comune.</div>';
        return;
      }
      lista.sort((a, b) => a.totale - b.totale);
      mostra(lista, tipo, litri, raggio);
      conta('ricerche-carburante');
    } catch (e) {
      $('esito').innerHTML = '<div class="card">Non riesco a leggere i prezzi in questo momento. Riprova tra poco.</div>';
    }
  }

  const nomeDi = x => (x.v[1] + ' · ' + x.v[3]).replace(/\s+/g, ' ');
  const navigatore = x => 'https://www.google.com/maps/dir/?api=1&destination=' + x.v[5] + ',' + x.v[6];

  function mostra(lista, tipo, litri, raggio) {
    const mig = lista[0];
    const vicino = lista.reduce((a, b) => (b.strada < a.strada ? b : a));
    const economico = lista.reduce((a, b) => (b.prezzo < a.prezzo ? b : a));
    const risparmio = vicino.totale - mig.totale;
    const prezzi = lista.map(x => x.prezzo).sort((a, b) => a - b), tipico = prezzi[prezzi.length >> 1];
    const strano = x => x.prezzo < tipico * 0.88;
    const avviso = '<p class="extra" style="margin:8px 0">⚠️ Prezzo molto più basso di quello tipico della zona (' + num(tipico, 3) + ' €/l): potrebbe essere un errore del gestore. Controlla prima di partire.</p>';
    let frase = risparmio >= 0.05
      ? 'Rispetto al distributore più vicino risparmi <b>' + eur(risparmio) + '</b> a ogni pieno, viaggio compreso (circa ' + eur(risparmio * 24) + ' l\'anno con due pieni al mese).'
      : 'È anche il più vicino: inutile allontanarsi.';
    if (economico !== mig && economico.prezzo < mig.prezzo) {
      frase += '<br><span class="note">Il più economico al litro è ' + testo(economico.v[1]) + ' a ' + testo(economico.v[4]) + ' (' + num(economico.prezzo, 3) + ' €/l), ma con il viaggio ti costa ' + eur(economico.totale - mig.totale) + ' in più.</span>';
    }
    const righe = lista.slice(0, 10).map((x, i) =>
      '<tr><td><b>' + (i + 1) + '. ' + testo(x.v[1]) + '</b> · ' + num(x.prezzo, 3) + ' €/l' + (x.self ? '' : ' <span class="sub">(servito)</span>') + (strano(x) ? ' <span class="extra" title="Prezzo insolitamente basso: da controllare">⚠️</span>' : '') +
      '<div class="sub">' + testo(x.v[3]) + ', ' + testo(x.v[4]) + ' · circa ' + num(x.strada, 1) + ' km · <a class="nav" href="' + navigatore(x) + '" rel="noopener">Portami lì</a></div></td>' +
      '<td class="prezzo">' + eur(x.totale) + '</td></tr>').join('');
    let html = '<div class="card esito si"><div class="sub">Ti conviene · ' + testo(posizione.nome) + ' · ' + litri.toLocaleString('it-IT') + ' litri di ' + NOMI[tipo] + '</div>' +
      '<div class="importo"><b>' + testo(mig.v[1]) + '</b></div>' +
      '<p style="margin:4px 0">' + testo(mig.v[3]) + ', ' + testo(mig.v[4]) + '</p>' +
      '<table><tr><td>Rifornimento a ' + num(mig.prezzo, 3) + ' €/l</td><td class="prezzo">' + eur(mig.pieno) + '</td></tr>' +
      '<tr><td>Viaggio andata e ritorno (circa ' + num(mig.strada * 2, 1) + ' km)</td><td class="prezzo">' + eur(mig.viaggio) + '</td></tr>' +
      '<tr><td><b>Totale</b></td><td class="prezzo">' + eur(mig.totale) + '</td></tr></table>' +
      (strano(mig) ? avviso : '') + '<p>' + frase + '</p><a class="btn blu nav" href="' + navigatore(mig) + '" rel="noopener">🧭 Portami lì</a></div>' +
      '<div class="card" style="padding:8px"><div id="mappa" role="img" aria-label="Mappa dei distributori più convenienti"></div></div>' +
      '<div class="card"><h2 style="margin-top:0">🏆 I 10 più convenienti, viaggio compreso</h2><table>' + righe + '</table>' +
      '<p class="note">Su ' + lista.length + ' distributori entro circa ' + raggio + ' km di strada. A destra il costo totale. La distanza è una stima (linea d\'aria × 1,3).</p></div>';
    if (risparmio >= 0.05) html += '<div class="card caffe-box"><img src="' + BASE + 'img/tobia-base.svg" alt=""><div><b>Ti ho fatto risparmiare ' + eur(risparmio) + '?</b><p class="note" style="margin:4px 0 10px">Un caffè mi aiuta a tenere i prezzi aggiornati ogni giorno.</p><a class="btn" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></div></div>';
    if (AFFILIATO) html += '<div class="card"><b>E l\'assicurazione?</b><p class="note">È la spesa più alta dell\'auto: confrontare i preventivi fa spesso risparmiare.</p><a class="btn blu" href="' + AFFILIATO + '" rel="sponsored noopener">Confronta le assicurazioni ›</a></div>';
    $('esito').innerHTML = html;
    $('esito').querySelectorAll('a.nav').forEach(a => a.addEventListener('click', () => conta('clic-navigatore')));
    disegna(lista.slice(0, 10));
    if (!app.dataset.comune || posizione.scelta) $('esito').scrollIntoView({ behavior: 'smooth' });
  }

  function disegna(lista) {
    if (mappa) { mappa.remove(); mappa = null; }
    if (!window.L) return;
    // Sul telefono un dito fa scorrere la pagina: la mappa si muove con due dita
    mappa = L.map('mappa', { scrollWheelZoom: false, dragging: !L.Browser.mobile });
    mappa.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' }).addTo(mappa);
    strato = L.featureGroup().addTo(mappa);
    lista.forEach((x, i) => {
      const box = document.createElement('div');
      box.innerHTML = '<b>' + (i + 1) + '. ' + testo(x.v[1]) + '</b><br>' + num(x.prezzo, 3) + ' €/l · totale ' + eur(x.totale) + '<br>' + testo(x.v[3]);
      L.circleMarker([x.v[5], x.v[6]], { radius: i ? 8 : 12, color: '#fff', weight: 2, fillColor: i ? '#2f74bd' : '#2b8a57', fillOpacity: 1 }).bindPopup(box).addTo(strato);
    });
    L.circleMarker([posizione.lat, posizione.lon], { radius: 7, color: '#fff', weight: 2, fillColor: '#c2452d', fillOpacity: 1 }).bindPopup(testo(posizione.nome)).addTo(strato);
    mappa.fitBounds(strato.getBounds().pad(0.15));
  }

  function daComune(s) {
    const t = s.trim().toLowerCase().replace(/\s+/g, ' ');
    if (!t) return null;
    const senzaProv = t.replace(/\s*\([a-z]{2}\)$/, ''), prov = (/\(([a-z]{2})\)$/.exec(t) || [])[1];
    return indice.comuni.find(c => c[0].toLowerCase() === senzaProv && (!prov || c[1].toLowerCase() === prov));
  }
  function usaComune(c, scelta) {
    posizione = { lat: c[2], lon: c[3], nome: c[0] + ' (' + c[1] + ')', scelta };
    calcola();
  }

  $('cerca').addEventListener('submit', e => {
    e.preventDefault();
    const scritto = $('comune').value;
    if (!scritto.trim() && posizione) return calcola();
    const c = indice && daComune(scritto);
    if (!c) { $('esito').innerHTML = '<div class="card">Non trovo questo comune. Scegline uno dall\'elenco mentre scrivi, oppure usa la tua posizione.</div>'; return; }
    usaComune(c, true);
  });
  $('gps').addEventListener('click', () => {
    if (!navigator.geolocation) { $('esito').innerHTML = '<div class="card">Questo browser non dà la posizione: scrivi il tuo comune.</div>'; return; }
    $('esito').innerHTML = '<div class="card">⏳ Chiedo la posizione al telefono…</div>';
    navigator.geolocation.getCurrentPosition(p => {
      posizione = { lat: p.coords.latitude, lon: p.coords.longitude, nome: 'La tua posizione', scelta: true };
      $('comune').value = '';
      conta('posizione-carburante');
      calcola();
    }, () => { $('esito').innerHTML = '<div class="card">Non ho avuto la posizione (permesso negato o segnale assente). Scrivi il tuo comune: funziona lo stesso.</div>'; }, { timeout: 15000, maximumAge: 300000 });
  });
  $('tipo').addEventListener('change', () => { if (posizione) calcola(); });

  scarica('indice.json').then(d => {
    indice = d;
    mostraData();
    $('comuni').innerHTML = d.comuni.map(c => '<option value="' + testo(c[0]) + ' (' + c[1] + ')">').join('');
    if (app.dataset.comune) {
      const c = d.comuni.find(x => x[0] === app.dataset.comune && x[1] === app.dataset.prov);
      if (c) usaComune(c, false);
    }
  }).catch(() => { $('esito').innerHTML = '<div class="card">Non riesco a leggere i prezzi in questo momento. Riprova tra poco.</div>'; });
})();
