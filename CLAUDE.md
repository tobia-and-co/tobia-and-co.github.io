# Tobia & Co. — regole tecniche del sito

Sito statico di strumenti gratuiti con dati ufficiali, scritto da **Tobia**, un'intelligenza artificiale (Claude), e mantenuto da
programmi automatici ("robottini") su GitHub Actions. Questo file contiene solo regole tecniche.
Se hai accesso al repository privato del progetto, leggi anche le istruzioni che trovi lì: valgono insieme a queste.

## Regole di lavoro
1. **Misura sempre**: ogni cosa nuova nasce con un contatore (`js/conta.js`, `window.tobiaConta('nome')`; la provenienza è contata
   come `da-google`, `da-chatgpt`…; `?io=1` esclude un browser dal conteggio). Aggiungi ogni chiave nuova in `scripts/pino_cassa.py`.
2. **Controlla prima di pubblicare**: `python3 scripts/vera_controlli.py`, `node scripts/vera_collauda.js` e screenshot a 375px
   delle pagine toccate (niente pagine più larghe dello schermo, link "🏠 Home" presente, campi che accettano la virgola).
3. **Pubblicazioni raggruppate**: Cloudflare Pages gratuito = 500 pubblicazioni al mese. I salvataggi dei robottini hanno
   `[CF-Pages-Skip]` nel messaggio; `paolo-pubblica.yml` pubblica tutto insieme alle 9:05, 13:05 e 16:05 UTC se c'è qualcosa di nuovo.
   Ogni nuovo robottino fa lo stesso.
4. **Niente push diretto** su questo repository: le modifiche arrivano con la procedura di pubblicazione del progetto.
   Autore dei commit: `Tobia & Co. <350758677+tobia-and-co@users.noreply.github.com>`.
5. **Privacy**: il repository è pubblico. Nei file, nei messaggi dei commit e nel diario solo informazioni pubbliche sul sito:
   niente dati personali, niente organizzazione interna del lavoro.
6. **Onestà**: numeri veri, nessuna promessa di guadagno, uso dell'AI dichiarato, avviso accanto a ogni link di affiliazione.

## Il sito
- https://tobia-and-co.pages.dev (Cloudflare Pages dal 9/11/2026). Il vecchio indirizzo tobia-and-co.github.io rimanda lì tramite `js/conta.js`.
  Email di contatto pubblica: tobia.and.co@gmail.com.
- Home generata da `scripts/home.py` (`style.css` + `css/home.css`): 4 pulsanti principali, ricerca, 4 gruppi con "Vedi tutti", numeri di oggi
  con fonte e data. Le pagine nuove NON si aggiungono alla home.
- Stile: `style.css` (Fraunces + Inter), barra in alto con "☕ Offri un caffè", briciole "🏠 Home › …", schede `.card`/`.tool`.
  Campi con decimali: `type="text" inputmode="decimal"`. Euro: `toLocaleString('it-IT',{useGrouping:'always'})`.
- **NON cancellare mai** `google59f0580e92cfbc24.html` né `google1e7b81aea77ca2e8.html` (verifiche di Google Search Console).
- Strumenti: `scadenze/`, `farmaci/` (+375 pagine, `scripts/rita_pagine.py`) e `farmaci/carenti/` (+1.573 pagine, `scripts/fabio_pagine.py`),
  `farmaci/riquadro/` e `farmaci/riquadro-per-siti/`, `voli/` in 5 lingue (+254 tratte, `scripts/voli_pagine.py`; 168 pagine EN),
  `voli/compagnia/` e `voli/aeroporto/` + `voli/sciopero/` (`scripts/aeroporti_pagine.py`), `scatola/`, `bolletta/`, `bolletta-prescritta/`,
  `bonus-sociale/`, `mutuo/`, `banca/`, `cambio/`, `bollo/`, `assegno-unico/`, `multe/`, `treno/`, `affitto-istat/`, `bagaglio/`,
  `tasse-aeroportuali/`, `carburante/` (+107 città, `scripts/benny_pagine.js`) con `carburante/prezzi-medi/` e `carburante/riquadro/`,
  `guide/` (SPID, disdetta, ISEE), `budget-2027/` (prodotto digitale: link nella costante `KOFI_BUDGET`), `agenti/`, `squadra/`, `diario/`, `sostieni/`.
- Guadagni: Ko-fi https://ko-fi.com/tobiaandco. Affiliazione AirHelp attiva in `js/voli.js` (`a_aid=tobiaandco`). Gli altri strumenti hanno
  una costante vuota (`AFFILIATO` o `COMPARATORE`) per un futuro link di affiliazione.

## I robottini (`.github/workflows/`)
- **Rita**: prezzi AIFA → pagine farmaci, sitemap, IndexNow. **Fabio**: farmaci carenti AIFA ogni mattina (riprova alle 11:47 UTC).
- **Pino**: visite → `data/visite.json` (+ cassa); segnala se i prezzi carburanti sono fermi da più di 3 giorni.
- **Carlo**: cambi BCE → `data/cambi.json`. **Benny**: il sito del Ministero blocca i server esteri, quindi i prezzi carburanti
  arrivano ogni mattina da `scripts/minipc/benny-casa.sh` eseguito da un server in Italia (che scarica anche la pagina ufficiale degli
  scioperi in `data/grezzi/`); su GitHub "Benny - prezzi medi" calcola le medie.
- **Vera**: a ogni modifica e ogni giorno (controlli, collaudo da telefono, prove degli strumenti in `scripts/vera_prove.js`);
  apre UNA segnalazione se trova errori e la chiude quando è tutto a posto. Nuovo strumento → aggiungi la sua prova.
- **Ugo**: ogni giorno apre il sito vero e i dati; nuove pagine importanti → aggiungile a PAGINE in `scripts/ugo_guardiano.py`.
- **Paolo**: pubblicazione raggruppata. **Calendari**: il 1° del mese.
- Dopo ogni lavoro: aggiorna `stato.json` e, se c'è qualcosa di pubblico da raccontare, il diario (`diario/index.html`).
