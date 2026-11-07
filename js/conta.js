// Contatore di Tobia & Co.: conta solo numeri (visite per sezione e azioni importanti),
// senza cookie e senza dati personali (servizio gratuito Abacus, nessun account).
(function () {
  var base = 'https://abacus.jasoncameron.dev/hit/tobiaandco/';
  var locale = /localhost|127\.0\.0\.1/.test(location.hostname);
  var giaContati = {};
  // tobiaConta('nome'): conta un'azione al massimo una volta per pagina aperta
  window.tobiaConta = function (nome) {
    if (locale || giaContati[nome]) return;
    giaContati[nome] = true;
    try { fetch(base + String(nome).replace(/[^a-z0-9_-]/gi, '').slice(0, 40), { mode: 'cors', keepalive: true }).catch(function () {}); } catch (e) {}
  };
  var p = location.pathname.split('/').filter(Boolean);
  var sezione = p.length === 0 ? 'home' : (p[0] === 'farmaci' && p.length > 1 ? 'farmaci-pagine' : (p[0] === 'voli' && p[1] === 'compagnia' ? 'compagnie' : p[0] === 'voli' && p[1] === 'sciopero' ? 'sciopero' : p[0] === 'voli' && p.length > 1 ? 'tratte' : (p[0] === 'carburante' && p.length > 1 ? 'carburante-pagine' : p[0])));
  window.tobiaConta('totale');
  window.tobiaConta(sezione);
  // clic su "Offri un caffè" (Ko-fi)
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="ko-fi.com"]');
    if (a) window.tobiaConta('clic-kofi');
  });
})();
