"""Pino il Contabile: legge dalle blockchain pubbliche quanto c'è nella cassa di Tobia
(USDC ed ETH su Base, Polygon ed Ethereum) e lo scrive in data/cassa.json."""
import json, urllib.request, datetime

CASSA = "0xd1d91ed385ae794992f048f17e99e6d830cf48e1"
RETI = {
    "base": ("https://mainnet.base.org", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "ETH"),
    "polygon": ("https://polygon-bor-rpc.publicnode.com", "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359", "POL"),
    "ethereum": ("https://ethereum-rpc.publicnode.com", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "ETH"),
}

def rpc(url, metodo, params):
    corpo = json.dumps({"jsonrpc": "2.0", "id": 1, "method": metodo, "params": params}).encode()
    req = urllib.request.Request(url, data=corpo, headers={"Content-Type": "application/json", "User-Agent": "TobiaAndCo/1.0"})
    return int(json.load(urllib.request.urlopen(req, timeout=30))["result"], 16)

saldi, usdc_tot = {}, 0.0
for rete, (url, usdc, nativa) in RETI.items():
    try:
        dati = "0x70a08231" + CASSA[2:].lower().rjust(64, "0")  # balanceOf(CASSA)
        u = rpc(url, "eth_call", [{"to": usdc, "data": dati}, "latest"]) / 1e6
        n = rpc(url, "eth_getBalance", [CASSA, "latest"]) / 1e18
        saldi[rete] = {"usdc": round(u, 2), nativa.lower(): round(n, 6)}
        usdc_tot += u
    except Exception as e:
        saldi[rete] = {"errore": str(e)[:120]}
uscita = {"indirizzo": CASSA, "controllato": datetime.date.today().isoformat(),
          "usdc_totale": round(usdc_tot, 2), "reti": saldi}
json.dump(uscita, open("data/cassa.json", "w"), indent=2)
print(json.dumps(uscita, indent=2))

# Visite contate da js/conta.js (servizio Abacus, nessun account)
visite = {}
for chiave in ["totale", "home", "scadenze", "farmaci", "farmaci-pagine", "diario", "sostieni", "calendari-scaricati", "ricerche-farmaci", "clic-kofi", "voli", "en", "es", "fr", "de", "calcoli-voli", "lettere-voli", "clic-affiliato-voli", "scatola", "promemoria-scatola", "tratte", "bolletta", "confronti-bolletta", "clic-comparatore", "mutuo", "calcoli-mutuo", "clic-mutuo", "banca", "calcoli-banca", "clic-banca", "cambio", "calcoli-cambio", "clic-cambio", "bollo", "calcoli-bollo", "clic-assicurazione", "assegno-unico", "calcoli-assegno", "carburante", "carburante-pagine", "ricerche-carburante", "posizione-carburante", "indirizzo-carburante", "clic-navigatore", "bagaglio", "calcoli-bagaglio", "lettere-bagaglio", "promemoria-bagaglio", "tasse-aeroportuali", "calcoli-tasse", "lettere-tasse", "compagnie", "sciopero", "overbooking", "coincidenza-persa", "volo-cancellato", "aeroporti", "prezzi-medi", "treno", "calcoli-treno", "affitto-istat", "calcoli-affitto", "lettere-affitto", "promemoria-affitto", "agenti", "squadra"]:
    try:
        req = urllib.request.Request(f"https://abacus.jasoncameron.dev/get/tobiaandco/{chiave}", headers={"User-Agent": "TobiaAndCo/1.0"})
        visite[chiave] = json.load(urllib.request.urlopen(req, timeout=30)).get("value", 0)
    except Exception as e:
        visite[chiave] = 0 if "404" in str(e) else None
json.dump({"controllato": datetime.date.today().isoformat(), "visite": visite}, open("data/visite.json", "w"), indent=2)
print("visite:", visite)
