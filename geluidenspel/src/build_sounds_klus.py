import csv, os, json, wave, base64, subprocess, sys, urllib.request
import numpy as np, imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe(); SR=22050; WIN=1.6
UA={"User-Agent":"ToddlerGame/1.0"}; ESC="https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/"
os.makedirs("klus",exist_ok=True); os.makedirs("seg",exist_ok=True)

def lowpass(x,a):
    y=np.empty_like(x); y[0]=x[0]
    for i in range(1,len(x)): y[i]=y[i-1]+a*(x[i]-y[i-1])
    return y
def finish(seg):
    seg=seg.astype(np.float32)
    thr=0.02*np.max(np.abs(seg)+1e-9); idx=np.where(np.abs(seg)>thr)[0]
    if len(idx)>0: seg=seg[max(0,idx[0]-int(0.03*SR)):min(len(seg),idx[-1]+int(0.06*SR))]
    seg=seg/(np.max(np.abs(seg))+1e-9)*0.92
    fi=int(0.012*SR); fo=int(0.07*SR)
    if len(seg)>fi+fo: seg[:fi]*=np.linspace(0,1,fi); seg[-fo:]*=np.linspace(1,0,fo)
    return seg
def write_wav(seg,p):
    d=(np.clip(seg,-1,1)*32767).astype(np.int16); w=wave.open(p,"wb")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes()); w.close()
def to_mp3(p):
    m=p[:-4]+".mp3"
    subprocess.run([FF,"-y","-i",p,"-ac","1","-ar",str(SR),"-b:a","80k",m],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    return m
def to_mono(p):
    o=p+".m.wav"
    subprocess.run([FF,"-y","-i",p,"-ac","1","-ar",str(SR),o],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    w=wave.open(o,"rb"); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
    w.close(); os.remove(o); return x
def best_window(x):
    W=int(WIN*SR)
    if len(x)<=W: return x,float(np.sqrt(np.mean(x**2)+1e-9))
    e=x*x; c=np.concatenate([[0],np.cumsum(e)]); s=c[W:]-c[:-W]; i=int(np.argmax(s))
    return x[i:i+W], float(np.sqrt(s[i]/W))

# ---------- echte opnames ----------
bycat={}
for r in csv.DictReader(open("esc50.csv")): bycat.setdefault(r["category"],[]).append(r["filename"])
def esc(key,cat):
    best=None
    for fn in bycat.get(cat,[])[:4]:
        dst=os.path.join("klus",fn)
        if not os.path.exists(dst):
            try:
                req=urllib.request.Request(ESC+fn,headers=UA)
                open(dst,"wb").write(urllib.request.urlopen(req,timeout=60).read())
            except Exception: continue
        try:
            seg,rms=best_window(to_mono(dst))
            if best is None or rms>best[0]: best=(rms,seg,fn)
        except Exception: pass
    return (finish(best[1]), best[2]) if best else (None,None)

# ---------- synthese ----------
def hamer():
    dur=1.7; N=int(dur*SR); t=np.arange(N)/SR; out=np.zeros(N)
    for k,t0 in enumerate([0.02,0.34,0.66,0.98,1.30]):
        i0=int(t0*SR); tt=np.arange(N-i0)/SR
        # metalen naklank (inharmonische partialen)
        ring=sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt/d)
                 for f,a,d in [(1750,1.0,0.075),(2870,0.6,0.055),(4230,0.35,0.035),(760,0.5,0.06)])
        # aanslag-transient + lage dreun
        n=len(tt)
        trans=np.random.randn(n)*np.exp(-tt/0.006)*1.2
        thud=np.sin(2*np.pi*135*tt)*np.exp(-tt/0.05)*0.8
        amp=1.0 if k%2==0 else 0.82
        out[i0:]+=amp*(ring*0.55+trans+thud)
    return finish(lowpass(out,0.75))

