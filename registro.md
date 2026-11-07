# Registro di lavoro (passaggio di consegne tra sessioni)

Le voci più nuove in alto. Ogni sessione lo legge all'inizio e aggiunge 2-3 righe alla fine.

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
