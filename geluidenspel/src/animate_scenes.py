"""Voegt bewegings-attributen (data-anim) toe aan de tekeningen.

Leest scene_base/scene_<thema>.svg en schrijft scene_<thema>.svg. De animatie zelf
gebeurt in de pagina (zie ANIM_JS in build_app.py); hier staat alleen *wat*
er beweegt en hoe:

  drive  - rijdt in een lus van links naar rechts (rijstrook = data-lane)
  fly    - vliegt traag door de lucht, lichte golfbeweging
  drift  - wolk die heel traag voorbijdrijft
  patrol - loopt heen en weer (data-r = halve afstand), pauzeert aan de uiteinden
  swim   - als patrol, maar deinend op het water
  hover  - zweeft in een achtje (bij)
  bob    - deinen (boot)
  hop    - springt af en toe op (kikker)
  breathe- ademt zachtjes
  sway   - schommelt rond een draaipunt (aap aan een tak)
  wiggle - trilt af en toe (wekker, wasmachine)

data-face = 1 als de tekening naar rechts kijkt, -1 als naar links.
Snelheden (data-v) zijn in tekening-eenheden per seconde; de tekening is
1000 breed, dus 30 = ruim 30 seconden om het beeld over te steken.
"""
import re

FLY_V = 30      # vogels/vliegtuig: traag, makkelijk aan te tikken
ROAD_V = 34     # alle auto's op de weg even snel -> botsen nooit

CFG = {
    "dieren": {
        "koe":    dict(anim="patrol", v=10, r=45, p=5, face=-1, peck=1),
        "paard":  dict(anim="patrol", v=16, r=55, p=4, face=-1, peck=1),
        "hond":   dict(anim="patrol", v=28, r=40, p=2.5, face=-1),
        "schaap": dict(anim="patrol", v=9,  r=30, p=5, face=-1, peck=1),
        "varken": dict(anim="patrol", v=12, r=35, p=4, face=-1, peck=1),
        "ezel":   dict(anim="breathe", p=3.2),
        "geit":   dict(anim="hop", a=10, p=6),
        "poes":   dict(anim="breathe", p=2.6),
    },
    "erf": {
        "kraai":  dict(anim="fly", v=FLY_V, a=14, p=7, face=1),
        "kip":    dict(anim="patrol", v=14, r=45, p=2.5, face=-1, peck=1),
        "haan":   dict(anim="patrol", v=10, r=25, p=4, face=-1, peck=1),
        "eend":   dict(anim="swim", v=8, r=40, p=3, face=-1),
        "gans":   dict(anim="patrol", v=12, r=40, p=3, face=-1, peck=1),
        "kalkoen":dict(anim="patrol", v=9,  r=35, p=4, face=-1, peck=1),
        "duif":   dict(anim="breathe", p=1.8),
        "kikker": dict(anim="hop", a=16, p=4.5),
        "bij":    dict(anim="hover", r=38, p=7, face=-1),
        "muis":   dict(anim="patrol", v=34, r=35, p=3, face=-1),
    },
    "wild": {
        "adelaar":  dict(anim="fly", v=FLY_V - 4, a=18, p=9, face=1),
        "aap":      dict(anim="sway", a=5, p=3.4, py=-40),
        "papegaai": dict(anim="breathe", p=2.2),
        "uil":      dict(anim="breathe", p=3),
        "olifant":  dict(anim="patrol", v=7,  r=25, p=5, face=-1),
        "leeuw":    dict(anim="breathe", p=3.4),
        "tijger":   dict(anim="patrol", v=15, r=40, p=3, face=-1),
        "nijlpaard":dict(anim="bob", a=2.5, p=3.6, rot=0),
        "gorilla":  dict(anim="breathe", p=3),
        "wolf":     dict(anim="patrol", v=18, r=40, p=3, face=-1),
        "vos":      dict(anim="patrol", v=20, r=35, p=3, face=-1),
        "neushoorn":dict(anim="patrol", v=8,  r=30, p=5, face=-1),
    },
    "voertuigen": {
        "vliegtuig":  dict(anim="fly", v=FLY_V - 6, a=8, p=10, face=1),
        "helikopter": dict(anim="patrol", v=18, r=80, p=2, face=-1, a=6),
        "trein":      dict(anim="drive", v=40, face=1, lane="rails"),
        "brandweer":  dict(anim="drive", v=ROAD_V, face=1, lane="weg"),
        "auto":       dict(anim="drive", v=ROAD_V, face=1, lane="weg"),
        "traktor":    dict(anim="drive", v=ROAD_V, face=-1, lane="weg"),
        "motor":      dict(anim="drive", v=ROAD_V, face=-1, lane="weg"),
        "fiets":      dict(anim="patrol", v=22, r=190, p=2, face=1),   # niet door het water
        "boot":       dict(anim="swim", v=6, r=35, p=3, face=1),
    },
    "huis": {
        "wekker":     dict(anim="wiggle", p=5),
        "wasmachine": dict(anim="wiggle", p=4, a=2),
        "stofzuiger": dict(anim="patrol", v=18, r=18, p=2, face=1),
    },
    "klus": {
        "grasmaaier": dict(anim="patrol", v=16, r=30, p=2, face=1),
    },
    "mensen": {
        "baby":    dict(anim="sway", a=3, p=2.4, py=40),
        "snurken": dict(anim="breathe", p=3.4, a=3),
        "lachen":  dict(anim="breathe", p=1.4),
    },
}

