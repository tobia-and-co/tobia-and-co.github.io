"""Ugo il Guardiano: ogni giorno apre il sito VERO (come un visitatore) e controlla che le pagine rispondano
e che i robottini abbiano portato dati freschi. Se qualcosa non va apre UNA segnalazione su GitHub;
quando torna tutto a posto la chiude da solo. Con l'argomento "prova" stampa soltanto."""
import datetime, json, re, subprocess, sys, urllib.request

import os
SITO = os.environ.get("UGO_SITO", "https://tobia-and-co.github.io/")
TITOLO = "Ugo: qualcosa non va sul sito"
PAGINE = ["", "scadenze/", "farmaci/", "farmaci/omeprazolo/", "voli/", "en/flight-delay-compensation/", "scatola/",
          "bolletta/", "mutuo/", "banca/", "cambio/", "bollo/", "assegno-unico/", "carburante/", "diario/", "sostieni/",
          "sitemap.xml", "robots.txt", "google59f0580e92cfbc24.html", "style.css", "js/conta.js"]
# file di dati: (percorso, come leggere la data, giorni massimi, chi lo aggiorna)
DATI = [("data/cambi.json", lambda d: d["data"], 5, "Carlo"),
        ("data/visite.json", lambda d: d["controllato"], 2, "Pino"),
        ("data/farmaci.json", lambda d: d["aggiornato"], 20, "Rita"),
        ("data/carburanti/indice.json", lambda d: re.search(r"\d{4}-\d{2}-\d{2}", d["aggiornato"]).group(), 3, "Benny")]

def scarica(percorso):
    req = urllib.request.Request(SITO + percorso, headers={"User-Agent": "Ugo-il-Guardiano (Tobia & Co.)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()

problemi, oggi = [], datetime.date.today()
for p in PAGINE:
    try:
        stato, corpo = scarica(p)
        if stato != 200 or len(corpo) < 20:
            problemi.append(f"`/{p}` risponde {stato} ({len(corpo)} byte)")
        elif (p == "" or p.endswith("/")) and b"Tobia" not in corpo:
            problemi.append(f"`/{p}` non sembra una pagina del sito")
    except Exception as e:
        problemi.append(f"`/{p}` non si apre: {e}")
for percorso, leggi, massimo, chi in DATI:
    try:
        data = datetime.date.fromisoformat(leggi(json.loads(scarica(percorso)[1])))
        giorni = (oggi - data).days
        if giorni > massimo:
            problemi.append(f"{chi}: `{percorso}` è del {data} ({giorni} giorni fa, massimo {massimo})")
    except Exception as e:
        problemi.append(f"{chi}: `{percorso}` non si legge: {e}")

print("\n".join(problemi) or f"Tutto a posto: {len(PAGINE)} pagine e {len(DATI)} file di dati controllati.")
if len(sys.argv) > 1:
    sys.exit(0)
gh = lambda *a: subprocess.run(["gh", *a], check=True, capture_output=True, text=True).stdout
aperte = json.loads(gh("issue", "list", "--state", "open", "--search", f'"{TITOLO}" in:title', "--json", "number"))
if problemi and not aperte:
    gh("issue", "create", "--title", TITOLO, "--body", "Controllo del " + str(oggi) + ":\n\n- " + "\n- ".join(problemi))
    print("Segnalazione aperta")
elif not problemi and aperte:
    for a in aperte:
        gh("issue", "close", str(a["number"]), "--comment", f"Controllo del {oggi}: tutto di nuovo a posto.")
    print("Segnalazione chiusa")
