"""Chroma-key: knip een onderwerp los van een groen (of magenta) scherm -> WebP met alfa."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage

def cutout(src, dst, max_side=440):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[...,0], a[...,1], a[...,2]
    h, w = r.shape
    border = np.concatenate([a[:4].reshape(-1,3), a[-4:].reshape(-1,3), a[:,:4].reshape(-1,3), a[:,-4:].reshape(-1,3)])
    bg = np.median(border, axis=0)
    # sleutel = hoe sterk een pixel in de "chroma-richting" van het scherm ligt (groen, magenta, cyaan, ...)
    c = bg - bg.mean(); c = c / (np.linalg.norm(c) + 1e-6)
    ch = a - a.mean(axis=2, keepdims=True)
    proj = ch @ c
    orth = np.linalg.norm(ch - proj[..., None] * c, axis=2)
    key = proj - 1.0 * orth          # kleuren die 'naast' de schermkleur liggen blijven staan
    kb = float((bg - bg.mean()) @ c)
    magenta = False
    lo, hi = 0.18 * kb, 0.55 * kb                   # zachte overgang
    alpha = 1.0 - np.clip((key - lo) / (hi - lo), 0, 1)
    # alleen scherm-gebied dat met de rand verbonden is wegknippen
    screen = key > lo
    lab, _ = ndimage.label(screen)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:,0], lab[:,-1]]))) - {0}
    conn = np.isin(lab, list(edge))
    conn = ndimage.binary_dilation(conn, iterations=1)
    # ingesloten gaten (tussen poten, staart): duidelijk schermkleur -> ook weg
    holes = (key > 0.6 * kb) & ~conn
    lab3, n3 = ndimage.label(holes)
    if n3:
        sizes3 = ndimage.sum(holes, lab3, range(1, n3 + 1))
        big = np.isin(lab3, [i + 1 for i, sz in enumerate(sizes3) if sz >= 12])
        conn = conn | ndimage.binary_dilation(big, iterations=2)
    alpha = np.where(conn, alpha, 1.0)
    # losse snippers weg
    fg = alpha > 0.5
    lab2, n2 = ndimage.label(fg)
    if n2 > 1:
        sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
        alpha = np.where(np.isin(lab2, [i+1 for i,s in enumerate(sizes) if s < 0.01*sizes.max()]), 0, alpha)
    # despill: haal de schermkleur-zweem van randen (projectie op de chroma-richting afkappen)
    edge = conn | (alpha < 1)
    spill = np.clip(proj - 4, 0, None)[..., None] * c[None, None, :]
    out_rgb = np.where(edge[..., None], a - spill, a)
    out = np.dstack([np.clip(out_rgb, 0, 255), alpha * 255]).astype(np.uint8)
    img = Image.fromarray(out, "RGBA")
    ys, xs = np.where(alpha > 0.15)
    pad = 6
    img = img.crop((max(xs.min()-pad,0), max(ys.min()-pad,0), min(xs.max()+pad,w), min(ys.max()+pad,h)))
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    img.save(dst, "WEBP", quality=82, method=6)
    return img.size

def check(srcs, out):
    """Toon uitsneden op gras en lucht om randjes te beoordelen."""
    ims=[Image.open(s).convert("RGBA") for s in srcs]
    cell=max(max(i.size) for i in ims)+30
    canvas=Image.new("RGB",(cell*len(ims), cell*2),(255,255,255))
    for k,im in enumerate(ims):
        for row,col in enumerate(((110,170,80),(140,200,240))):
            tile=Image.new("RGBA",(cell,cell),col+(255,))
            tile.alpha_composite(im,((cell-im.size[0])//2,(cell-im.size[1])//2))
            canvas.paste(tile.convert("RGB"),(k*cell,row*cell))
    canvas.thumbnail((1400,700)); canvas.save(out)

if __name__ == "__main__":
    print(cutout(sys.argv[1], sys.argv[2]))
