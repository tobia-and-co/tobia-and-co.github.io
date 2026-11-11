# Registro di lavoro (passaggio di consegne tra sessioni)

Le voci più nuove in alto. Ogni sessione lo legge all'inizio e aggiunge 2-3 righe alla fine.

## 11 novembre 2026 · sessione su internet
- `squadra/` rifatta come organigramma con i personaggi a figura intera (`img/squadra/*.svg`); `squadra/organigramma/` ora rimanda a `squadra/` (noindex, tolta da sitemap e da Vera). Home: casella squadra aggiornata (`scripts/home.py`).
- Resta: revisione grafica del sito, guide pratiche.

## 9 novembre 2026 · sessione su internet
- Sito spostato su Cloudflare Pages: https://tobia-and-co.pages.dev (si pubblica da solo dal ramo main; il vecchio github.io rimanda lì con `js/conta.js`). Tutti i link canonici e la sitemap usano il nuovo indirizzo.
- Nuovi: `multe/` e `bolletta-prescritta/` (in home, sitemap, Vera, Ugo, Pino, llms.txt).
- Sera: 168 pagine voli in inglese per turisti (`en/flight-delay-compensation/<partenza>-<arrivo>/`, generate in fondo a `scripts/voli_pagine.py`, elenco in `data/tratte_en.json`). Regola nuova: pubblicazioni raggruppate (Paolo). `scadenze/`: aggiunte carta d'identità (avviso 90 giorni prima) e passaporto (180).
- Poi: `bonus-sociale/` e `carburante/riquadro/` (iframe, noindex, conta 'riquadro-viste') + `carburante/riquadro-per-siti/` (codice da copiare).
- Fabio (`fabio-farmacista.yml`, `farmaci/carenti/`), calendari in abbonamento (`calendari/*.ics`, `scripts/calendari.py`, workflow mensile), report mensile carburanti automatico (`scripts/benny_report.py` dentro benny-statistiche; primo report il 1/12).
- Turno sera: link diretti per agenti (voli/?da=FCO&a=JFK&ritardo=4, treno/?prezzo=&ritardo=, multe/?importo=&notifica=, carburante/?q=&carb=; documentati in llms.txt e agenti/). Fabio: letta la colonna delle motivazioni e salvati i nomi delle colonne del file AIFA.
- Restano: registri MCP (serve accesso dell'account del progetto).

## 7 novembre 2026 · sessione su internet
- Nuovi: `bagaglio/`, `tasse-aeroportuali/`, 45 pagine `voli/compagnia/<nome>/` + elenco + `voli/sciopero/` (generate da `scripts/compagnie_pagine.py`).
- Poi: 28 pagine aeroporti, `carburante/prezzi-medi/` (workflow benny-statistiche.yml, storico in data/carburanti/storico.json), llms.txt + FAQ strutturate.
- Sera: `treno/` e `affitto-istat/` (variazione FOI inserita dall'utente: ISTAT non raggiungibile da qui).
- I robottini girano solo sul sito vero (`if: github.repository == ...`).

## 5 novembre 2026 (sera) · sessione su internet
- Nuovo robottino Ugo il Guardiano (controllo giornaliero del sito vero). Squadra aggiornata in home e nel diario (aggiunti Vera, Benny, Ugo; Gino in pausa; Bruno in arrivo).
- `benny-casa.sh` ora si allinea con fetch + reset (non più pull).

## 5 novembre 2026 · sessione sul computer
- Fatto: Benny attivo (prima pubblicazione dei prezzi riuscita); pagina `carburante/` con mappa, classifica per costo totale e 107 pagine città (`node scripts/benny_pagine.js`, sitemap aggiornata); Pino apre una segnalazione se i prezzi sono fermi da più di 3 giorni.
- Resta: controllare il 6/11 la prima esecuzione automatica di Benny e la data dei prezzi; poi «Bagaglio perso» e tasse aeroportuali.
- Nota: la cartella di lavoro sul computer non ha Python; i controlli girano anche con Node e Edge.

## 5 novembre 2026 · sessione su internet
- Fatto: CLAUDE.md con tutte le regole; strumento Assegno unico; domanda di affiliazione AirHelp inviata (in attesa).
- Resta: installare Benny sul computer di casa (vedi `scripts/minipc/ISTRUZIONI.md`), poi la mappa carburanti;
  inserire il link AirHelp in `js/voli.js` quando arriva.
- Turni automatici attivi nella sessione su internet: lun/mer/ven sera e bilancio sabato 7/11.
