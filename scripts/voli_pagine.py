"""Crea le pagine del calcolatore voli nelle 5 lingue da data/voli_testi.json."""
import html, json, pathlib

SITO = "https://tobia-and-co.github.io"
TESTI = json.load(open("data/voli_testi.json", encoding="utf-8"))
NOMI = {"it": "Italiano", "en": "English", "es": "Español", "fr": "Français", "de": "Deutsch"}
e = lambda s: html.escape(s, quote=True)

for lingua, T in TESTI.items():
    base = "../" * T["percorso"].count("/")
    altre = " · ".join(f'<a href="{base}{TESTI[l]["percorso"]}" hreflang="{l}">{NOMI[l]}</a>' for l in TESTI if l != lingua)
    alternate = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{SITO}/{TESTI[l]["percorso"]}">' for l in TESTI)
    opz = lambda chiavi: "".join(f'<option value="{v}">{e(T[k])}</option>' for v, k in chiavi)
    pagina = f"""<!doctype html>
<html lang="{lingua}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(T['title'])} | Tobia & Co.</title>
<meta name="description" content="{e(T['description'])}">
<link rel="canonical" href="{SITO}/{T['percorso']}">
{alternate}
<link rel="icon" href="{base}img/tobia-base.svg">
<link rel="stylesheet" href="{base}style.css">
</head>
<body>
<div class="wrap">
  <header class="top"><img src="{base}img/tobia-base.svg" alt=""><a href="{base}">Tobia &amp; Co.</a><nav class="menu"><a class="caffe" href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ko-fi</a></nav></header>
  <nav class="briciole"><a href="{base}">🏠 {e(T['home'])}</a> › {e(T['sezione'])}</nav>
  <span class="occhiello">{e(T['occhiello'])}</span>
  <h1>{e(T['h1'])}</h1>
  <p class="lead">{e(T['lead'])}</p>

  <form class="card" id="modulo" autocomplete="off">
    <label for="da">{e(T['da'])}</label>
    <input id="da" placeholder="{e(T['segnaposto'])}"><div id="da-lista" class="lista"></div>
    <label for="a">{e(T['a'])}</label>
    <input id="a" placeholder="{e(T['segnaposto'])}"><div id="a-lista" class="lista"></div>
    <label class="check"><input type="checkbox" id="ue" checked> {e(T['ue'])}</label>
    <label for="evento">{e(T['evento'])}</label>
    <select id="evento">{opz([('ritardo','e_ritardo'),('cancellato','e_cancellato'),('negato','e_negato')])}</select>
    <div id="box-ritardo"><label for="ritardo">{e(T['ritardo'])}</label>
    <select id="ritardo">{opz([('4','r_4'),('3','r_3'),('2','r_2'),('0','r_0')])}</select></div>
    <div id="box-avviso" hidden><label for="avviso">{e(T['avviso'])}</label>
    <select id="avviso">{opz([('0','a_0'),('7','a_7'),('14','a_14')])}</select></div>
    <label for="causa">{e(T['causa'])}</label>
    <select id="causa">{opz([('tecnico','c_tecnico'),('sciopero','c_sciopero'),('meteo','c_meteo'),('atc','c_atc'),('sicurezza','c_sicurezza')])}</select>
    <p style="margin-top:20px"><button type="submit">✈️ {e(T['calcola'])}</button></p>
  </form>
  <div id="esito"></div>

  <p class="note">📚 <a href="{T['fonte_url']}" rel="noopener">{e(T['fonte'])}</a></p>
  <p class="note">🌍 {e(T['lingue'])}: {altre}</p>
  <footer><a href="{base}">← Tobia &amp; Co.</a> · <a href="https://ko-fi.com/tobiaandco" rel="noopener">☕ Ko-fi</a> · {e(T['avvertenza'])}</footer>
</div>
<script>window.T={json.dumps(T, ensure_ascii=False)};window.BASE="{base}";</script>
<script src="{base}js/voli.js" defer></script>
<script src="{base}js/conta.js" defer></script>
</body>
</html>
"""
    cartella = pathlib.Path(T["percorso"])
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / "index.html").write_text(pagina, encoding="utf-8")
print("pagine voli:", ", ".join(T["percorso"] for T in TESTI.values()))
