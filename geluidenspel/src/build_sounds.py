import csv, subprocess, urllib.request, os, json, wave, base64, struct, sys
import numpy as np
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
UA = {"User-Agent":"ToddlerGame/1.0"}
RAW = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/"

# dutch key -> esc50 category
MAP = [
 ("koe","cow"), ("hond","dog"), ("poes","cat"), ("varken","pig"),
 ("schaap","sheep"), ("kip","hen"), ("haan","rooster"),
 ("kikker","frog"), ("kraai","crow"), ("bij","insects"),
]
NCAND = 4
SR = 22050
WIN = 1.6   # seconds

# collect candidate filenames per category
bycat={}
for r in csv.DictReader(open("esc50.csv")):
    bycat.setdefault(r["category"],[]).append((r["filename"], r["src_file"]))

os.makedirs("dl", exist_ok=True)
os.makedirs("seg", exist_ok=True)

def dl(fn):
    p=os.path.join("dl",fn)
    if not os.path.exists(p):
        req=urllib.request.Request(RAW+fn, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r, open(p,"wb") as f:
            f.write(r.read())
    return p

def to_mono(path):
    out=path+".m.wav"
    subprocess.run([FF,"-y","-i",path,"-ac","1","-ar",str(SR),out],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    w=wave.open(out,"rb"); n=w.getnframes()
    data=np.frombuffer(w.readframes(n),dtype=np.int16).astype(np.float32)/32768.0
    w.close(); os.remove(out)
    return data

def best_window(x):
    W=int(WIN*SR)
    if len(x)<=W: return x, float(np.sqrt(np.mean(x**2)+1e-9))
    e=x*x
    c=np.concatenate([[0],np.cumsum(e)])
    sums=c[W:]-c[:-W]
    i=int(np.argmax(sums))
    seg=x[i:i+W]
    rms=float(np.sqrt(sums[i]/W))
    return seg, rms

def finish(seg):
    # trim leading/trailing near-silence within window
    thr=0.02*np.max(np.abs(seg)+1e-9)
    idx=np.where(np.abs(seg)>thr)[0]
    if len(idx)>0:
        a=max(0,idx[0]-int(0.03*SR)); b=min(len(seg),idx[-1]+int(0.06*SR))
        seg=seg[a:b]
    # normalize peak
    pk=np.max(np.abs(seg))+1e-9
    seg=seg/pk*0.92
    # fades
    fi=int(0.010*SR); fo=int(0.060*SR)
    if len(seg)>fi+fo:
        seg[:fi]*=np.linspace(0,1,fi)
        seg[-fo:]*=np.linspace(1,0,fo)
    return seg

def write_wav(seg,path):
    d=(np.clip(seg,-1,1)*32767).astype(np.int16)
    w=wave.open(path,"wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(d.tobytes()); w.close()

def to_mp3(wavpath):
    mp3=wavpath[:-4]+".mp3"
    r=subprocess.run([FF,"-y","-i",wavpath,"-ac","1","-ar",str(SR),"-b:a","72k",mp3],
                     stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    if r.returncode!=0 or not os.path.exists(mp3):
        return None
    return mp3

result={}; credits={}
for key,cat in MAP:
    cands=bycat.get(cat,[])[:NCAND]
    best=None
    for fn,src in cands:
        try:
            p=dl(fn); x=to_mono(p)
            seg,rms=best_window(x)
            if best is None or rms>best[0]:
                best=(rms, seg, fn, src)
        except Exception as e:
            print(f"  ! {key}/{fn}: {e}", file=sys.stderr)
    if not best:
        print(f"  XX no candidate for {key}"); continue
    rms,seg,fn,src=best
    seg=finish(seg)
    wp=os.path.join("seg",key+".wav"); write_wav(seg,wp)
    mp3=to_mp3(wp)
    if not mp3:
        print(f"  XX mp3 fail {key}"); continue
    b=open(mp3,"rb").read()
    result[key]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
    credits[key]={"file":fn,"freesound_src":src,"bytes":len(b),"dur":round(len(seg)/SR,2),"rms":round(rms,3)}
    print(f"  OK {key:8} <- {fn:22} dur={len(seg)/SR:.2f}s mp3={len(b)}B")

json.dump(result, open("sounds.json","w"))
json.dump(credits, open("credits.json","w"), indent=2)
tot=sum(len(v) for v in result.values())
print(f"\nTotal base64 chars: {tot}  (~{tot/1024:.0f} KB) for {len(result)} sounds")
