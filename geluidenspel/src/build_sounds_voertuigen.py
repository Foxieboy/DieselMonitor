import csv, subprocess, urllib.request, os, json, wave, base64, sys
import numpy as np
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
UA={"User-Agent":"ToddlerGame/1.0"}
RAW="https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/"
SR=22050; WIN=1.6; NCAND=4

# dutch key -> esc50 category  (fiets = synth)
MAP=[("auto","car_horn"),("trein","train"),("brandweer","siren"),
     ("traktor","engine"),("vliegtuig","airplane"),("helikopter","helicopter")]

bycat={}
for r in csv.DictReader(open("esc50.csv")): bycat.setdefault(r["category"],[]).append((r["filename"],r["src_file"]))
os.makedirs("dl",exist_ok=True); os.makedirs("seg",exist_ok=True)

def dl(fn):
    p=os.path.join("dl",fn)
    if not os.path.exists(p):
        req=urllib.request.Request(RAW+fn,headers=UA)
        with urllib.request.urlopen(req,timeout=60) as r,open(p,"wb") as f: f.write(r.read())
    return p
def to_mono(path):
    out=path+".m.wav"
    subprocess.run([FF,"-y","-i",path,"-ac","1","-ar",str(SR),out],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    w=wave.open(out,"rb");n=w.getnframes();x=np.frombuffer(w.readframes(n),dtype=np.int16).astype(np.float32)/32768.0;w.close();os.remove(out);return x
def best_window(x):
    W=int(WIN*SR)
    if len(x)<=W: return x,float(np.sqrt(np.mean(x**2)+1e-9))
    e=x*x;c=np.concatenate([[0],np.cumsum(e)]);sums=c[W:]-c[:-W];i=int(np.argmax(sums));return x[i:i+W],float(np.sqrt(sums[i]/W))
def finish(seg):
    thr=0.02*np.max(np.abs(seg)+1e-9);idx=np.where(np.abs(seg)>thr)[0]
    if len(idx)>0:
        a=max(0,idx[0]-int(0.03*SR));b=min(len(seg),idx[-1]+int(0.06*SR));seg=seg[a:b]
    seg=seg/(np.max(np.abs(seg))+1e-9)*0.92
    fi=int(0.010*SR);fo=int(0.060*SR)
    if len(seg)>fi+fo: seg[:fi]*=np.linspace(0,1,fi); seg[-fo:]*=np.linspace(1,0,fo)
    return seg
def write_wav(seg,path):
    d=(np.clip(seg,-1,1)*32767).astype(np.int16);w=wave.open(path,"wb");w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(d.tobytes());w.close()
def to_mp3(wavpath):
    mp3=wavpath[:-4]+".mp3"
    r=subprocess.run([FF,"-y","-i",wavpath,"-ac","1","-ar",str(SR),"-b:a","72k",mp3],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    return mp3 if (r.returncode==0 and os.path.exists(mp3)) else None

def synth_bikebell():
    # twee heldere belslagen: "tring-tring"
    t=np.arange(int(1.4*SR))/SR
    out=np.zeros_like(t)
    ratios=[1.0,2.76,5.40,8.93]; amps=[1.0,0.6,0.35,0.18]; taus=[0.45,0.32,0.22,0.15]
    def strike(t0,f0=2150):
        s=np.zeros_like(t); tt=t-t0; m=tt>=0
        for r,a,tau in zip(ratios,amps,taus):
            s[m]+=a*np.sin(2*np.pi*f0*r*tt[m])*np.exp(-tt[m]/tau)
        return s
    out+=strike(0.0)+0.85*strike(0.30)
    out/= (np.max(np.abs(out))+1e-9)
    return finish(out.astype(np.float32))

result={}; credits={}
for key,cat in MAP:
    best=None
    for fn,src in bycat.get(cat,[])[:NCAND]:
        try:
            x=to_mono(dl(fn)); seg,rms=best_window(x)
            if best is None or rms>best[0]: best=(rms,seg,fn,src)
        except Exception as e: print("  !",key,fn,e,file=sys.stderr)
    if not best: print("  XX",key); continue
    rms,seg,fn,src=best; seg=finish(seg)
    wp=os.path.join("seg",key+".wav"); write_wav(seg,wp); mp3=to_mp3(wp)
    if not mp3: print("  XX mp3",key); continue
    b=open(mp3,"rb").read(); result[key]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
    credits[key]={"file":fn,"freesound_src":src,"bytes":len(b),"dur":round(len(seg)/SR,2)}
    print(f"  OK {key:10} <- {fn:22} {len(b)}B")

# fiets: synth
seg=synth_bikebell(); wp="seg/fiets.wav"; write_wav(seg,wp); mp3=to_mp3(wp)
b=open(mp3,"rb").read(); result["fiets"]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
credits["fiets"]={"file":"(gesynthetiseerd)","bytes":len(b),"dur":round(len(seg)/SR,2)}
print(f"  OK {'fiets':10} <- synth               {len(b)}B")

json.dump(result,open("sounds_voertuigen.json","w")); json.dump(credits,open("credits_voertuigen.json","w"),indent=2)
tot=sum(len(v) for v in result.values()); print(f"\nTotal base64: {tot} (~{tot/1024:.0f} KB) for {len(result)} sounds")
