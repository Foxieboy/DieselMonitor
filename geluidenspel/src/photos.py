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
    "dieren": {"persp": (325, 0.43), "label": "Foto van een weide met boerderijdieren", "items": {
        "koe":    dict(name="Koe",    x=290, y=575, m=1.55, face=-1, anim=dict(anim="patrol", v=10, r=45, p=5, peck=1)),
        "ezel":   dict(name="Ezel",   x=535, y=565, m=1.45, face=-1, anim=dict(anim="breathe", p=3.2)),
        "paard":  dict(name="Paard",  x=790, y=580, m=2.05, face=-1, anim=dict(anim="patrol", v=16, r=55, p=4, peck=1)),
        "varken": dict(name="Varken", x=150, y=705, m=0.9, face=-1, anim=dict(anim="patrol", v=12, r=35, p=4, peck=1)),
        "schaap": dict(name="Schaap", x=375, y=715, m=1.0, face=1,  anim=dict(anim="patrol", v=9, r=30, p=5, peck=1)),
        "geit":   dict(name="Geit",   x=600, y=710, m=1.05, face=1,  anim=dict(anim="hop", a=10, p=6)),
        "hond":   dict(name="Hond",   x=790, y=700, m=0.72,  face=-1, anim=dict(anim="patrol", v=28, r=40, p=2.5)),
        "poes":   dict(name="Poes",   x=925, y=742, m=0.3,  face=1,  anim=dict(anim="breathe", p=2.6)),
    }},
    # woonkamer: plint/vloer op y~578, ~190 eenheden per meter aan de muur.
    # kleine spullen staan (iets vergroot) op een wandplank.
    "huis": {"persp": (352, 0.833), "label": "Foto van een kamer in huis", "decor": (
        '<defs><linearGradient id="plank" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#c79a63"/><stop offset="1" stop-color="#8f6234"/></linearGradient></defs>'
        '<rect x="392" y="336" width="380" height="22" rx="3" fill="#000" opacity="0.10"/>'
        '<path d="M430 344 v34 l22 -34z M734 344 v34 l-22 -34z" fill="#7b5430"/>'
        '<rect x="385" y="328" width="385" height="16" rx="3" fill="url(#plank)"/>'), "items": {
        "kloppen":       dict(name="Deur",          x=120, y=580, h=400, face=1, air=1),
        "klok":          dict(name="Klok",          x=300, y=580, m=2.0, face=1),
        "wekker":        dict(name="Wekker",        x=440, y=330, m=0.17, sy=580, f=1.6,  face=1, air=1, anim=dict(anim="wiggle", p=5)),
        "blikje":        dict(name="Blikje",        x=515, y=330, m=0.12, sy=580, f=1.6,  face=1, air=1),
        "tandenborstel": dict(name="Tandenborstel", x=610, y=330, mw=0.19, sy=580, f=1.6,  face=1, air=1),
        "water":         dict(name="Water",         x=718, y=330, m=0.32, sy=580, f=1.6, face=1, air=1),
        "wasmachine":    dict(name="Wasmachine",    x=520, y=592, m=0.85, face=1, anim=dict(anim="wiggle", p=4, a=2)),
        "wc":            dict(name="Wc",            x=700, y=594, m=0.78, face=1),
        "stofzuiger":    dict(name="Stofzuiger",    x=860, y=665, m=0.55, face=1, anim=dict(anim="patrol", v=18, r=40, p=2)),
    }},
    # tuin: schuurtje recht van voren, grond bij de schuur op y~547; gereedschap ligt
    # (iets vergroot) op een werkbank op het gras, grasmaaier rijdt heen en weer.
    "klus": {"persp": (358, 0.66), "label": "Foto van een tuin met gereedschap", "decor": (
        '<defs><linearGradient id="bank" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#c99a62"/><stop offset="1" stop-color="#94673a"/></linearGradient></defs>'
        '<ellipse cx="775" cy="700" rx="235" ry="14" fill="#1d2a12" opacity="0.28"/>'
        '<rect x="572" y="588" width="18" height="110" fill="#7b5430"/><rect x="962" y="588" width="18" height="110" fill="#7b5430"/>'
        '<rect x="600" y="600" width="12" height="96" fill="#6a4628"/><rect x="940" y="600" width="12" height="96" fill="#6a4628"/>'
        '<rect x="575" y="655" width="400" height="10" fill="#8a5f35"/>'
        '<rect x="556" y="572" width="438" height="20" rx="3" fill="url(#bank)"/>'), "items": {
        "hamer":      dict(name="Hamer",      x=620, y=582, mw=0.33, sy=690,  face=1,  air=1),
        "handzaag":   dict(name="Handzaag",   x=745, y=582, mw=0.55, sy=690,  face=1,  air=1),
        "boor":       dict(name="Boor",       x=885, y=584, m=0.24, sy=690,  face=1,  air=1, anim=dict(anim="wiggle", p=5)),
        "schaar":     dict(name="Schaar",     x=900, y=740, mw=0.6,  face=1),
        "kettingzaag":dict(name="Kettingzaag",x=480, y=732, mw=0.8,  face=1,  anim=dict(anim="wiggle", p=4)),
        "grasmaaier": dict(name="Grasmaaier", x=200, y=722, mw=1.45, face=-1, anim=dict(anim="patrol", v=16, r=60, p=2)),
    }},
    # savanne: horizon y~450; achterste rij ~60 eenheden/m, voorste ~100/m.
    # uil en papegaai zitten op een tak die van buiten beeld komt (tak raakt de rand).
    "wild": {"persp": (450, 0.46), "label": "Foto van de savanne met wilde dieren", "items": {
        "adelaar":   dict(name="Adelaar",   x=500, y=170, h=80,  face=1,  air=1, z=9999, anim=dict(anim="fly", v=26, a=18, p=9)),
        "papegaai":  dict(name="Papegaai",  x=108, y=330, h=280, face=-1, air=1),
        "uil":       dict(name="Uil",       x=957, y=262, h=120, face=1,  air=1),
        "olifant":   dict(name="Olifant",   x=165, y=585, m=3.2, face=-1, anim=dict(anim="patrol", v=7, r=25, p=5)),
        "neushoorn": dict(name="Neushoorn", x=420, y=585, m=1.8, face=-1, anim=dict(anim="patrol", v=8, r=30, p=5)),
        "nijlpaard": dict(name="Nijlpaard", x=650, y=588, m=1.5,  face=-1, anim=dict(anim="breathe", p=3.6)),
        "gorilla":   dict(name="Gorilla",   x=845, y=590, m=1.3,  face=1,  anim=dict(anim="breathe", p=3)),
        "leeuw":     dict(name="Leeuw",     x=110, y=728, m=1.2, face=-1, anim=dict(anim="breathe", p=3.4)),
        "tijger":    dict(name="Tijger",    x=330, y=730, m=1.05,  face=-1, anim=dict(anim="patrol", v=15, r=40, p=3)),
        "aap":       dict(name="Aap",       x=525, y=732, m=0.85,  face=1,  anim=dict(anim="breathe", p=2.2)),
        "wolf":      dict(name="Wolf",      x=705, y=728, m=0.85,  face=1,  anim=dict(anim="patrol", v=18, r=40, p=3)),
        "vos":       dict(name="Vos",       x=905, y=735, m=0.45,  face=-1, anim=dict(anim="patrol", v=20, r=35, p=3)),
    }},
    # speelkamer: muur recht van voren, plint/vloer op y~555 (~230 eenheden per meter aan de muur).
    # grote mensen en de lachende peuter zitten op een bank (voorkant over de onderkant van de foto).
    "mensen": {"persp": (279, 0.833), "label": "Foto van een speelkamer met mensen", "decor": (
        '<defs><linearGradient id="bank2" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#8fb0bb"/><stop offset="1" stop-color="#5f8290"/></linearGradient></defs>'
        '<ellipse cx="390" cy="578" rx="290" ry="11" fill="#3a2a1a" opacity="0.25"/>'
        '<rect x="130" y="360" width="520" height="150" rx="30" fill="url(#bank2)"/>'
        '<rect x="150" y="458" width="480" height="30" rx="10" fill="#9dbcc6"/>'
        '<rect x="96" y="640" width="250" height="40" rx="14" fill="#f3d27a"/>'
        '<rect x="96" y="672" width="250" height="10" rx="5" fill="#d9b25a"/>'), "front": (
        '<g pointer-events="none">'
        '<rect x="135" y="563" width="14" height="16" fill="#5b3d22"/><rect x="631" y="563" width="14" height="16" fill="#5b3d22"/>'
        '<rect x="150" y="478" width="480" height="86" rx="14" fill="url(#bank2)"/>'
        '<path d="M160 486 h460" stroke="#a9c6cf" stroke-width="3" opacity="0.6"/>'
        '<rect x="106" y="420" width="72" height="146" rx="26" fill="url(#bank2)"/>'
        '<rect x="602" y="420" width="72" height="146" rx="26" fill="url(#bank2)"/>'
        '<path d="M262 606 q40 -14 84 -4 v46 q-2 8 -12 8 h-84 q-8 -22 12 -50z" fill="#b9d3e2"/>'
        '<path d="M262 606 q40 -14 84 -4" stroke="#e8f1f6" stroke-width="7" fill="none" stroke-linecap="round"/></g>'), "items": {
        "niezen":      dict(name="Niezen",      x=250, y=505, h=190, face=1, air=1, anim=dict(anim="breathe", p=3.2)),
        "lachen":      dict(name="Lachen",      x=395, y=505, h=125, face=1, air=1, anim=dict(anim="breathe", p=1.4)),
        "hoesten":     dict(name="Hoesten",     x=530, y=505, h=195, face=1, air=1, anim=dict(anim="breathe", p=2.6)),
        "klappen":     dict(name="Klappen",     x=730, y=615, m=0.92, face=1, anim=dict(anim="hop", a=8, p=3)),
        "snurken":     dict(name="Snurken",     x=222, y=652, m=0.28,  face=1, air=1, anim=dict(anim="breathe", p=3.4)),
        "baby":        dict(name="Baby",        x=505, y=690, m=0.3,  face=1, anim=dict(anim="sway", a=3, p=2.4)),
        "voetstappen": dict(name="Voetstappen", x=640, y=742, m=0.17,  face=-1, anim=dict(anim="patrol", v=30, r=90, p=1)),
        "drinken":     dict(name="Drinken",     x=875, y=750, h=270, face=1, air=1, z=9000),
    }},
    "erf": {"persp": (357, 0.77), "label": "Foto van het erf met dieren", "items": {
        "kraai":   dict(name="Kraai",   x=250, y=190, h=125, face=1,  air=1, anim=dict(anim="fly", v=30, a=14, p=7)),
        "bij":     dict(name="Bij",     x=540, y=520, h=40,  face=1,  air=1, z=9999, anim=dict(anim="hover", r=45, p=7)),
        "gans":    dict(name="Gans",    x=110, y=560, m=0.85, face=-1, anim=dict(anim="patrol", v=12, r=35, p=3, peck=1)),
        "kalkoen": dict(name="Kalkoen", x=860, y=575, m=1.0, face=-1, anim=dict(anim="patrol", v=9, r=30, p=4, peck=1)),
        "kip":     dict(name="Kip",     x=420, y=598, m=0.45, face=-1, anim=dict(anim="patrol", v=14, r=45, p=2.5, peck=1)),
        "haan":    dict(name="Haan",    x=640, y=612, m=0.65, face=1,  anim=dict(anim="patrol", v=10, r=30, p=4, peck=1)),
        "eend":    dict(name="Eend",    x=250, y=660, m=0.55, face=-1, anim=dict(anim="patrol", v=9, r=30, p=3, peck=1)),
        "duif":    dict(name="Duif",    x=790, y=690, m=0.3, face=1,  anim=dict(anim="patrol", v=12, r=30, p=3, peck=1)),
        "kikker":  dict(name="Kikker",  x=420, y=735, h=48,  face=1,  anim=dict(anim="hop", a=18, p=4.5)),
        "muis":    dict(name="Muis",    x=590, y=730, h=46,  face=-1, anim=dict(anim="patrol", v=30, r=30, p=3)),
    }},
    "voertuigen": {"label": "Foto van een straat met voertuigen", "items": {
        "vliegtuig":  dict(name="Vliegtuig",  x=700, y=120, h=55,  face=1,  air=1, anim=dict(anim="fly", v=26, a=8, p=10)),
        "helikopter": dict(name="Helikopter", x=260, y=200, h=80,  face=-1, air=1, anim=dict(anim="patrol", v=18, r=110, p=2, a=6)),
        "trein":      dict(name="Trein",      x=600, y=430, h=72,  face=1,  anim=dict(anim="drive", v=40, lane="spoor")),
        "boot":       dict(name="Boot",       x=500, y=712, h=115,  face=1,  anim=dict(anim="swim", v=10, r=250, p=4)),
        "motor":      dict(name="Motor",      x=480, y=505, h=70,  face=1,  anim=dict(anim="drive", v=28, dir=-1, lane="ver")),
        "fiets":      dict(name="Fiets",      x=870, y=505, h=52,  face=1,  anim=dict(anim="drive", v=28, dir=-1, lane="ver")),
        "brandweer":  dict(name="Brandweer",  x=175, y=598, h=205, face=1,  anim=dict(anim="drive", v=34, lane="dicht")),
        "auto":       dict(name="Auto",       x=667, y=598, h=95, face=1,  anim=dict(anim="drive", v=34, lane="dicht")),
        "traktor":    dict(name="Traktor",    x=1071, y=598, h=180, face=1,  anim=dict(anim="drive", v=34, lane="dicht")),
    }},
}


def scale_at(spec, y):
    """eenheden per meter op grondlijn y (perspectief van de achtergrond)."""
    hz, k = spec["persp"]
    return k * (y - hz)


def item_height(spec, it, aspect):
    """h rechtstreeks, of uit de werkelijke maat: m = hoogte, mw = breedte (meter).
    sy = diepte voor de schaal als die afwijkt van y (bv. op een bank/plank),
    f = vaste vergroting voor heel kleine voorwerpen (onderling blijven ze kloppen)."""
    if "h" in it:
        return it["h"]
    s = scale_at(spec, it.get("sy", it["y"])) * it.get("f", 1)
    return it["m"] * s if "m" in it else it["mw"] * s / aspect


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
        h = item_height(spec, it, iw / ih); w = h * iw / ih
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
    if spec.get("front"):
        out.append(spec["front"])   # voorgrond (bv. voorkant van een bank) over de items
    out.append("</svg>")
    return "\n".join(out)
