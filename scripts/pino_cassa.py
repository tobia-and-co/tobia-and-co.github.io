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