MOVING = {"drive", "fly", "patrol", "swim", "hover"}


def tag_nodes(svg, cfg):
    for key, c in cfg.items():
        pat = re.compile(r'<g transform="translate\(([-\d.]+),([-\d.]+)\)(?: scale\(([-\d.]+)\))?">(\s*(?:<[a-z]+[^>]*/>\s*)?)<g class="animal-node" data-key="%s"' % key)
        m = pat.search(svg)
        if not m:
            raise SystemExit("node niet gevonden: %s" % key)
        attrs = "".join(' data-%s="%s"' % (k, v) for k, v in c.items())
        x, y, s = float(m.group(1)), float(m.group(2)), float(m.group(3) or 1)
        head = '<g transform="translate(%s,%s) scale(%s)"%s>' % (m.group(1), m.group(2), m.group(3) or 1, attrs)
        inner = m.group(4)
        # bewegende items: schaduw meenemen in de groep
        if c["anim"] in MOVING and c["anim"] not in ("fly", "hover"):
            svg, sh = steal_shadow(svg, x, y, s)
            if sh:
                m = pat.search(svg)          # posities zijn verschoven
                inner = sh + m.group(4)
        svg = svg[:m.start()] + head + inner + svg[m.end() - len('<g class="animal-node" data-key="%s"' % key):]
    return svg


def steal_shadow(svg, x, y, s):
    """Zoek de losse schaduw-ellips onder dit item, haal hem weg en geef hem terug in lokale coördinaten."""
    best = None
    for m in re.finditer(r'<ellipse cx="([-\d.]+)" cy="([-\d.]+)" rx="([-\d.]+)" ry="([-\d.]+)"(?: fill="([^"]+)" opacity="([\d.]+)")?/>', svg):
        cx, cy, rx, ry = map(float, m.group(1, 2, 3, 4))
        if abs(cx - x) < 40 and 0 < cy - y < 110 and ry < 18:
            # kleur/doorzichtigheid: van de ellips zelf of van de omringende schaduwgroep
            fill, op = m.group(5), m.group(6)
            if not fill:
                g = svg.rfind('<g fill="', 0, m.start())
                gm = re.match(r'<g fill="([^"]+)" opacity="([\d.]+)">', svg[g:])
                if not gm:
                    continue
                fill, op = gm.group(1), gm.group(2)
            d = abs(cx - x) + abs(cy - y - 40)
            if best is None or d < best[0]:
                best = (d, m, cx, cy, rx, ry, fill, op)
    if not best:
        return svg, ""
    _, m, cx, cy, rx, ry, fill, op = best
    sh = '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity="%s"/>' % (
        (cx - x) / s, (cy - y) / s, rx / s, ry / s, fill, op)
    return svg[:m.start()] + svg[m.end():], sh


