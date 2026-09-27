"""Overzichtsblad van alle foto's tot nu toe: python3 sheet.py out.png"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
NAMES = {}
for t in sorted(os.listdir("real")):
    if os.path.isdir("real/"+t):
        for f in sorted(os.listdir("real/"+t)):
            if f.endswith(".webp") and f != "bg.webp":
                NAMES[(t, f[:-5])] = f[:-5].capitalize()
items = list(NAMES.items())
cell=(360,400); cols=4; rows=(len(items)+cols-1)//cols
W,H=cols*cell[0]+40, rows*cell[1]+130
c=Image.new("RGB",(W,H),(246,241,230)); d=ImageDraw.Draw(c)
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=ImageFont.truetype(F,34); tfont=ImageFont.truetype(F,42)
d.text((W//2,52),"Geluidenspel – echte foto's (%d)" % len(items),fill=(61,44,78),font=tfont,anchor="mm")
for i,((t,k),n) in enumerate(items):
    x0=20+(i%cols)*cell[0]; y0=100+(i//cols)*cell[1]
    d.rounded_rectangle((x0+10,y0+10,x0+cell[0]-10,y0+cell[1]-10),28,fill=(255,255,255))
    im=Image.open(f"real/{t}/{k}.webp").convert("RGBA"); im.thumbnail((300,300))
    c.paste(im,(x0+(cell[0]-im.size[0])//2, y0+20+(300-im.size[1])//2), im)
    d.text((x0+cell[0]//2,y0+cell[1]-45),n,fill=(61,44,78),font=font,anchor="mm")
c.save(sys.argv[1] if len(sys.argv)>1 else "fotos_tot_nu.png")
