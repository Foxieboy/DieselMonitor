# Dierengeluiden — peuterspel

Een simpel, peuterproof spelletje (±2,5 jaar) met echte dierengeluiden.
Volledig zelfstandige `index.html` (geen server nodig): de geluiden zitten
als data-URI's in de pagina ingesloten.

Live (via GitHub Pages): `…/DieselMonitor/dierengeluiden/`

## Speelvormen

Twee schakelaars boven in beeld combineren tot vier varianten:

- **🎨 Vrij spelen** — tik op een dier → geluid, naam in beeld, confetti.
- **❓ Quiz** — je hoort een geluid, de peuter kiest het juiste dier.
  Goed → confetti + ⭐ + de naam wordt uitgesproken; fout → het dier wiebelt
  en het geluid speelt opnieuw. Geen straf, nooit "game over".
- **🔲 Tegels** — de dieren als grote knoppen.
- **🌳 Boerderij** — de dieren in één grote boerderijtekening (SVG). In de
  quiz wordt dit een "zoek-het-dier-in-de-tekening".

Dieren: koe, hond, poes, varken, schaap, kip, haan, kikker, kraai, bij.

De Nederlandse namen worden (als bonus) uitgesproken via de voorleesstem van
het toestel; de dierengeluiden zelf zijn opnames en spelen altijd af.

## Geluiden — bron & licentie

De opnames komen uit de **ESC-50 dataset**
(https://github.com/karolpiczak/ESC-50), gelicentieerd onder
**Creative Commons BY-NC 3.0** (niet-commercieel, met naamsvermelding).
Per dier is één fragment gekozen, kort geknipt en genormaliseerd.
Zie `src/credits.json` voor de exacte bronbestanden.

## Opnieuw bouwen

De pagina is gegenereerd; om te herbouwen (vereist internettoegang tot
`raw.githubusercontent.com` en een `ffmpeg`):

```bash
cd src
python3 build_sounds.py   # downloadt + knipt geluiden -> sounds.json
python3 build_html.py      # bouwt ../index.html (leest scene.svg + sounds.json)
```

- `scene.svg` — de boerderijtekening (illustratie, vector).
- `build_html.py` — HTML/JS/CSS + inbedding van de geluiden.
- `build_sounds.py` — sourcet en verwerkt de audiofragmenten.