def split_clouds(svg, v=6):
    """Elke wolk een eigen groep die traag voorbijdrijft."""
    def rep(m):
        head, body = m.group(1), m.group(2)
        ells = re.findall(r'<ellipse[^>]*/>', body)
        # groepeer ellipsen per wolk: dicht bij elkaar liggend
        clouds = []
        for e in ells:
            cx = float(re.search(r'cx="([-\d.]+)"', e).group(1))
            for cl in clouds:
                if abs(cl[0] - cx) < 140:
                    cl[1].append(e); break
            else:
                clouds.append([cx, [e]])
        out = []
        for i, (cx, es) in enumerate(clouds):
            out.append('<g transform="translate(0,0)" data-anim="drift" data-v="%d">%s</g>' % (v + 2 * (i % 2), "".join(es)))
        return head + "".join(out) + "</g>"
    return re.sub(r'(<g fill="#ffffff" opacity="0\.\d+">)(.*?)</g>', rep, svg, count=1, flags=re.S)


FLYING_CROW = '''<rect class="hit" x="-62" y="-58" width="124" height="104"/>
      <g class="flap">
        <path d="M-6,-4 q-22,-40 -52,-44 q14,18 18,40 q18,6 34,4z" fill="#171a20"/>
        <path d="M-2,-6 q-10,-30 -30,-40 q6,20 8,36z" fill="#262a32"/>
      </g>
      <ellipse cx="0" cy="0" rx="30" ry="13" fill="#20242b"/>
      <path d="M-26,-2 l-22,-8 l4,10 l-4,10 l22,-6z" fill="#171a20"/>
      <circle cx="28" cy="-6" r="12" fill="#20242b"/>
      <path d="M38,-8 l18,3 l-18,6 z" fill="#f0a52e"/>
      <circle cx="31" cy="-9" r="2.8" fill="#fff"/><circle cx="32" cy="-9" r="1.6" fill="#000"/>
      <g class="flap flap2">
        <path d="M2,2 q20,28 46,30 q-12,-14 -16,-30 q-16,-4 -30,0z" fill="#2c3139"/>
      </g>'''


def redraw_crow(svg):
    # kraai: niet meer op het dak, maar vliegend in de lucht
    svg = svg.replace('<g transform="translate(752,214) scale(0.8)">', '<g transform="translate(300,170) scale(0.85)">')
    start = svg.index('data-key="kraai"')
    a = svg.index('>', start) + 1
    b = svg.index('</g>', svg.index('stroke="#3a2f28" stroke-width="4" stroke-linecap="round"/>', a))
    return svg[:a] + "\n      " + FLYING_CROW + "\n    " + svg[b:]


def main():
    for theme, cfg in CFG.items():
        name = "scene_%s.svg" % theme
        svg = open("scene_base/" + name).read()
        if theme == "erf":
            svg = redraw_crow(svg)
        svg = tag_nodes(svg, cfg)
        if theme in ("dieren", "erf", "wild", "voertuigen"):
            svg = split_clouds(svg)
        if theme == "voertuigen":
            svg = svg.replace('<rect x="-64" y="-40" width="150" height="8" rx="4" fill="#3a3f45"/>',
                              '<rect class="rotor" x="-64" y="-40" width="150" height="8" rx="4" fill="#3a3f45"/>')
        open(name, "w").write(svg)
        print(theme, svg.count("data-anim="))
    for theme in ("klus", "huis", "mensen"):
        pass


if __name__ == "__main__":
    main()
