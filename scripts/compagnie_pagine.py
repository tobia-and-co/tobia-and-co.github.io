"""Crea le pagine "Volo <compagnia> in ritardo o cancellato?" (voli/compagnia/<nome>/), l'elenco voli/compagnia/
e la pagina sugli scioperi (voli/sciopero/). Usa i testi italiani del calcolatore (data/voli_testi.json)."""
import html, json, pathlib, re, unicodedata

SITO = "https://tobia-and-co.pages.dev"
T = json.load(open("data/voli_testi.json", encoding="utf-8"))["it"]
e = lambda s: html.escape(s, quote=True)
def slug(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

# nome, codice IATA, paese della compagnia, tipo: ue (UE/SEE/Svizzera), uk, extra, misto (+ nota)
COMPAGNIE = [
    ("Ryanair", "FR", "Irlanda", "ue", ""), ("ITA Airways", "AZ", "Italia", "ue", ""),
    ("easyJet", "U2", "Regno Unito / Austria", "misto", "Il gruppo ha più società: easyJet Europe (Austria, europea) ed easyJet UK (britannica). Sulla carta d'imbarco o nella prenotazione trovi «operato da»: è quella che conta."),
    ("Wizz Air", "W6", "Ungheria / Malta / Regno Unito", "misto", "Il gruppo ha più società: Wizz Air Hungary e Wizz Air Malta (europee) e Wizz Air UK (britannica). Conta quella che opera il tuo volo («operato da»)."),
    ("Volotea", "V7", "Spagna", "ue", ""), ("Vueling", "VY", "Spagna", "ue", ""), ("Neos", "NO", "Italia", "ue", ""),
    ("Aeroitalia", "XZ", "Italia", "ue", ""), ("Air Dolomiti", "EN", "Italia", "ue", ""), ("Lufthansa", "LH", "Germania", "ue", ""),
    ("Air France", "AF", "Francia", "ue", ""), ("KLM", "KL", "Paesi Bassi", "ue", ""), ("Iberia", "IB", "Spagna", "ue", ""),
    ("Air Europa", "UX", "Spagna", "ue", ""), ("TAP Air Portugal", "TP", "Portogallo", "ue", ""), ("Aegean Airlines", "A3", "Grecia", "ue", ""),
    ("Brussels Airlines", "SN", "Belgio", "ue", ""), ("Austrian Airlines", "OS", "Austria", "ue", ""), ("Eurowings", "EW", "Germania", "ue", ""),
    ("Transavia", "HV", "Paesi Bassi / Francia", "ue", ""), ("Aer Lingus", "EI", "Irlanda", "ue", ""), ("SAS", "SK", "Scandinavia", "ue", ""),
    ("Finnair", "AY", "Finlandia", "ue", ""), ("LOT Polish Airlines", "LO", "Polonia", "ue", ""), ("Croatia Airlines", "OU", "Croazia", "ue", ""),
    ("airBaltic", "BT", "Lettonia", "ue", ""), ("Luxair", "LG", "Lussemburgo", "ue", ""),
    ("Norwegian", "DY", "Norvegia", "ue", "La Norvegia non è nell'Unione europea ma applica le stesse regole (Spazio economico europeo)."),
    ("Icelandair", "FI", "Islanda", "ue", "L'Islanda non è nell'Unione europea ma applica le stesse regole (Spazio economico europeo)."),
    ("Swiss", "LX", "Svizzera", "ue", "La Svizzera non è nell'Unione europea ma applica il regolamento grazie a un accordo con l'UE."),
    ("British Airways", "BA", "Regno Unito", "uk", ""), ("Jet2", "LS", "Regno Unito", "uk", ""),
    ("Turkish Airlines", "TK", "Turchia", "extra", ""), ("Pegasus Airlines", "PC", "Turchia", "extra", ""),
    ("Emirates", "EK", "Emirati Arabi Uniti", "extra", ""), ("Etihad Airways", "EY", "Emirati Arabi Uniti", "extra", ""),
    ("Qatar Airways", "QR", "Qatar", "extra", ""), ("Royal Air Maroc", "AT", "Marocco", "extra", ""), ("Tunisair", "TU", "Tunisia", "extra", ""),
    ("EgyptAir", "MS", "Egitto", "extra", ""), ("Air Serbia", "JU", "Serbia", "extra", ""), ("Delta Air Lines", "DL", "Stati Uniti", "extra", ""),
    ("United Airlines", "UA", "Stati Uniti", "extra", ""), ("American Airlines", "AA", "Stati Uniti", "extra", ""), ("Air Canada", "AC", "Canada", "extra", ""),
]
REGOLA = {
    "ue": "È una compagnia europea: il Regolamento UE 261/2004 vale per <b>tutti i suoi voli che partono da un aeroporto europeo</b> (Italia compresa) e anche per quelli che <b>arrivano in Europa</b> da fuori.",
    "uk": "È una compagnia britannica: il Regolamento UE vale per i suoi voli che <b>partono dall'Unione europea</b> (quindi dall'Italia). Per i voli che partono dal Regno Unito vale la versione britannica (UK261), con importi in sterline (fino a 520 £).",
    "extra": "Non è una compagnia europea: il Regolamento UE vale per i suoi voli che <b>partono da un aeroporto europeo</b>, per esempio dall'Italia. Per i voli verso l'Italia da fuori Europa di solito non vale: lì puoi chiedere solo i danni dimostrati (Convenzione di Montreal).",
    "misto": "Dipende dalla società che opera il volo. Se è europea, il Regolamento UE 261/2004 vale per tutti i voli che partono o arrivano in Europa; se è britannica, vale per i voli che partono dall'Unione europea (e UK261 per quelli dal Regno Unito).",
}
def airhelp(contenuto):
    return ("https://www.airhelp.it/?utm_medium=affiliate&utm_source=pap&utm_campaign=aff-tobiaandco&utm_content="
            + contenuto + "&a_aid=tobiaandco")
AVVISO = "Link di affiliazione: se AirHelp vince la tua pratica ricevo una piccola commissione da loro. A te non costa nulla in più, e puoi sempre fare la richiesta da solo, gratis, con il calcolatore e la lettera qui sopra."

def opz(coppie): return "".join(f'<option value="{v}">{e(T[k])}</option>' for v, k in coppie)
MODULO = f"""<form class="card" id="modulo" autocomplete="off">
    <label for="da">{e(T['da'])}</label><input id="da" placeholder="{e(T['segnaposto'])}"><div id="da-lista" class="lista"></div>
    <label for="a">{e(T['a'])}</label><input id="a" placeholder="{e(T['segnaposto'])}"><div id="a-lista" class="lista"></div>
    <label class="check"><input type="checkbox" id="ue" checked> {e(T['ue'])}</label>
    <label for="evento">{e(T['evento'])}</label><select id="evento">{opz([('ritardo','e_ritardo'),('cancellato','e_cancellato'),('negato','e_negato')])}</select>
    <div id="box-ritardo"><label for="ritardo">{e(T['ritardo'])}</label><select id="ritardo">{opz([('4','r_4'),('3','r_3'),('2','r_2'),('0','r_0')])}</select></div>
    <div id="box-avviso" hidden><label for="avviso">{e(T['avviso'])}</label><select id="avviso">{opz([('0','a_0'),('7','a_7'),('14','a_14')])}</select></div>
    <label for="causa">{e(T['causa'])}</label><select id="causa">{opz([('tecnico','c_tecnico'),('sciopero','c_sciopero'),('meteo','c_meteo'),('atc','c_atc'),('sicurezza','c_sicurezza')])}</select>
    <p style="margin-top:20px"><button type="submit">✈️ {e(T['calcola'])}</button></p>
  </form>
  <div id="esito"></div>"""

def pagina(perc, titolo, descr, briciola, occhiello, h1, lead, corpo, contenuto_aff, faq=()):
    base = "../" * perc.count("/")
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}, ensure_ascii=False) if faq else ""
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)} | Tobia & Co.</title>
<meta name="description" content="{e(descr)}">
<link rel="canonical" href="{SITO}/{perc}">
<link rel="icon" href="{base}img/tobia-base.svg">
<link rel="stylesheet" href="{base}style.css">
{f'<script type="application/ld+json">{ld}</script>' if ld else ''}
</head>
<body>
<div class="wrap">
  <header class="top"><img src="{base}img/tobia-base.svg" alt=""><a href="{base}">Tobia &amp; Co.</a><nav class="menu"><a class="nasc" href="{base}#strumenti">Strumenti</a><a class="nasc" href="{base}diario/">Diario</a><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Offri un caffè</a></nav></header>
  <nav class="briciole"><a href="{base}">🏠 Home</a> › <a href="{base}voli/">Voli</a> › {briciola}</nav>
  <span class="occhiello">{e(occhiello)}</span>
  <h1>{e(h1)}</h1>
  <p class="lead">{lead}</p>
{corpo}
  <h2>Calcola il tuo caso</h2>
  {MODULO}
  <div class="card caffe-box"><div><b>Non hai tempo di occupartene?</b><p class="note">AirHelp gestisce la richiesta al posto tuo e trattiene una percentuale solo se vince.</p><a class="btn blu" href="{airhelp(contenuto_aff)}" rel="sponsored noopener" onclick="window.tobiaConta&&tobiaConta('clic-affiliato-voli')">Fallo gestire a un esperto ›</a><p class="note" style="margin:10px 0 0">{e(AVVISO)}</p></div></div>
  <div class="card"><h2 style="margin-top:0">🧳 Altri problemi col volo?</h2><p><a href="{base}bagaglio/">Bagaglio perso, in ritardo o rotto</a> · <a href="{base}tasse-aeroportuali/">Non sei partito? Riprenditi le tasse</a> · <a href="{base}voli/sciopero/">Sciopero</a> · <a href="{base}voli/volo-cancellato/">Volo cancellato</a> · <a href="{base}voli/overbooking/">Overbooking</a> · <a href="{base}voli/coincidenza-persa/">Coincidenza persa</a> · <a href="{base}voli/compagnia/">Tutte le compagnie</a> · <a href="{base}voli/aeroporto/">Tutti gli aeroporti</a></p></div>
  <p class="note">📚 <a href="{T['fonte_url']}" rel="noopener">{e(T['fonte'])}</a></p>
  <footer><a href="{base}">← Tutti gli strumenti</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ti è stato utile? Offri un caffè</a> · Pagina creata da Tobia, un'intelligenza artificiale (Claude). Informazioni generali, non consulenza legale; non siamo collegati alle compagnie aeree citate.</footer>
