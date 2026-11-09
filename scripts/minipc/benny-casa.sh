#!/bin/bash
# Benny "di casa": gira sul mini PC in Italia (il sito del Ministero blocca i server esteri).
# Ogni mattina scarica i prezzi ufficiali dei carburanti, li prepara e li carica sul sito di Tobia.
set -e
cd /opt/tobia/sito
git fetch -q origin main && git reset -q --hard origin/main  # sempre allineato al sito (anche se la cronologia viene riscritta)
python3 scripts/benny_carburanti.py
git add data/carburanti
if ! git diff --cached --quiet; then
  git -c user.name="Benny il Benzinaio (Tobia & Co.)" -c user.email="tobia.and.co@proton.me" commit -qm "Benny: prezzi dei carburanti aggiornati [CF-Pages-Skip]"
  git push -q
fi
