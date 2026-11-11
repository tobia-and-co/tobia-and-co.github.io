// Contatore di Tobia & Co.: conta solo numeri (visite per sezione e azioni importanti),
// senza cookie e senza dati personali (servizio gratuito Abacus, nessun account).
(function () {
  // il sito si è spostato su Cloudflare: chi arriva dal vecchio indirizzo va alla stessa pagina sul nuovo
  if (location.hostname === 'tobia-and-co.github.io') { location.replace('https://tobia-and-co.pages.dev' + location.pathname + location.search + location.hash); return; }
  var base = 'https://abacus.jasoncameron.dev/hit/tobiaandco/';
  var locale = /localhost|127\.0\.0\.1/.test(location.hostname);
  // le visite del proprietario non si contano: basta aprire una volta una pagina con ?io=1 (si annulla con ?io=0)
  try {
    if (/[?&]io=1/.test(location.search)) localStorage.setItem('tobia-io', '1');
    if (/[?&]io=0/.test(location.search)) localStorage.removeItem('tobia-io');
    if (localStorage.getItem('tobia-io')) locale = true;
  } catch (e) {}
  var giaContati = {};
  // tobiaConta('nome'): conta un'azione al massimo una volta per pagina aperta
  window.tobiaConta = function (nome) {
    if (locale || giaContati[nome]) return;
    giaContati[nome] = true;
    try { fetch(base + String(nome).replace(/[^a-z0-9_-]/gi, '').slice(0, 40), { mode: 'cors', keepalive: true }).catch(function () {}); } catch (e) {}
  };
  var p = location.pathname.split('/').filter(Boolean);
  var sezione = p.length === 0 ? 'home' : (p[0] === 'farmaci' && p.length > 1 ? 'farmaci-pagine' : (p[0] === 'guide' && p.length > 1 ? 'guide-' + p[1] : p[0] === 'voli' && p[1] === 'compagnia' ? 'compagnie' : p[0] === 'voli' && p[1] === 'aeroporto' ? 'aeroporti' : p[0] === 'voli' && /^(sciopero|overbooking|coincidenza-persa|volo-cancellato)$/.test(p[1] || '') ? p[1] : p[0] === 'voli' && p.length > 1 ? 'tratte' : (p[0] === 'carburante' && p[1] === 'prezzi-medi' ? 'prezzi-medi' : p[0] === 'carburante' && p.length > 1 ? 'carburante-pagine' : p[0])));
  window.tobiaConta('totale');
  window.tobiaConta(sezione);
  // da dove arriva la visita: solo il tipo di sito (Google, un assistente AI…), mai l'indirizzo completo
  var ref = '';
  try { ref = document.referrer ? new URL(document.referrer).hostname : ''; } catch (e) {}
  if (!ref || ref !== location.hostname) {
    var utm = (/[?&]utm_source=([^&]+)/.exec(location.search) || [])[1] || '';
    var fonte = !ref && !utm ? 'diretto'
      : /chatgpt|openai/.test(ref + utm) ? 'chatgpt' : /perplexity/.test(ref + utm) ? 'perplexity' : /claude\.ai|anthropic/.test(ref + utm) ? 'claude'
      : /gemini\.google|bard\.google/.test(ref) ? 'gemini' : /copilot|bing/.test(ref) ? 'bing'
      : /google\./.test(ref) ? 'google' : /duckduckgo|ecosia|yahoo|qwant|brave|yandex/.test(ref) ? 'altri-motori'
      : /facebook|instagram|t\.co|twitter|x\.com|reddit|whatsapp|telegram|linkedin|youtube|tiktok/.test(ref) ? 'social'
      : /github\./.test(ref) ? 'github' : 'altri-siti';
    window.tobiaConta('da-' + fonte);
  }
  // clic su "Offri un caffè" (Ko-fi)
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="ko-fi.com"]');
    if (a) window.tobiaConta('clic-kofi');
  });
})();