</div>
<script>window.T={json.dumps(T, ensure_ascii=False)};window.BASE="{base}";</script>
<script src="{base}js/voli.js" defer></script>
<script src="{base}js/conta.js" defer></script>
</body>
</html>
"""

def scrivi(perc, testo):
    pathlib.Path(perc).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(perc) / "index.html").write_text(testo, encoding="utf-8")

TABELLA = """<table>
    <tr><td>Fino a 1.500 km</td><td class="prezzo">250 €</td></tr>
    <tr><td>Da 1.500 a 3.500 km (e tutti i voli dentro l'UE oltre 1.500 km)</td><td class="prezzo">400 €</td></tr>
    <tr><td>Oltre 3.500 km</td><td class="prezzo">600 €</td></tr>
  </table>
  <p class="note">A persona, per ritardi all'arrivo di almeno 3 ore, cancellazioni avvisate meno di 14 giorni prima o imbarco negato. Non spetta se la causa è davvero straordinaria (maltempo, sciopero dei controllori di volo…): lo sciopero del personale della compagnia invece non la esonera.</p>"""

uscite = []
for nome, iata, paese, tipo, nota in COMPAGNIE:
    s = slug(nome); perc = f"voli/compagnia/{s}/"
    titolo = f"Volo {nome} in ritardo o cancellato? Rimborso fino a 600 €"
    descr = f"Volo {nome} ({iata}) in ritardo di oltre 3 ore, cancellato o overbooking? Scopri se vale il Regolamento UE 261/2004, quanto ti spetta (250, 400 o 600 €) e chiedilo con la lettera pronta. Gratis."
    corpo = f"""  <div class="card">
    <h2 style="margin-top:0">✈️ {e(nome)}</h2><p class="note">Codice volo {e(iata)} · {e(paese)}</p>
    <p>{REGOLA[tipo]}</p>{f'<p class="note">{e(nota)}</p>' if nota else ''}
    <h3>Quanto ti spetta</h3>
  {TABELLA}
  </div>
  <div class="card">
    <h2 style="margin-top:0">📝 Cosa fare, in 3 passi</h2>
    <ol class="passi-lista">
      <li>Conserva carta d'imbarco e prenotazione, e annota l'orario reale di arrivo (conta quando si aprono le porte).</li>
      <li>Calcola qui sotto quanto ti spetta: ti preparo anche la lettera da mandare a {e(nome)}, dal modulo reclami sul suo sito.</li>
      <li>Se non risponde entro 2 mesi o rifiuta senza motivo, puoi fare reclamo all'ENAC (voli da o per l'Italia) o farti aiutare.</li>
    </ol>
    <p class="note">Oltre alla compensazione, in caso di attesa lunga la compagnia deve darti pasti e bevande e, se serve, l'albergo. Se il volo è cancellato puoi scegliere tra rimborso del biglietto e un volo alternativo.</p>
  </div>"""
    scrivi(perc, pagina(perc, titolo, descr, f'<a href="../">Compagnie</a> › {e(nome)}', "Regolamento UE 261/2004",
                        f"✈️ Volo {nome} in ritardo o cancellato?",
                        f"Con {e(nome)} in ritardo di oltre 3 ore, un volo cancellato o l'imbarco negato possono spettarti <b>fino a 600 € a persona</b>. Ti dico se vale per il tuo volo e ti preparo la richiesta.",
                        corpo, "compagnia-" + s, faq=[
        (f"Quanto spetta se un volo {nome} è in ritardo?", f"Con un ritardo all'arrivo di almeno 3 ore spettano 250 € fino a 1.500 km, 400 € da 1.500 a 3.500 km (e per i voli dentro l'UE oltre 1.500 km) e 600 € oltre 3.500 km, a persona (Regolamento UE 261/2004), salvo circostanze straordinarie."),
        (f"Il Regolamento UE 261/2004 vale per i voli {nome}?", re.sub("<[^>]+>", "", REGOLA[tipo]) + (" " + nota if nota else "")),
        (f"Volo {nome} cancellato per sciopero: spetta il rimborso?", "Se sciopera il personale della compagnia, di norma sì: per la Corte di giustizia UE (C-28/20) non è una circostanza straordinaria. Se scioperano i controllori di volo, la compensazione di solito non spetta, ma resta il diritto al rimborso del biglietto o a un volo alternativo.")]))
    uscite.append((nome, iata, perc))

# elenco delle compagnie
voci = "".join(f'<li><a href="{p.replace("voli/compagnia/", "")}">{e(n)}</a> <span class="note">({e(c)})</span></li>' for n, c, p in sorted(uscite))
corpo = f'  <div class="card"><h2 style="margin-top:0">🛫 Scegli la compagnia</h2><ul class="colonne">{voci}</ul></div>'
scrivi("voli/compagnia/", pagina("voli/compagnia/", "Rimborso volo in ritardo o cancellato: compagnia per compagnia",
       "Ryanair, ITA Airways, easyJet, Wizz Air, Volotea, Lufthansa e altre: per ogni compagnia aerea quando vale il Regolamento UE 261/2004 e quanto ti spetta (fino a 600 €).",
       "Compagnie", "Regolamento UE 261/2004", "✈️ Rimborso volo, compagnia per compagnia",
       "Per ogni compagnia ti dico quando vale il regolamento europeo e quanto ti spetta per un ritardo, una cancellazione o l'overbooking.",
       corpo, "elenco-compagnie"))

# sciopero
corpo = """  <div class="card">
    <h2 style="margin-top:0">⚖️ Sciopero: chi sciopera fa la differenza</h2>
    <table class="tab-info">
      <tr><td>Sciopero del personale della compagnia (piloti, assistenti di volo)</td><td>Di norma <b>la compensazione spetta</b> (fino a 600 €): per la Corte di giustizia UE (sentenza C-28/20 del 23 marzo 2021) non è una circostanza straordinaria.</td></tr>
      <tr><td>Sciopero di controllori di volo, aeroporto o servizi esterni</td><td>Di solito è una circostanza straordinaria: <b>la compensazione non spetta</b>, ma restano gli altri diritti.</td></tr>
      <tr><td>Sempre, qualunque sciopero</td><td>Se il volo è cancellato: <b>rimborso del biglietto o volo alternativo</b>, a tua scelta. Durante l'attesa: pasti, bevande e, se serve, albergo.</td></tr>
    </table>
  </div>
  <div class="card">
    <h2 style="margin-top:0">🕖 In Italia alcuni voli sono garantiti</h2>
    <p>Durante gli scioperi del trasporto aereo in Italia devono comunque partire i voli nelle <b>fasce orarie di garanzia, dalle 7 alle 10 e dalle 18 alle 21</b>, oltre ad alcuni collegamenti essenziali (per esempio con le isole). Controlla l'orario del tuo volo.</p>
    <p>Gli scioperi programmati sono pubblicati sul <a href="https://scioperi.mit.gov.it/" rel="noopener">calendario ufficiale del Ministero dei Trasporti</a>.</p>
  </div>"""
scrivi("voli/sciopero/", pagina("voli/sciopero/", "Sciopero aereo: volo cancellato o in ritardo, ti spetta il rimborso?",
       "Volo cancellato per sciopero? Se scioperano piloti o assistenti di volo della compagnia ti spettano fino a 600 €; se scioperano i controllori di volo no, ma hai diritto al rimborso del biglietto. Le fasce garantite e il calcolo.",
       "Sciopero", "Sciopero aereo", "📢 Volo cancellato per sciopero: cosa ti spetta?",
       "Non tutti gli scioperi sono uguali: se a scioperare è il personale della compagnia, <b>la compensazione fino a 600 € di solito spetta</b>. Ti spiego quando, e ti preparo la richiesta.",
       corpo, "sciopero", faq=[
        ("Volo cancellato per sciopero: spetta il rimborso?", "Il rimborso del biglietto o un volo alternativo spettano sempre. La compensazione fino a 600 € spetta di norma se sciopera il personale della compagnia (Corte di giustizia UE, C-28/20), non se scioperano i controllori di volo o il personale aeroportuale."),
        ("Quali voli sono garantiti durante uno sciopero in Italia?", "I voli in partenza nelle fasce orarie dalle 7 alle 10 e dalle 18 alle 21, oltre ad alcuni collegamenti essenziali.")]))
# ---- pagine per caso: overbooking, coincidenza persa, volo cancellato ----
CASI = [
 ("voli/overbooking/", "Overbooking: imbarco negato", "Imbarco negato per overbooking? Ti spettano subito fino a 600 €",
  "Ti hanno negato l'imbarco perché il volo era pieno? Per il Regolamento UE 261/2004 ti spettano subito 250, 400 o 600 € a persona, più il rimborso del biglietto o un volo alternativo. Come chiederli.",
  "🚫 Imbarco negato per overbooking?",
  "Se il volo è pieno e ti lasciano a terra contro la tua volontà, la compagnia deve pagarti <b>subito</b> una compensazione <b>fino a 600 €</b>, oltre a un volo alternativo o al rimborso.",
  """  <div class="card">
    <h2 style="margin-top:0">✋ Cosa ti spetta</h2>
    <ol class="passi-lista">
      <li><b>Compensazione</b> di 250, 400 o 600 € in base alla distanza, se ti negano l'imbarco contro la tua volontà e ti eri presentato in tempo al check-in. Va pagata subito, in aeroporto, o comunque in tempi brevi.</li>
      <li>A scelta: <b>rimborso del biglietto</b> oppure <b>volo alternativo</b> il prima possibile.</li>
      <li><b>Assistenza</b> durante l'attesa: pasti, bevande, telefonate e, se serve, albergo e trasferimenti.</li>
    </ol>
    <p class="note">Se ti offri volontario per lasciare il posto, vale quello che concordi con la compagnia (buoni, soldi, altro volo): prima di accettare, chiedi per iscritto cosa ti danno. Se ti sposta su un volo che arriva entro 2, 3 o 4 ore dall'orario previsto (in base alla distanza), la compensazione può essere ridotta del 50%.</p>
  {TABELLA}
  </div>""", "overbooking",
  [("Quanto spetta per l'imbarco negato per overbooking?", "Da 250 a 600 € a persona in base alla distanza del volo (Regolamento UE 261/2004), più il rimborso del biglietto o un volo alternativo e l'assistenza durante l'attesa."),
   ("Se accetto di cedere il posto come volontario ho diritto alla compensazione?", "No: ai volontari spetta quello che concordano con la compagnia, oltre al rimborso o al volo alternativo.")]),
 ("voli/coincidenza-persa/", "Coincidenza persa", "Coincidenza persa per un ritardo? Ti spettano fino a 600 €",
  "Hai perso la coincidenza per il ritardo del primo volo? Se avevi un'unica prenotazione e arrivi a destinazione con oltre 3 ore di ritardo, ti spettano fino a 600 € calcolati sulla distanza totale.",
  "🔁 Hai perso la coincidenza?",
  "Se il primo volo era in ritardo e hai perso il secondo, conta il <b>ritardo all'arrivo nella destinazione finale</b>: con oltre 3 ore ti spettano <b>fino a 600 €</b>, calcolati sulla distanza dal primo aeroporto all'ultimo.",
  """  <div class="card">
    <h2 style="margin-top:0">🔎 Quando ti spetta</h2>
    <table class="tab-info">
      <tr><td>Un'unica prenotazione</td><td>I voli devono essere nella <b>stessa prenotazione</b> (un solo codice). Con biglietti separati, il secondo volo non è un problema della prima compagnia.</td></tr>
      <tr><td>Ritardo finale di 3 ore</td><td>Conta l'arrivo all'aeroporto <b>finale</b> (Corte di giustizia UE, causa C-11/11). La distanza è quella in linea d'aria tra la prima partenza e l'ultimo arrivo.</td></tr>
      <tr><td>Partenza dall'Europa</td><td>Se il primo volo parte dall'Unione europea vale anche se lo scalo è fuori Europa (causa C-537/17). Se parti da fuori Europa vale solo con una compagnia europea.</td></tr>
    </table>
    <p class="note">Nel calcolatore qui sotto metti come partenza il <b>primo</b> aeroporto e come arrivo l'<b>ultimo</b>.</p>
  </div>""", "coincidenza",
  [("Ho perso la coincidenza per il ritardo del primo volo: mi spetta un rimborso?", "Sì, se i voli erano in un'unica prenotazione e sei arrivato alla destinazione finale con almeno 3 ore di ritardo: da 250 a 600 € calcolati sulla distanza dalla prima partenza all'ultimo arrivo (Regolamento UE 261/2004, Corte di giustizia UE C-11/11)."),
   ("Vale anche con biglietti separati?", "No: con prenotazioni separate ogni volo è un contratto a sé e la perdita della coincidenza non dà diritto alla compensazione.")]),
 ("voli/volo-cancellato/", "Volo cancellato", "Volo cancellato? Rimborso del biglietto e fino a 600 € di compensazione",
  "Volo cancellato dalla compagnia? Hai diritto al rimborso del biglietto entro 7 giorni o a un volo alternativo, e se ti hanno avvisato meno di 14 giorni prima anche a una compensazione fino a 600 €.",
  "❌ Volo cancellato: cosa ti spetta?",
  "Se la compagnia cancella il volo hai sempre diritto al <b>rimborso del biglietto</b> o a un <b>volo alternativo</b>. E se ti ha avvisato meno di 14 giorni prima, spesso anche a una <b>compensazione fino a 600 €</b>.",
  """  <div class="card">
    <h2 style="margin-top:0">📋 I tuoi diritti</h2>
    <table class="tab-info">
      <tr><td>Sempre</td><td>A scelta: <b>rimborso</b> del biglietto entro 7 giorni (in denaro, non solo buoni) oppure <b>volo alternativo</b>. In attesa: pasti, bevande e, se serve, albergo.</td></tr>
      <tr><td>Avviso 14 giorni prima o più</td><td>Niente compensazione, ma resta il rimborso.</td></tr>
      <tr><td>Avviso tra 7 e 13 giorni</td><td>Compensazione dovuta, salvo che il volo alternativo parta al massimo 2 ore prima e arrivi meno di 4 ore dopo l'orario previsto.</td></tr>
      <tr><td>Avviso meno di 7 giorni prima</td><td>Compensazione dovuta, salvo che il volo alternativo parta al massimo 1 ora prima e arrivi meno di 2 ore dopo.</td></tr>
      <tr><td>Circostanze straordinarie</td><td>Maltempo, sciopero dei controllori di volo, problemi di sicurezza: niente compensazione, ma rimborso e assistenza restano. Lo sciopero del personale della compagnia invece non la esonera.</td></tr>
    </table>
  {TABELLA}
  </div>""", "cancellato",
  [("Volo cancellato: entro quanto devono rimborsarmi?", "Entro 7 giorni, in denaro se lo chiedi (Regolamento UE 261/2004, art. 8). I buoni sono validi solo se li accetti."),
   ("Volo cancellato: quando spetta la compensazione?", "Se la compagnia ti ha avvisato meno di 14 giorni prima e la cancellazione non è dovuta a circostanze straordinarie: da 250 a 600 € a persona, salvo voli alternativi con orari molto vicini a quelli originali.")]),
]
for perc, bric, titolo, descr, h1, lead, corpo, aff, faq in CASI:
    scrivi(perc, pagina(perc, titolo, descr, bric, "Regolamento UE 261/2004", h1, lead, corpo.replace("{TABELLA}", TABELLA), aff, faq=faq))
    uscite.append((bric, "", perc))
json.dump([p for _, _, p in uscite] + ["voli/compagnia/", "voli/sciopero/"], open("data/compagnie.json", "w"))
print(len(uscite), "pagine di compagnie + elenco + sciopero")
