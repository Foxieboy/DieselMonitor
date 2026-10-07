"""Realistische foto's (gegenereerd met Hugging Face-beeldmodellen, zie README).

real/<thema>/<key>.webp  - uitgeknipt onderwerp (alfa), via cutout.py
real/<thema>/bg.webp     - lege achtergrond voor de tekening

Een thema schakelt pas over op foto's als *alle* items een foto hebben (geen
mengelmoes van emoji en foto's). De foto-tekening komt er als ook bg.webp
bestaat en het thema in SCENES staat.
"""
import base64, os

HERE = os.path.dirname(os.path.abspath(__file__))


def data_uri(path):
    return "data:image/webp;base64," + base64.b64encode(open(path, "rb").read()).decode()


def photo_path(theme, key):
    return os.path.join(HERE, "real", theme, key + ".webp")


def theme_photos(theme, keys):
    """{key: data-uri} als alle keys een foto hebben, anders {}."""
    if not all(os.path.exists(photo_path(theme, k)) for k in keys):
        return {}
    return {k: data_uri(photo_path(theme, k)) for k in keys}


# ---- foto-tekeningen ----
# Per item: x = midden, y = voeten (grondlijn), h = hoogte in tekening-eenheden,
# face = kijkrichting van de foto (1 rechts, -1 links), plus bewegings-attributen
# (zie animate_scenes.py). Achtergrond: 1000 x 750.
SCENES = {
    # weide: hek op y~435 (ca. 50 eenheden = 1,2 m); achterste rij ~100/m, voorste ~130/m
    "dieren": {"label": "Foto van een weide met boerderijdieren", "items": {
        "koe":    dict(name="Koe",    x=290, y=575, h=150, face=-1, anim=dict(anim="patrol", v=10, r=45, p=5, peck=1)),
        "ezel":   dict(name="Ezel",   x=535, y=565, h=128, face=-1, anim=dict(anim="breathe", p=3.2)),
        "paard":  dict(name="Paard",  x=790, y=580, h=170, face=-1, anim=dict(anim="patrol", v=16, r=55, p=4, peck=1)),
        "varken": dict(name="Varken", x=135, y=705, h=125, face=-1, anim=dict(anim="patrol", v=12, r=35, p=4, peck=1)),
        "schaap": dict(name="Schaap", x=375, y=715, h=140, face=1,  anim=dict(anim="patrol", v=9, r=30, p=5, peck=1)),
        "geit":   dict(name="Geit",   x=600, y=710, h=135, face=1,  anim=dict(anim="hop", a=10, p=6)),
        "hond":   dict(name="Hond",   x=790, y=700, h=100,  face=-1, anim=dict(anim="patrol", v=28, r=40, p=2.5)),
        "poes":   dict(name="Poes",   x=925, y=742, h=74,  face=1,  anim=dict(anim="breathe", p=2.6)),
    }},
    # woonkamer: plint/vloer op y~578, ~190 eenheden per meter aan de muur.
    # kleine spullen staan (iets vergroot) op een wandplank.
    "huis": {"label": "Foto van een kamer in huis", "decor": (
        '<defs><linearGradient id="plank" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#c79a63"/><stop offset="1" stop-color="#8f6234"/></linearGradient></defs>'
        '<rect x="392" y="336" width="380" height="22" rx="3" fill="#000" opacity="0.10"/>'
        '<path d="M430 344 v34 l22 -34z M734 344 v34 l-22 -34z" fill="#7b5430"/>'
        '<rect x="385" y="328" width="385" height="16" rx="3" fill="url(#plank)"/>'), "items": {
        "kloppen":       dict(name="Deur",          x=120, y=580, h=400, face=1, air=1),
        "klok":          dict(name="Klok",          x=300, y=580, h=380, face=1),
        "wekker":        dict(name="Wekker",        x=440, y=330, h=75,  face=1, air=1, anim=dict(anim="wiggle", p=5)),
        "blikje":        dict(name="Blikje",        x=515, y=330, h=72,  face=1, air=1),
        "tandenborstel": dict(name="Tandenborstel", x=610, y=330, h=18,  face=1, air=1),
        "water":         dict(name="Water",         x=718, y=330, h=125, face=1, air=1),
        "wasmachine":    dict(name="Wasmachine",    x=520, y=592, h=165, face=1, anim=dict(anim="wiggle", p=4, a=2)),
        "wc":            dict(name="Wc",            x=700, y=594, h=150, face=1),
        "stofzuiger":    dict(name="Stofzuiger",    x=860, y=665, h=120, face=1, anim=dict(anim="patrol", v=18, r=40, p=2)),
    }},
    # savanne: horizon y~450; achterste rij ~60 eenheden/m, voorste ~100/m.
    # uil en papegaai zitten op een tak die van buiten beeld komt (tak raakt de rand).
    "wild": {"label": "Foto van de savanne met wilde dieren", "items": {
        "adelaar":   dict(name="Adelaar",   x=500, y=170, h=80,  face=1,  air=1, z=9999, anim=dict(anim="fly", v=26, a=18, p=9)),
        "papegaai":  dict(name="Papegaai",  x=108, y=330, h=280, face=-1, air=1),
        "uil":       dict(name="Uil",       x=938, y=270, h=180, face=1,  air=1),
        "olifant":   dict(name="Olifant",   x=165, y=585, h=190, face=-1, anim=dict(anim="patrol", v=7, r=25, p=5)),
        "neushoorn": dict(name="Neushoorn", x=420, y=585, h=100, face=-1, anim=dict(anim="patrol", v=8, r=30, p=5)),
        "nijlpaard": dict(name="Nijlpaard", x=650, y=588, h=95,  face=-1, anim=dict(anim="breathe", p=3.6)),
        "gorilla":   dict(name="Gorilla",   x=845, y=590, h=90,  face=1,  anim=dict(anim="breathe", p=3)),
        "leeuw":     dict(name="Leeuw",     x=110, y=728, h=125, face=-1, anim=dict(anim="breathe", p=3.4)),
        "tijger":    dict(name="Tijger",    x=330, y=730, h=95,  face=-1, anim=dict(anim="patrol", v=15, r=40, p=3)),
        "aap":       dict(name="Aap",       x=525, y=732, h=95,  face=1,  anim=dict(anim="breathe", p=2.2)),
        "wolf":      dict(name="Wolf",      x=705, y=728, h=95,  face=1,  anim=dict(anim="patrol", v=18, r=40, p=3)),
        "vos":       dict(name="Vos",       x=905, y=735, h=55,  face=-1, anim=dict(anim="patrol", v=20, r=35, p=3)),
    }},
    "erf": {"label": "Foto van het erf met dieren", "items": {
        "kraai":   dict(name="Kraai",   x=250, y=190, h=125,  face=1,  air=1, anim=dict(anim="fly", v=30, a=14, p=7)),
        "bij":     dict(name="Bij",     x=560, y=390, h=75,  face=1,  air=1, anim=dict(anim="hover", r=45, p=7)),
        "duif":    dict(name="Duif",    x=720, y=470, h=85,  face=1,  anim=dict(anim="patrol", v=12, r=30, p=3, peck=1)),
        "eend":    dict(name="Eend",    x=225, y=475, h=110,  face=-1, anim=dict(anim="patrol", v=9, r=30, p=3, peck=1)),
        "kikker":  dict(name="Kikker",  x=355, y=462, h=82,  face=1,  anim=dict(anim="hop", a=18, p=4.5)),
        "kip":     dict(name="Kip",     x=440, y=575, h=150, face=-1, anim=dict(anim="patrol", v=14, r=45, p=2.5, peck=1)),
        "haan":    dict(name="Haan",    x=640, y=610, h=185, face=1,  anim=dict(anim="patrol", v=10, r=30, p=4, peck=1)),
        "gans":    dict(name="Gans",    x=125, y=660, h=185, face=-1, anim=dict(anim="patrol", v=12, r=35, p=3, peck=1)),
        "kalkoen": dict(name="Kalkoen", x=845, y=665, h=205, face=-1, anim=dict(anim="patrol", v=9, r=30, p=4, peck=1)),
        "muis":    dict(name="Muis",    x=330, y=725, h=82,  face=-1, anim=dict(anim="patrol", v=30, r=30, p=3)),
    }},
    "voertuigen": {"label": "Foto van een straat met voertuigen", "items": {
        "vliegtuig":  dict(name="Vliegtuig",  x=700, y=120, h=55,  face=1,  air=1, anim=dict(anim="fly", v=26, a=8, p=10)),
        "helikopter": dict(name="Helikopter", x=260, y=200, h=80,  face=-1, air=1, anim=dict(anim="patrol", v=18, r=110, p=2, a=6)),
        "trein":      dict(name="Trein",      x=600, y=430, h=72,  face=1,  anim=dict(anim="drive", v=40, lane="spoor")),
        "boot":       dict(name="Boot",       x=500, y=712, h=75,  face=1,  anim=dict(anim="swim", v=10, r=250, p=4)),
        "motor":      dict(name="Motor",      x=300, y=505, h=70,  face=1,  anim=dict(anim="drive", v=28, dir=-1, lane="ver")),
        "fiets":      dict(name="Fiets",      x=870, y=505, h=62,  face=1,  anim=dict(anim="drive", v=28, dir=-1, lane="ver")),
        "brandweer":  dict(name="Brandweer",  x=175, y=598, h=150, face=1,  anim=dict(anim="drive", v=34, lane="dicht")),
        "auto":       dict(name="Auto",       x=667, y=598, h=95, face=1,  anim=dict(anim="drive", v=34, lane="dicht")),
        "traktor":    dict(name="Traktor",    x=1071, y=598, h=135, face=1,  anim=dict(anim="drive", v=34, lane="dicht")),
    }},
}


