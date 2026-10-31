"""Rita la Farmacista: scarica dal sito AIFA la lista di trasparenza dei farmaci equivalenti (CSV)."""
import re, sys, urllib.request, urllib.parse, pathlib

PAGINE = ["https://www.aifa.gov.it/it/liste-dei-farmaci", "https://www.aifa.gov.it/liste-di-trasparenza"]
UA = {"User-Agent": "Mozilla/5.0 (Tobia & Co.; tobia-and-co.github.io)"}
out = pathlib.Path("data/aifa"); out.mkdir(parents=True, exist_ok=True)

def leggi(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()

trovati = []
for pagina in PAGINE:
    try:
        html = leggi(pagina).decode("utf-8", "replace")
    except Exception as e:
        print("pagina non raggiungibile", pagina, e); continue
    for href in re.findall(r'href="([^"]+)"', html):
        testo = href.lower()
        if ".csv" in testo or ("trasparenza" in testo and "/documents/" in testo):
            trovati.append(urllib.parse.urljoin(pagina, href.replace("&amp;", "&")))
trovati = list(dict.fromkeys(trovati))
(out / "link_trovati.txt").write_text("\n".join(trovati) + "\n")
print(len(trovati), "link trovati")
salvati = 0
for i, url in enumerate(trovati[:12]):
    try:
        dati = leggi(url)
    except Exception as e:
        print("errore", url, e); continue
    nome = re.sub(r"[^A-Za-z0-9._-]+", "_", urllib.parse.unquote(url.split("/")[-1].split("?")[0]))[:80] or f"file{i}"
    (out / f"{i:02d}_{nome}").write_bytes(dati)
    print("salvato", nome, len(dati), "byte"); salvati += 1
sys.exit(0 if salvati else 1)
