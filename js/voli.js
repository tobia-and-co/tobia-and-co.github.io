// Calcolatore della compensazione per voli in ritardo (Reg. UE 261/2004 e UK261).
// Usa window.T (testi nella lingua della pagina) e window.BASE (percorso verso la radice del sito).
(function () {
  var UE = 'AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE IS NO CH LI GP MQ GF RE YT MF'.split(' ');
  // Programma di affiliazione AirHelp (approvato il 6/11/2026): link nella lingua della pagina, codice affiliato "tobiaandco".
  var LINGUA = (document.documentElement.lang || 'it').slice(0, 2);
  var AH_PAGINA = { it: 'https://www.airhelp.it/' }[LINGUA] || 'https://www.airhelp.com/en-int/';
  var AFFILIATO = AH_PAGINA + '?utm_medium=affiliate&utm_source=pap&utm_campaign=aff-tobiaandco&utm_content=voli-' + LINGUA + '&a_aid=tobiaandco';
  var AVVISO_AFF = {
    it: 'Link di affiliazione: se AirHelp vince la tua pratica ricevo una piccola commissione da loro. A te non costa nulla in più, e puoi sempre fare la richiesta da solo, gratis, con la lettera qui sopra.',
    en: 'Affiliate link: if AirHelp wins your claim, they pay me a small commission. It costs you nothing extra, and you can always claim yourself for free with the letter above.',
    es: 'Enlace de afiliado: si AirHelp gana tu reclamación, me paga una pequeña comisión. A ti no te cuesta nada más, y siempre puedes reclamar tú mismo gratis con la carta de arriba.',
    fr: "Lien d'affiliation : si AirHelp gagne votre dossier, ils me versent une petite commission. Cela ne vous coûte rien de plus, et vous pouvez toujours réclamer vous-même gratuitement avec la lettre ci-dessus.",
    de: 'Affiliate-Link: Wenn AirHelp Ihren Fall gewinnt, erhalte ich eine kleine Provision. Für Sie entstehen keine Mehrkosten, und Sie können immer selbst kostenlos mit dem Brief oben fordern.'
  }[LINGUA] || '';
  var T = window.T, A = [], scelto = { da: null, a: null };
  var $ = function (id) { return document.getElementById(id); };
  var norm = function (s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
  var h = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var nome = function (a) { return (a[2] ? a[2] + ' · ' : '') + a[1] + ' (' + a[0] + ')'; };

  // nomi delle città nelle altre lingue (i dati sono in inglese)
  var ALIAS = {
    rome: 'roma rom', milan: 'milano milán mailand', naples: 'napoli nápoles neapel', venice: 'venezia venecia venise venedig',
    florence: 'firenze florencia florenz', turin: 'torino turín', genoa: 'genova génova gênes genua', london: 'londra londres',
    paris: 'parigi parís', munich: 'monaco monaco di baviera múnich münchen', lisbon: 'lisbona lisboa lisbonne lissabon',
    athens: 'atene atenas athènes athen', warsaw: 'varsavia varsovia varsovie warschau', prague: 'praga prag',
    copenhagen: 'copenaghen copenhague kopenhagen', moscow: 'mosca moscú moscou moskau', barcelona: 'barcellona barcelone',
    seville: 'siviglia sevilla séville', frankfurt: 'francoforte fráncfort francfort', cologne: 'colonia köln',
    zurich: 'zurigo zúrich zürich', geneva: 'ginevra ginebra genève genf', berlin: 'berlino berlín', hamburg: 'amburgo hamburgo hambourg',
    stockholm: 'stoccolma estocolmo', edinburgh: 'edimburgo édimbourg', dublin: 'dublino dublín', krakow: 'cracovia cracovie krakau',
    bucharest: 'bucarest bukarest', brussels: 'bruxelles bruselas brüssel', vienna: 'viena vienne wien', 'new york': 'nuova york nueva york',
    cairo: 'il cairo le caire kairo', istanbul: 'istanbul estambul', tunis: 'tunisi túnez', marrakesh: 'marrakech marrakesch',
    'the hague': 'l aia la haya', antwerp: 'anversa amberes anvers', bologna: 'bolonia bologne', palermo: 'palerme', catania: 'catane',
    bari: '', cagliari: '', pisa: 'pise', verona: 'vérone', bergamo: 'orio al serio', trieste: '', lamezia: 'lamezia terme'
  };
  var alias = function (testo) { var c = ' ' + norm(testo).replace(/[^a-z0-9]+/g, ' ') + ' ', x = []; for (var k in ALIAS) if (c.indexOf(' ' + k + ' ') >= 0) x.push(ALIAS[k]); return norm(x.join(' ')); };

  fetch(window.BASE + 'data/aeroporti.json').then(function (r) { return r.json(); }).then(function (d) {
    A = d.map(function (a) { a.c = ' ' + (norm(a[2]) + ' ' + alias(a[2] + ' ' + a[1])).replace(/[^a-z0-9]+/g, ' ') + ' '; a.k = norm(a[0] + ' ' + a[1] + ' ' + a[2]) + a.c; return a; });
    precompila();
  });

  function cerca(campo) {
    var input = $(campo), lista = $(campo + '-lista');
    input.addEventListener('input', function () {
      scelto[campo] = null;
      var v = norm(input.value.trim());
      if (v.length < 2 || !A.length) { lista.innerHTML = ''; return; }
      var parole = v.split(/\s+/);
      var esatti = A.filter(function (a) { return norm(a[0]) === v; });
      var altri = A.filter(function (a) { return norm(a[0]) !== v && parole.every(function (p) { return a.k.indexOf(p) >= 0; }); });
      // prima le città il cui nome (o traduzione) comincia con la parola cercata
      var citta = function (a) { return a.c.indexOf(' ' + parole[0]) >= 0 ? 0 : 1; };
      altri.sort(function (x, y) { return citta(x) - citta(y) || y[6] - x[6]; });
      var tutti = esatti.concat(altri).slice(0, 7);
      lista.innerHTML = tutti.length ? tutti.map(function (a, i) {
        return '<button type="button" class="scelta" data-i="' + A.indexOf(a) + '">' + h(nome(a)) + '</button>';
      }).join('') : '<div class="note">' + h(T.nessuno) + '</div>';
    });
    lista.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      scelto[campo] = A[+b.dataset.i]; input.value = nome(scelto[campo]); lista.innerHTML = '';
    });
  }
  cerca('da'); cerca('a');
  // pagine delle tratte: aeroporti già scelti
  function precompila() {
    if (!A.length) return;
    var Q = {}; try { new URLSearchParams(location.search).forEach(function (v, k) { Q[k.toLowerCase()] = v; }); } catch (e) {}
    var cod = function (v) { return /^[a-z]{3}$/i.test(v || '') ? v.toUpperCase() : null; };
    var trova = function (c) { return c && A.filter(function (a) { return a[0] === c; })[0]; };
    var cerca = [trova(cod(Q.da)), trova(cod(Q.a))];
    var daLink = !!(cerca[0] && cerca[1]);
    if (window.PREFILL || daLink) ['da', 'a'].forEach(function (c, i) {
      var x = daLink ? cerca[i] : A.filter(function (a) { return a[0] === window.PREFILL[i]; })[0];
      if (x) { scelto[c] = x; $(c).value = nome(x); }
    });
    if (!daLink) return;
    // link diretto (per assistenti AI): campi opzionali e calcolo subito
    [['evento', 'evento'], ['ritardo', 'ritardo'], ['causa', 'causa']].forEach(function (p) {
      var v = (Q[p[0]] || '').toLowerCase(), sel = $(p[1]);
      if (v && Array.prototype.some.call(sel.options, function (o) { return o.value === v; })) sel.value = v;
    });
    aggiornaCampi();
    window.tobiaLinkAgenti();
    $('modulo').requestSubmit();
  }
  window.tobiaLinkAgenti = function () { var n = 0; (function p() { if (window.tobiaConta) tobiaConta('link-agenti'); else if (n++ < 30) setTimeout(p, 200); })(); };

  function km(p, q) {
    var R = 6371, r = Math.PI / 180, dLat = (q[4] - p[4]) * r, dLon = (q[5] - p[5]) * r;
    var x = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(p[4] * r) * Math.cos(q[4] * r) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return Math.round(2 * R * Math.asin(Math.sqrt(x)));
  }

  function aggiornaCampi() {
    var ev = $('evento').value;
    $('box-ritardo').hidden = ev !== 'ritardo';
    $('box-avviso').hidden = ev !== 'cancellato';
  }
  $('evento').addEventListener('change', aggiornaCampi); aggiornaCampi();

  $('modulo').addEventListener('submit', function (e) {
    e.preventDefault();
    var da = scelto.da, a = scelto.a, out = $('esito');
    if (!da || !a) { out.innerHTML = '<div class="card">' + h(T.scegli) + '</div>'; return; }
    window.tobiaConta && tobiaConta('calcoli-voli');
    var ue = $('ue').checked, ev = $('evento').value, rit = $('ritardo').value, avv = $('avviso').value, causa = $('causa').value;
    var daUE = UE.indexOf(da[3]) >= 0, aUE = UE.indexOf(a[3]) >= 0, daUK = da[3] === 'GB', aUK = a[3] === 'GB';
    var regola = daUE || (aUE && ue) ? 'ue' : (daUK || (aUK && ue) ? 'uk' : null);
    var d = km(da, a), intra = daUE && aUE;
    var fascia = d <= 1500 ? 0 : (d <= 3500 || (regola === 'ue' && intra) ? 1 : 2);
    var importi = regola === 'uk' ? ['£220', '£350', '£520'] : ['250 €', '400 €', '600 €'];
    var metaImporti = regola === 'uk' ? '£260' : '300 €';
    var importo = importi[fascia], note = [], spetta = true;

    if (!regola) { spetta = false; note.push(T.no_regola); }
    else if (ev === 'ritardo') {
      if (rit === '0' || rit === '2') { spetta = false; note.push(T.no_ritardo); }
      else if (rit === '3' && fascia === 2) { importo = metaImporti; note.push(T.meta); }
    } else if (ev === 'cancellato') {
      if (avv === '14') { spetta = false; note.push(T.no_avviso); } else note.push(T.forse_avviso);
    }
    if (spetta && ev !== 'negato' && ['meteo', 'atc', 'sicurezza'].indexOf(causa) >= 0) note.push(T.forse_causa);
    if (regola === 'uk') note.unshift(T.uk);
    if (regola) note.push(T.extra);

    var html = '<div class="card esito ' + (spetta ? 'si' : 'no') + '">' +
      '<div class="sub">' + h(da[0]) + ' → ' + h(a[0]) + ' · ' + h(T.km) + ': ' + d.toLocaleString(document.documentElement.lang) + ' km</div>' +
      (spetta ? '<div class="importo">' + h(T.spetta) + ' <b>' + h(importo) + '</b></div><div class="sub">' + h(T.a_persona) + '</div>' : '') +
      '<ul>' + note.map(function (n) { return '<li>' + h(n) + '</li>'; }).join('') + '</ul></div>';

    if (spetta) {
      var lettera = T.lettera.replace('{DA}', nome(da)).replace('{A}', nome(a)).replace('{IMPORTO}', importo)
        .replace('{EVENTO}', T['l_' + ev]);
      html += '<div class="card"><h2 style="margin-top:0;font-size:20px">' + h(T.come_t) + '</h2><ol class="passi-lista"><li>' + h(T.passo1) +
        '</li><li>' + h(T.passo2) + '</li><li>' + h(T.passo3) + '</li></ol>' +
        '<h3>' + h(T.lettera_t) + '</h3><pre id="lettera">' + h(lettera) + '</pre>' +
        '<button type="button" id="copia">' + h(T.copia) + '</button></div>';
      if (AFFILIATO) html += '<div class="card caffe-box"><div><b>' + h(T.affiliato_t) + '</b><p class="note">' + h(T.affiliato_p) +
        '</p><a class="btn blu" id="affiliato" href="' + AFFILIATO + '" rel="sponsored noopener">' + h(T.affiliato_b) + '</a><p class="note" style="margin:10px 0 0">' + h(AVVISO_AFF) + '</p></div></div>';
    }
    out.innerHTML = html;
    out.scrollIntoView({ behavior: 'smooth', block: 'start' });
    var c = $('copia');
    if (c) c.onclick = function () {
      var testo = $('lettera').textContent;
      (navigator.clipboard ? navigator.clipboard.writeText(testo) : Promise.reject()).then(function () { c.textContent = T.copiato; }, function () {
        var r = document.createRange(); r.selectNodeContents($('lettera')); getSelection().removeAllRanges(); getSelection().addRange(r);
      });
      window.tobiaConta && tobiaConta('lettere-voli');
    };
    var af = $('affiliato'); if (af) af.onclick = function () { window.tobiaConta && tobiaConta('clic-affiliato-voli'); };
  });
})();
