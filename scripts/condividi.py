# Riassunto automatico dei numeri del sito, da dare ad altri assistenti AI (ChatGPT ecc.): data/numeri.txt
# Lo rifà Pino ogni mattina. Solo contatori pubblici del sito (già in data/visite.json): niente account, email, ricavi o strategie.
import json, datetime
v = json.load(open('data/visite.json')).get('visite', {})
g = lambda *k: sum((v.get(x) or 0) for x in k)
NOMI = {'home': 'Home', 'squadra': 'Squadra', 'diario': 'Diario', 'carburante': 'Benzina', 'carburante-pagine': 'Benzina città',
        'farmaci-pagine': 'Farmaci', 'carenti-pagine': 'Farmaci carenti', 'voli': 'Voli', 'tratte': 'Tratte voli', 'compagnie': 'Compagnie aeree',
        'en': 'Voli in inglese', 'guide': 'Guide', 'budget-2027': 'Budget 2027', 'scadenze': 'Scadenze', 'banca': 'Banca', 'bolletta': 'Bolletta',
        'treno': 'Treno', 'multe': 'Multe', 'mutuo': 'Mutuo', 'bollo': 'Bollo'}
pag = sorted(((NOMI[k], v.get(k) or 0) for k in NOMI), key=lambda x: -x[1])[:10]
inter = sorted(((k[4:], x) for k, x in v.items() if k.startswith('int-') and x), key=lambda x: -x[1])[:8]
ingr = sorted(((k[4:], x) for k, x in v.items() if k.startswith('ing-') and x), key=lambda x: -x[1])[:8]
righe = [
 f"Tobia & Co. — numeri del sito https://tobia-and-co.pages.dev (aggiornati il {datetime.date.today():%d/%m/%Y}, ogni mattina in automatico)",
 "Sito di strumenti gratuiti con dati ufficiali italiani (rimborsi voli, farmaci, benzina, bollette, guide). Le visite del proprietario e i test automatici sono esclusi.",
 "",
 f"Visite totali dal 31/10/2026: {v.get('totale') or 0}",
 f"Canali: dirette {g('da-diretto')} · motori di ricerca {g('da-google','da-bing','da-altri-motori')} · assistenti AI {g('da-chatgpt','da-claude','da-perplexity','da-gemini')} · altri siti e social {g('da-altri-siti','da-social','da-github')} · vecchio indirizzo {g('da-vecchio-indirizzo')}",
 "Pagine più viste: " + ", ".join(f"{a} {b}" for a, b in pag),
 "Pagine con visitatori interessati (usano lo strumento o restano 30 secondi, dal 14/11): " + (", ".join(f"{a} {b}" for a, b in inter) or "ancora nessun dato"),
 "Pagine d'ingresso da motori (org) e altri siti (ref), dal 14/11: " + (", ".join(f"{a} {b}" for a, b in ingr) or "ancora nessun dato"),
 "",
 "Percorso rimborsi voli (affiliazione AirHelp, paga solo a rimborso vinto): "
 f"visite pagine voli {g('voli','tratte','compagnie','aeroporti','sciopero','overbooking','coincidenza-persa','volo-cancellato','en')} → calcoli del rimborso {v.get('calcoli-voli') or 0} → clic su AirHelp {v.get('clic-affiliato-voli') or 0}",
 "Percorso Budget 2027 (foglio di calcolo digitale, 3,90 €): "
 f"visite alla pagina {v.get('budget-2027') or 0} → interessati {v.get('int-budget-2027') or 0} → clic dai riquadri negli strumenti {v.get('clic-budget-riquadro') or 0} → clic su Acquista {v.get('clic-budget-acquisto') or 0}",
 f"Clic su \"Offri un caffè\" (Ko-fi): {v.get('clic-kofi') or 0}",
 "Nota: i clic non sono vendite; vendite e ricavi non sono in questo file.",
]
open('data/numeri.txt', 'w').write("\n".join(righe) + "\n")
print("\n".join(righe))