def boor():
    dur=2.0; N=int(dur*SR); t=np.arange(N)/SR
    env_up=np.clip(t/0.25,0,1); env_dn=np.clip((dur-t)/0.3,0,1)
    f0=210+120*np.clip((t-0.2)/0.6,0,1)-60*np.clip((t-1.5)/0.5,0,1)
    ph=2*np.pi*np.cumsum(f0)/SR
    saw=2*((ph/(2*np.pi))%1.0)-1.0
    whine=0.5*np.sin(6*ph)+0.3*np.sin(9*ph)          # hoge boortoon
    rattle=0.25*np.random.randn(N)*(0.6+0.4*np.sin(2*np.pi*38*t))
    sig=lowpass(saw*0.7+whine+rattle,0.55)
    return finish(sig*env_up*env_dn)

def cirkelzaag():
    dur=2.2; N=int(dur*SR); t=np.arange(N)/SR
    bite=(t>0.65)&(t<1.5)
    f0=520+180*np.clip(t/0.5,0,1)
    f0=f0-np.where(bite,90,0)                         # toon zakt in het hout
    ph=2*np.pi*np.cumsum(f0)/SR
    tone=np.sin(ph)+0.5*np.sin(2*ph)+0.25*np.sin(3*ph)
    wood=np.where(bite,1.0,0.12)*np.random.randn(N)*0.9
    wood=lowpass(wood,0.5)
    env=np.clip(t/0.15,0,1)*np.clip((dur-t)/0.35,0,1)
    return finish(lowpass(tone*0.6+wood,0.7)*env)

def grasmaaier():
    dur=2.0; N=int(dur*SR); t=np.arange(N)/SR
    ff=np.full(N,29.0)+1.5*np.sin(2*np.pi*0.8*t)      # rustig stationair
    ph=2*np.pi*np.cumsum(ff)/SR; cyc=np.floor(ph/(2*np.pi))
    train=np.zeros(N); idx=np.where(np.diff(cyc)>0)[0]+1; train[idx]=1.0
    L=int(0.07*SR); tt=np.arange(L)/SR
    ir=(np.sin(2*np.pi*105*tt)+0.45*np.sin(2*np.pi*210*tt))*np.exp(-tt/0.022)
    eng=np.convolve(train,ir)[:N]
    blade=lowpass(np.random.randn(N),0.25)*0.35       # ruisend maaiblad
    env=np.clip(t/0.12,0,1)*np.clip((dur-t)/0.3,0,1)
    return finish(lowpass(eng+blade,0.5)*env)

def schaar():
    dur=1.5; N=int(dur*SR); out=np.zeros(N)
    for t0 in [0.05,0.55,1.05]:
        i0=int(t0*SR); tt=np.arange(N-i0)/SR; n=len(tt)
        shear=lowpass(np.random.randn(n),0.9)*np.exp(-tt/0.035)
        ring=(np.sin(2*np.pi*3100*tt)*0.5+np.sin(2*np.pi*4700*tt)*0.3)*np.exp(-tt/0.05)
        clack=np.sin(2*np.pi*900*tt)*np.exp(-tt/0.012)*0.6
        out[i0:]+=shear*1.1+ring+clack
    return finish(out)

out={}; cred={}
for key,cat in [("handzaag","hand_saw"),("kettingzaag","chainsaw")]:
    seg,fn=esc(key,cat)
    if seg is None: print("  XX",key); continue
    wp="seg/%s.wav"%key; write_wav(seg,wp); b=open(to_mp3(wp),"rb").read()
    out[key]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
    cred[key]={"file":fn,"bron":"ESC-50 (CC BY-NC)","bytes":len(b)}
    print(f"  OK {key:12} <- {fn:22} (echte opname)")
for key,fn in [("hamer",hamer),("boor",boor),("cirkelzaag",cirkelzaag),("grasmaaier",grasmaaier),("schaar",schaar)]:
    seg=fn(); wp="seg/%s.wav"%key; write_wav(seg,wp); b=open(to_mp3(wp),"rb").read()
    out[key]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
    cred[key]={"file":"(gesynthetiseerd)","bytes":len(b)}
    print(f"  OK {key:12} <- synthese")
json.dump(out,open("sounds_klus.json","w")); json.dump(cred,open("credits_klus.json","w"),indent=2)
print("\ntotaal:",len(out),"geluiden")
