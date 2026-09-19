import json, re, sys, shutil

BOERDERIJ=["koe","paard","ezel","varken","schaap","geit","hond","poes"]
ERF=["kip","haan","eend","gans","kalkoen","duif","kraai","kikker","bij","muis"]

# ---------- geluiden splitsen ----------
snd=json.load(open("sounds_dieren.json")); cred=json.load(open("credits.json"))
missing=[k for k in BOERDERIJ+ERF if k not in snd]
if missing: sys.exit("ontbrekende geluiden: "+str(missing))
b={k:snd[k] for k in BOERDERIJ}; e={k:snd[k] for k in ERF}
bc={k:cred[k] for k in BOERDERIJ if k in cred}; ec={k:cred[k] for k in ERF if k in cred}
json.dump(b,open("sounds_dieren.json","w")); json.dump(e,open("sounds_erf.json","w"))
json.dump(bc,open("credits.json","w"),indent=2); json.dump(ec,open("credits_erf.json","w"),indent=2)
print("geluiden: boerderij",len(b),"| erf",len(e))

# ---------- scene splitsen ----------
GOPEN=re.compile(r"<g[\s>]"); GCLOSE=re.compile(r"</g>")

def remove_animal(svg, key):
    m=re.search(r'data-key="%s"'%re.escape(key), svg)
    if not m: return svg, False
    # buitenste <g transform=...> die dit dier omvat
    start=svg.rfind("<g transform=", 0, m.start())
    if start<0: start=svg.rfind("<g ", 0, m.start())
    # bijpassende </g> zoeken
    depth=0; i=start
    while i < len(svg):
        o=GOPEN.search(svg,i); c=GCLOSE.search(svg,i)
        if c is None: break
        if o and o.start()<c.start():
            depth+=1; i=o.start()+2
        else:
            depth-=1; i=c.end()
            if depth==0: break
    end=i
    # voorafgaande schaduw-ellipse en commentaarregel meenemen
    head=svg.rfind("\n", 0, start)
    prev=svg[:head]
    for _ in range(2):
        ln_start=prev.rfind("\n")
        line=prev[ln_start+1:]
        if ("<!--" in line and "-->" in line) or ('<ellipse' in line and 'opacity="0.16"' in line):
            prev=prev[:ln_start]
        else:
            break
    return prev+svg[end:], True

base=open("scene_dieren.svg").read()

# 1) Boerderij: kleine dieren eruit
s=base
for k in ERF:
    s,ok=remove_animal(s,k)
    if not ok: print("  ! niet gevonden in boerderij:",k)
open("scene_dieren.svg","w").write(s)

# 2) Erf: grote dieren eruit (uit dezelfde basis)
s2=base
for k in BOERDERIJ:
    s2,ok=remove_animal(s2,k)
    if not ok: print("  ! niet gevonden in erf:",k)
s2=s2.replace('aria-label="Boerderij met dieren"','aria-label="Het erf met pluimvee en kleine dieren"')
open("scene_erf.svg","w").write(s2)

for f,grp in (("scene_dieren.svg",BOERDERIJ),("scene_erf.svg",ERF)):
    t=open(f).read()
    have=re.findall(r'data-key="([a-z]+)"',t)
    print(f"{f:20} {len(t):6}B  dieren: {sorted(have)}")
    extra=set(have)-set(grp); miss=set(grp)-set(have)
    if extra: print("   TEVEEL:",extra)
    if miss: print("   MIST:",miss)
