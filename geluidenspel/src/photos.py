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
SCENES = {}


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
        out.append(
            '<g transform="translate(%.0f,%.0f) scale(1)" data-face="%d"%s>%s'
            '<g class="animal-node" data-key="%s" role="button" aria-label="%s" tabindex="0">'
            '<rect class="hit" x="%.0f" y="%.0f" width="%.0f" height="%.0f"/>'
            '<image data-img="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/></g></g>' % (
                it["x"], it["y"], face, attrs.replace(' data-face="%s"' % face, ""), shadow,
                key, it["name"], -w / 2 - pad, -h - pad, w + 2 * pad, h + 2 * pad,
                key, -w / 2, -h, w, h))
    out.append("</svg>")
    return "\n".join(out)
