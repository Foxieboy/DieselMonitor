# Geluidenspel — peuterspel

Een simpel, peuterproof geluidenspel (±2,5 jaar). Op de startpagina kies je
een **thema**; elk thema heeft dezelfde opzet. Volledig zelfstandige
`index.html` (geen server nodig): alle geluiden zitten als data-URI's in de
pagina ingesloten.

Live (via GitHub Pages): `…/DieselMonitor/geluidenspel/`

## Thema's

- 🐮 **Boerderij** — koe, hond, poes, varken, schaap, ezel, kip, haan, kikker, kraai, bij
- 🦁 **Wilde dieren** — leeuw, aap, olifant, uil
- 🚗 **Voertuigen** — auto, motor, fiets, trein, brandweer, traktor, boot, vliegtuig, helikopter
- ➕ ruimte voor meer thema's (zie *Nieuw thema toevoegen*)

## Speelvormen (per thema)

Twee schakelaars combineren tot vier varianten:

- **🎨 Vrij spelen** — tik op een plaatje → geluid, naam in beeld, confetti.
- **❓ Quiz** — je hoort een geluid, de peuter kiest het juiste plaatje.
  Goed → confetti + ⭐ + de naam wordt uitgesproken; fout → het plaatje
  wiebelt en het geluid speelt opnieuw. Geen straf, nooit "game over".
- **🔲 Tegels** — grote knoppen.
- **🌳 Tekening** — alles in één grote habitat-illustratie (boerderij voor
  dieren, straat voor voertuigen). In de quiz wordt dit "zoek-in-de-tekening".

De Nederlandse namen worden (als bonus) uitgesproken via de voorleesstem van
het toestel; de geluiden zelf zijn opnames en spelen altijd af.

## Geluiden — bron & licentie

Echte opnames komen uit meerdere vrij gelicentieerde bronnen:
- **ESC-50** (https://github.com/karolpiczak/ESC-50) — boerderijdieren, **CC BY-NC 3.0**
- **YashNita/Animal-Sound-Dataset** — leeuw, aap, ezel
- **Animal-Sound-Dataset-Research-2019-Sri-Lanka** — olifant, **CC BY-4.0**

Per item is één fragment gekozen, kort geknipt en genormaliseerd. Enkele geluiden zonder ESC-50-bron zijn **gesynthetiseerd**
(`src/add_synth.py`): de **fietsbel**, de **motor** (optrekkend motorgeluid) en
de **boottoeter**. Exacte bronbestanden staan in `src/credits*.json`.

## Opnieuw bouwen

Vereist internettoegang tot `raw.githubusercontent.com` en `ffmpeg`
(bijv. via `pip install imageio-ffmpeg`).

```bash
cd src
python3 build_sounds.py             # dieren  -> sounds_dieren.json
python3 build_sounds_voertuigen.py  # voertuigen -> sounds_voertuigen.json
python3 build_app.py                # bouwt ../index.html (leest scene_*.svg + sounds_*.json)
```

## Nieuw thema toevoegen

1. Maak `src/sounds_<thema>.json` (map key → data-URI mp3).
2. Teken `src/scene_<thema>.svg` met per item een
   `<g class="animal-node" data-key="<key>">…</g>` (met een transparant
   `<rect class="hit">` als ruim tikvlak).
3. Voeg het thema toe in `build_app.py` (`sounds`, `SCENE_*`, en het
   `THEMES`/`THEME_ORDER`-blok met items en emoji's) en herbouw.

## Bestanden

- `index.html` — het volledige spel (gegenereerd, geluiden ingesloten).
- `src/build_app.py` — bouwt de multi-thema pagina (HTML/CSS/JS + inbedding).
- `src/build_sounds*.py` — sourcet/verwerkt de audiofragmenten.
- `src/scene_*.svg` — de habitat-tekeningen (illustratie, vector).
- `src/sounds_*.json`, `src/credits*.json` — geluiden + bronvermelding.
