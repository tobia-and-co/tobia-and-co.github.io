"""Pino controlla Benny: se i prezzi dei carburanti sono fermi da più di 3 giorni apre una segnalazione
su GitHub (una sola alla volta). Con l'argomento AAAA-MM-GG prova quella data senza aprire nulla."""
import datetime, json, re, subprocess, sys

TITOLO = "Benny: i prezzi dei carburanti sono fermi"
testo = json.load(open("data/carburanti/indice.json", encoding="utf-8"))["aggiornato"]
data = datetime.date.fromisoformat(re.search(r"\d{4}-\d{2}-\d{2}", testo).group())
prova = sys.argv[1] if len(sys.argv) > 1 else None
oggi = datetime.date.fromisoformat(prova) if prova else datetime.date.today()
giorni = (oggi - data).days
print("Prezzi del", data, "-", giorni, "giorni fa")
if giorni <= 3:
    sys.exit(0)
if prova:
    print("Aprirei la segnalazione")
    sys.exit(0)
aperte = subprocess.run(["gh", "issue", "list", "--state", "open", "--search", f'"{TITOLO}" in:title', "--json", "number"],
                        check=True, capture_output=True, text=True).stdout
if json.loads(aperte):
    print("Segnalazione già aperta")
    sys.exit(0)
subprocess.run(["gh", "issue", "create", "--title", TITOLO, "--body",
                f"Gli ultimi prezzi in `data/carburanti/` sono del {data} ({giorni} giorni fa). "
                "Controllare `benny-casa.sh` e il suo log. Chiudere questa segnalazione quando i dati ripartono."], check=True)
print("Segnalazione aperta")
