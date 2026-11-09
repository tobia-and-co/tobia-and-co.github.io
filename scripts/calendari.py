#!/usr/bin/env python3
"""Calendari in abbonamento: scrive calendari/*.ics (anno corrente + prossimo).
Il telefono si iscrive una volta e si aggiorna da solo. Date concrete (niente RRULE)."""
import calendar, datetime as dt, pathlib

DOM = "tobia-and-co.pages.dev"
FIRMA = "— Tobia & Co. · https://tobia-and-co.pages.dev/scadenze/"
OUT = pathlib.Path(__file__).resolve().parent.parent / "calendari"
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]

def lunedi_se_festivo(d):
    """Scadenze fiscali: se cade di sabato o domenica slitta al lunedì."""
    if d.weekday() >= 5:
        return d + dt.timedelta(days=7 - d.weekday()), True
    return d, False

def esc(t):
    return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def fold(line):
    """Spezza a 75 ottetti UTF-8 (RFC 5545), senza tagliare i caratteri."""
    out, cur, n = [], "", 0
    for ch in line:
        b = len(ch.encode("utf-8"))
        lim = 75 if not out else 74
        if n + b > lim:
            out.append(cur); cur, n = "", 0
        cur += ch; n += b
    out.append(cur)
    return "\r\n ".join(out)

def evento(data, slug, titolo, testo, stamp):
    d = data.strftime("%Y%m%d")
    fine = (data + dt.timedelta(days=1)).strftime("%Y%m%d")
    return [
        "BEGIN:VEVENT",
        f"UID:{d}-{slug}@{DOM}",
        f"DTSTAMP:{stamp}",
        f"DTSTART;VALUE=DATE:{d}",
        f"DTEND;VALUE=DATE:{fine}",
        f"SUMMARY:{esc(titolo)}",
        f"DESCRIPTION:{esc(testo + chr(10) + chr(10) + FIRMA)}",
        "TRANSP:TRANSPARENT",
        "BEGIN:VALARM", "ACTION:DISPLAY",
        f"DESCRIPTION:{esc(titolo)}", "TRIGGER:-P3D", "END:VALARM",
        "END:VEVENT",
    ]

def calendario(nome, eventi):
    righe = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//Tobia & Co.//Calendari {DOM}//IT",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{esc(nome)}",
             "X-WR-TIMEZONE:Europe/Rome", "REFRESH-INTERVAL;VALUE=DURATION:P1D",
             "X-PUBLISHED-TTL:P1D"]
    for e in sorted(eventi, key=lambda e: e[0]):
        righe += e[1]
    righe.append("END:VCALENDAR")
    return "".join(fold(r) + "\r\n" for r in righe)

def fiscali(y, stamp):
    ev = []
    def add(d, slug, titolo, testo, sposta=False):
        nota = ""
        if sposta:
            d2, mosso = lunedi_se_festivo(d)
            if mosso:
                nota = (f" Il {d.day}/{d.month} cade di {GIORNI[d.weekday()]}: per le scadenze fiscali "
                        f"slitta a lunedì {d2.day}/{d2.month}.")
            d = d2
        ev.append((d, evento(d, slug, titolo, testo + nota, stamp)))
    add(dt.date(y, 1, 15), "isee-rinnovo", "ISEE: da rinnovare",
        "L'ISEE scade il 31 dicembre: ora puoi rifare la DSU (dal CAF, da INPS online o con un commercialista) per avere bonus e agevolazioni.")
    add(dt.date(y, 2, calendar.monthrange(y, 2)[1]), "isee-assegno-unico", "Assegno unico: ISEE entro oggi",
        "Entro fine febbraio presenta l'ISEE aggiornato: senza, da marzo l'Assegno unico scende all'importo minimo. Se lo presenti entro il 30 giugno ricevi comunque gli arretrati da marzo.")
    add(dt.date(y, 6, 16), "imu-acconto", "IMU: acconto da pagare",
        "Scade l'acconto IMU (metà dell'imposta annua), con il modello F24. Non serve per l'abitazione principale non di lusso.", True)
    add(dt.date(y, 9, 30), "730-precompilato", "730 precompilato: ultimo giorno per l'invio",
        "Ultimo giorno per inviare il modello 730 (anche precompilato) all'Agenzia delle Entrate.", True)
    add(dt.date(y, 11, 30), "acconto-irpef", "Secondo acconto IRPEF",
        "Scade il secondo acconto delle imposte sui redditi, se lo devi pagare (lo trovi nel tuo 730 o nel modello Redditi).", True)
    add(dt.date(y, 12, 16), "imu-saldo", "IMU: saldo da pagare",
        "Scade il saldo IMU, con conguaglio dell'anno. Non serve per l'abitazione principale non di lusso.", True)
    return ev

def gomme(y, stamp):
    voci = [
        (4, 15, "gomme-estive", "Gomme: si possono rimettere le estive",
         "Da oggi puoi rimontare le gomme estive. Prenota il gommista prima della coda."),
        (5, 15, "gomme-termine", "Gomme: ultimo giorno per le estive",
         "Dove c'è l'obbligo di invernali, oggi scade il termine per montare le estive."),
        (10, 15, "gomme-invernali", "Gomme: si possono montare le invernali",
         "Da oggi puoi montare le invernali: conviene prenotare ora il gommista."),
        (11, 15, "gomme-obbligo", "Gomme: obbligo invernali dove previsto",
         "Da oggi, dove c'è l'ordinanza, servono gomme invernali o catene a bordo (fino al 15 aprile)."),
    ]
    return [(dt.date(y, m, g), evento(dt.date(y, m, g), s, t, d, stamp)) for m, g, s, t, d in voci]

def main():
    oggi = dt.date.today()
    stamp = dt.datetime(oggi.year, oggi.month, 1).strftime("%Y%m%dT000000Z")  # stabile nel mese: niente commit inutili
    anni = [oggi.year, oggi.year + 1]
    OUT.mkdir(exist_ok=True)
    for f, nome, fn in [("scadenze-fiscali.ics", "Scadenze di casa e tasse · Tobia & Co.", fiscali),
                        ("gomme.ics", "Cambio gomme · Tobia & Co.", gomme)]:
        ev = [e for y in anni for e in fn(y, stamp)]
        with open(OUT / f, "w", encoding="utf-8", newline="") as fh:
            fh.write(calendario(nome, ev))
        print(f, len(ev), "eventi")

if __name__ == "__main__":
    main()
