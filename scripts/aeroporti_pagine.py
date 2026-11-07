"""Crea le pagine "Volo in ritardo da <aeroporto>?" (voli/aeroporto/<nome>/) e l'elenco voli/aeroporto/.
Riusa il modello delle pagine delle compagnie (scripts/compagnie_pagine.py)."""
import json, pathlib, re
import importlib.util
spec = importlib.util.spec_from_file_location("cp", "scripts/compagnie_pagine.py"); cp = importlib.util.module_from_spec(spec)
import sys, io
_out = sys.stdout; sys.stdout = io.StringIO(); spec.loader.exec_module(cp); sys.stdout = _out   # rigenera anche le compagnie
e, slug, pagina, scrivi, TABELLA = cp.e, cp.slug, cp.pagina, cp.scrivi, cp.TABELLA

# codice, nome italiano, città (per le tratte già pronte: prefisso dei percorsi voli/<città>-...)
AEROPORTI = [("FCO", "Roma Fiumicino", "roma"), ("CIA", "Roma Ciampino", None), ("MXP", "Milano Malpensa", "milano"),
    ("LIN", "Milano Linate", "milano-linate"), ("BGY", "Bergamo Orio al Serio", "bergamo"), ("VCE", "Venezia Marco Polo", "venezia"),
    ("TSF", "Treviso", None), ("NAP", "Napoli Capodichino", "napoli"), ("CTA", "Catania Fontanarossa", "catania"),
    ("PMO", "Palermo Falcone Borsellino", "palermo"), ("BRI", "Bari", "bari"), ("BDS", "Brindisi", None), ("CAG", "Cagliari Elmas", "cagliari"),
    ("OLB", "Olbia Costa Smeralda", None), ("AHO", "Alghero", None), ("BLQ", "Bologna Marconi", "bologna"), ("TRN", "Torino Caselle", "torino"),
    ("FLR", "Firenze Peretola", "firenze"), ("PSA", "Pisa Galilei", "pisa"), ("VRN", "Verona Villafranca", None), ("GOA", "Genova", None),
    ("TRS", "Trieste", None), ("SUF", "Lamezia Terme", None), ("REG", "Reggio Calabria", None), ("PSR", "Pescara", None),
    ("AOI", "Ancona Falconara", None), ("TPS", "Trapani Birgi", None), ("CIY", "Comiso", None)]
TRATTE = json.load(open("data/tratte.json"))
NOMI_TRATTE = {}
for p in TRATTE:   # voli/roma-new-york/ -> "Roma – New York" (dal titolo della pagina)
    t = pathlib.Path(p, "index.html").read_text(encoding="utf-8")
    m = re.search(r"<h1>✈️ Volo (.*?) in ritardo\?</h1>", t)
    if m: NOMI_TRATTE[p] = m.group(1)

uscite = []
for cod, nome, citta in AEROPORTI:
    s = slug(nome); perc = f"voli/aeroporto/{s}/"
    tratte = [p for p in TRATTE if citta and p.startswith(f"voli/{citta}-") and not (citta == "milano" and p.startswith("voli/milano-linate-"))]
    lista = ("<h3>Le tratte più cercate da qui</h3><p>" + " · ".join(f'<a href="../../{p[5:]}">{e(NOMI_TRATTE.get(p, p))}</a>' for p in tratte) + "</p>") if tratte else ""
    corpo = f"""  <div class="card">
    <h2 style="margin-top:0">🛫 {e(nome)} ({cod})</h2>
    <p>Per i voli che <b>partono da {e(nome)}</b> il Regolamento UE 261/2004 vale <b>con qualsiasi compagnia aerea</b>, europea o no: Ryanair, ITA Airways, Emirates, easyJet, tutte. Per i voli che <b>arrivano</b> qui da fuori Europa vale solo se la compagnia è europea.</p>
    <h3>Quanto ti spetta</h3>
  {TABELLA}
  {lista}
  </div>
  <div class="card">
    <h2 style="margin-top:0">📝 Se sei ancora in aeroporto</h2>
    <ol class="passi-lista">
      <li>Fatti dire (o fotografa sul tabellone) il motivo del ritardo o della cancellazione: ti servirà nella richiesta.</li>
      <li>Dopo 2 ore di attesa (3 o 4 per i voli più lunghi) la compagnia deve darti pasti e bevande; se si va al giorno dopo, anche l'albergo. Conserva gli scontrini di quello che paghi tu.</li>
      <li>Se il volo è cancellato puoi scegliere tra il rimborso del biglietto e un volo alternativo.</li>
      <li>Se la valigia non arriva, vai al banco «Lost &amp; Found» prima di uscire: <a href="../../../bagaglio/">ecco cosa fare</a>.</li>
    </ol>
  </div>"""
    scrivi(perc, pagina(perc, f"Volo in ritardo o cancellato da {nome}? Rimborso fino a 600 €",
        f"Volo da {nome} ({cod}) in ritardo di oltre 3 ore, cancellato o in overbooking? Con qualsiasi compagnia ti spettano fino a 600 € a persona (Regolamento UE 261/2004). Calcolo e lettera pronta, gratis.",
        f'<a href="../">Aeroporti</a> › {e(nome)}', "Regolamento UE 261/2004", f"🛫 Volo in ritardo da {nome}?",
        f"Se il tuo volo da {e(nome)} è arrivato con oltre 3 ore di ritardo, è stato cancellato o ti hanno negato l'imbarco, possono spettarti <b>fino a 600 € a persona</b>, con qualsiasi compagnia.",
        corpo, "aeroporto-" + cod.lower(), faq=[
            (f"Volo in ritardo da {nome}: quanto spetta?", f"Per i voli in partenza da {nome}, con qualsiasi compagnia, spettano 250 €, 400 € o 600 € a persona in base alla distanza, se il ritardo all'arrivo supera le 3 ore e la causa non è straordinaria (Regolamento UE 261/2004)."),
            (f"Il regolamento europeo vale per tutte le compagnie che partono da {nome}?", "Sì: per i voli in partenza da un aeroporto dell'Unione europea vale con qualsiasi compagnia. Per i voli in arrivo da fuori Europa vale solo se la compagnia è europea.")]))
    uscite.append((nome, cod, perc))

voci = "".join(f'<li><a href="{p.replace("voli/aeroporto/", "")}">{e(n)}</a> <span class="note">({c})</span></li>' for n, c, p in sorted(uscite))
scrivi("voli/aeroporto/", pagina("voli/aeroporto/", "Volo in ritardo o cancellato: aeroporto per aeroporto",
    "Fiumicino, Malpensa, Linate, Orio al Serio, Napoli, Catania, Palermo e altri 21 aeroporti italiani: quando ti spetta il rimborso fino a 600 € per un volo in ritardo o cancellato.",
    "Aeroporti", "Regolamento UE 261/2004", "🛫 Volo in ritardo: aeroporto per aeroporto",
    "Dagli aeroporti italiani il regolamento europeo vale con qualsiasi compagnia. Scegli il tuo e calcola quanto ti spetta.",
    f'  <div class="card"><h2 style="margin-top:0">🇮🇹 Scegli l\'aeroporto di partenza</h2><ul class="colonne">{voci}</ul></div>', "elenco-aeroporti"))
elenco = json.load(open("data/compagnie.json"))
json.dump(elenco + [p for _, _, p in uscite] + ["voli/aeroporto/"], open("data/compagnie.json", "w"))
print(len(uscite), "pagine di aeroporti + elenco")
