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
        "vliegtuig":  dict(name="Vliegtuig",  x=700, y=140, h=62,  face=1,  air=1, anim=dict(anim="fly", v=26, a=8, p=10)),
        "helikopter": dict(name="Helikopter", x=260, y=250, h=90,  face=-1, air=1, anim=dict(anim="patrol", v=18, r=110, p=2, a=6)),
        "trein":      dict(name="Trein",      x=600, y=402, h=96,  face=1,  anim=dict(anim="drive", v=40, lane="spoor")),
        "boot":       dict(name="Boot",       x=272, y=478, h=44,  face=1,  anim=dict(anim="swim", v=5, r=12, p=3)),
        "motor":      dict(name="Motor",      x=380, y=568, h=80,  face=1,  anim=dict(anim="drive", v=28, dir=-1, lane="ver")),
        "fiets":      dict(name="Fiets",      x=760, y=568, h=76,  face=1,  anim=dict(anim="drive", v=28, dir=-1, lane="ver")),
        "brandweer":  dict(name="Brandweer",  x=180, y=722, h=128, face=1,  anim=dict(anim="drive", v=34, lane="dicht")),
        "auto":       dict(name="Auto",       x=540, y=722, h=104, face=1,  anim=dict(anim="drive", v=34, lane="dicht")),
        "traktor":    dict(name="Traktor",    x=850, y=722, h=128, face=1,  anim=dict(anim="drive", v=34, lane="dicht")),
    }},
}


def photo_scene(theme, spec, imgs):
    from PIL import Image
    W, H = spec.get("size", (1000, 750))
    out = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">' % (W, H, spec["label"]),
           '<image href="%s" x="0" y="0" width="%d" height="%d" preserveAspectRatio="xMidYMid slice"/>' % (
               data_uri(os.path.join(HERE, "real", theme, "bg.webp")), W, H)]
    # achteraan eerst tekenen: sorteer op grondlijn
    for key, it in sorted(spec["items"].items(), key=lambda kv: kv[1]["y"]):
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
