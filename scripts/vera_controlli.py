"""Vera, controlli "da scrivania" su TUTTO il sito (veloci, senza browser):
link interni di tutte le pagine, sitemap (indirizzi mancanti o doppi), file JSON validi,
contatori usati nelle pagine ma non letti da Pino. Esce con errore se trova problemi."""
import json, pathlib, re, sys, urllib.parse
R = pathlib.Path(__file__).resolve().parent.parent
problemi = []
pagine = [p for p in R.rglob("*.html") if not set(p.relative_to(R).parts) & {".git", ".anteprime", "node_modules"}]
link = 0
for f in pagine:
    s = f.read_text(encoding="utf-8", errors="ignore")
    for u in re.findall(r'(?:href|src)="([^"#?]+)', s):
        if re.match(r"^(https?:|mailto:|data:|javascript:|//|tel:)", u) or "{" in u or "'" in u: continue
        link += 1
        t = (f.parent / urllib.parse.unquote(u)).resolve()
        if u.endswith("/") or t.is_dir(): t = t / "index.html"
        if not t.exists(): problemi.append(f"{f.relative_to(R)}: link rotto verso {u}")
sm = (R / "sitemap.xml").read_text(encoding="utf-8")
urls = re.findall(r"<loc>https://tobia-and-co\.pages\.dev/([^<]*)</loc>", sm)
for u in sorted({u for u in urls if urls.count(u) > 1}): problemi.append(f"sitemap: indirizzo doppio {u}")
for u in urls:
    t = R / u / "index.html" if (u == "" or u.endswith("/")) else R / u
    if not t.exists(): problemi.append(f"sitemap: la pagina non esiste {u}")
for j in R.rglob("*.json"):
    if set(j.relative_to(R).parts) & {".git", "node_modules"}: continue
    try: json.loads(j.read_text(encoding="utf-8"))
    except Exception as e: problemi.append(f"{j.relative_to(R)}: JSON non valido ({str(e)[:60]})")
pino = (R / "scripts/pino_cassa.py").read_text(encoding="utf-8")
chiavi = set()
for f in pagine + list((R / "js").glob("*.js")):
    chiavi |= set(re.findall(r"tobiaConta\('([a-z0-9-]+)'\)", f.read_text(encoding="utf-8", errors="ignore")))
for k in sorted(chiavi - {"nome"}):
    if f'"{k}"' not in pino: problemi.append(f"contatore '{k}' usato nelle pagine ma Pino non lo legge")
print(f"Vera (scrivania): {len(pagine)} pagine, {link} link interni, {len(urls)} indirizzi in sitemap. Problemi: {len(problemi)}")
for p in problemi[:60]: print(" - " + p)
sys.exit(1 if problemi else 0)
