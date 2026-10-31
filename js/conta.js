// Contatore visite di Tobia & Co.: conta solo il numero di visite per sezione,
// senza cookie e senza dati personali (servizio gratuito Abacus, nessun account).
(function () {
  try {
    if (/localhost|127\.0\.0\.1/.test(location.hostname)) return;
    var p = location.pathname.split('/').filter(Boolean);
    var sezione = p.length === 0 ? 'home' : (p[0] === 'farmaci' && p.length > 1 ? 'farmaci-pagine' : p[0]);
    var base = 'https://abacus.jasoncameron.dev/hit/tobiaandco/';
    fetch(base + 'totale', { mode: 'cors' }).catch(function () {});
    fetch(base + sezione.replace(/[^a-z0-9_-]/gi, '').slice(0, 40), { mode: 'cors' }).catch(function () {});
  } catch (e) {}
})();
