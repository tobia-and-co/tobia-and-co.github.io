# Installare "Benny di casa" sul mini PC

Serve perché il sito del Ministero (prezzi carburanti) accetta solo connessioni dall'Italia.

## 1. Chiave GitHub limitata (la crea l'utente, da browser)
Entrando su github.com come **tobia-and-co**: Settings → Developer settings → Personal access tokens →
**Fine-grained tokens** → Generate new token.
- Nome: `mini-pc-benny` · Scadenza: 1 anno
- Repository access: **Only select repositories** → `tobia-and-co/tobia-and-co.github.io`
- Permissions → Repository → **Contents: Read and write** (nient'altro)
Copiare la chiave (inizia con `github_pat_`) e NON condividerla in chat.

## 2. Messaggio da incollare in una sessione Claude Code LOCALE sul proprio PC
> Sul computer di casa c'è un container Debian dove installare Benny.
> Aiutami a: (1) collegarti al container; (2) installare git e python3 se mancano; (3) clonare
> https://github.com/tobia-and-co/tobia-and-co.github.io in /opt/tobia/sito usando una chiave GitHub che ti
> darò io al momento (salvala solo nella configurazione git del container, mai in file pubblici);
> (4) rendere eseguibile /opt/tobia/sito/scripts/minipc/benny-casa.sh e lanciarlo una volta per prova;
> (5) aggiungere a crontab: `35 9 * * * /opt/tobia/sito/scripts/minipc/benny-casa.sh >> /var/log/benny.log 2>&1`.
> Chiedimi conferma prima di ogni comando.

## 3. Verifica
Dopo la prova, su GitHub compare un aggiornamento "Benny: prezzi dei carburanti aggiornati" e
`data/carburanti/indice.json`. Da lì Tobia costruisce la mappa.
