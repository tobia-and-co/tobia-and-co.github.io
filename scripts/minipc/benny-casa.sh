#!/bin/bash
# Benny "di casa": gira sul mini PC in Italia (il sito del Ministero blocca i server esteri).
# Ogni mattina scarica i prezzi ufficiali dei carburanti, li prepara e li carica sul sito di Tobia.
set -e
cd /opt/tobia/sito
git fetch -q origin main && git reset -q --hard origin/main  # sempre allineato al sito (anche se la cronologia viene riscritta)
python3 scripts/benny_carburanti.py
# Anche il calendario ufficiale degli scioperi (MIT) blocca i server esteri: lo scarica Benny da qui.
# Per ora salva la pagina così com'è; il robottino che crea le pagine degli scioperi la legge su GitHub.
mkdir -p data/grezzi
curl -s -m 40 -A "Mozilla/5.0 (TobiaAndCo; dati pubblici)" -o data/grezzi/scioperi-mit.txt.tmp "https://scioperi.mit.gov.it/mit2/public/scioperi" \
  && [ -s data/grezzi/scioperi-mit.txt.tmp ] && mv data/grezzi/scioperi-mit.txt.tmp data/grezzi/scioperi-mit.txt || rm -f data/grezzi/scioperi-mit.txt.tmp
git add data/carburanti
git add data/grezzi 2>/dev/null || true
if ! git diff --cached --quiet; then
  git -c user.name="Benny il Benzinaio (Tobia & Co.)" -c user.email="tobia.and.co@proton.me" commit -qm "Benny: prezzi dei carburanti aggiornati [CF-Pages-Skip]"
  git push -q
fi