def photo_scene(theme, spec, imgs):
    from PIL import Image
    W, H = spec.get("size", (1000, 750))
    out = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">' % (W, H, spec["label"]),
           '<image href="%s" x="0" y="0" width="%d" height="%d" preserveAspectRatio="xMidYMid slice"/>' % (
               data_uri(os.path.join(HERE, "real", theme, "bg.webp")), W, H)]
    if spec.get("decor"):
        out.append(spec["decor"])
    # achteraan eerst tekenen: sorteer op grondlijn (z = optionele voorrang, bv. vliegende vogel)
    for key, it in sorted(spec["items"].items(), key=lambda kv: kv[1].get("z", kv[1]["y"])):
        iw, ih = Image.open(photo_path(theme, key)).size
        h = it["h"]; w = h * iw / ih
        anim = dict(it.get("anim", {}))
        attrs = "".join(' data-%s="%s"' % (k, v) for k, v in anim.items())
        face = it.get("face", 1)
        # het groepje staat met (0,0) op de voeten; zweven (vliegen) = geen schaduw
        shadow = "" if it.get("air") else '<ellipse cx="0" cy="-2" rx="%.0f" ry="%.0f" fill="#1d2a12" opacity="0.28"/>' % (w * 0.42, max(4, h * 0.05))
        pad = max(14, 0.12 * h)
        padx = max(pad, (110 - w) / 2); pady = max(pad, (110 - h) / 2)   # kleine dieren: ruim tikvlak
        out.append(
            '<g transform="translate(%.0f,%.0f) scale(1)" data-face="%d"%s>%s'
            '<g class="animal-node" data-key="%s" role="button" aria-label="%s" tabindex="0">'
            '<rect class="hit" x="%.0f" y="%.0f" width="%.0f" height="%.0f"/>'
            '<image data-img="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/></g></g>' % (
                it["x"], it["y"], face, attrs.replace(' data-face="%s"' % face, ""), shadow,
                key, it["name"], -w / 2 - padx, -h - pady, w + 2 * padx, h + 2 * pady,
                key, -w / 2, -h, w, h))
    out.append("</svg>")
    return "\n".join(out)
