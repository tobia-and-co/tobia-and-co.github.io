"""Carlo il Cambiavalute: scarica ogni giorno i cambi di riferimento ufficiali della BCE in data/cambi.json."""
import json, re, urllib.request
URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
xml = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "TobiaAndCo/1.0"}), timeout=60).read().decode()
data = re.search(r"time=['\"](\d{4}-\d{2}-\d{2})['\"]", xml).group(1)
cambi = {v: float(r) for v, r in re.findall(r"currency=['\"]([A-Z]{3})['\"]\s+rate=['\"]([\d.]+)['\"]", xml)}
assert len(cambi) > 20, "pochi cambi letti"
json.dump({"data": data, "fonte": "BCE – tassi di cambio di riferimento", "eur": cambi}, open("data/cambi.json", "w"), indent=1)
print(data, len(cambi), "valute")
