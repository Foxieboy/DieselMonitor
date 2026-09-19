import urllib.request, urllib.error, os, json, wave, base64, subprocess, sys
import numpy as np
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe(); SR=22050; WIN=1.6
UA={"User-Agent":"ToddlerGame/1.0"}

CLASSES={
 "leeuw":   ("https://raw.githubusercontent.com/YashNita/Animal-Sound-Dataset/master/Aslan/aslan_{}.wav",[1,5,10,20,30,40]),
 "aap":     ("https://raw.githubusercontent.com/YashNita/Animal-Sound-Dataset/master/Maymun/maymun_{}.wav",[1,3,5,8,12,20]),
 "ezel":    ("https://raw.githubusercontent.com/YashNita/Animal-Sound-Dataset/master/Esek/esek_{}.wav",[1,3,5,8,12,20]),
 "olifant": ("https://raw.githubusercontent.com/chathuravithakshana/Animal-Sound-Dataset-Research-2019-Sri-Lanka/master/dataset/elephant/elephant_{}.wav",[1,3,5,10,20,30,40]),
}
os.makedirs("wild",exist_ok=True); os.makedirs("seg",exist_ok=True)
def dl(url,dst):
    if os.path.exists(dst) and os.path.getsize(dst)>2000: return True
    try:
        req=urllib.request.Request(url,headers=UA)
        with urllib.request.urlopen(req,timeout=60) as r,open(dst,"wb") as f: f.write(r.read())
        return os.path.getsize(dst)>2000
    except Exception as e:
        return False
def to_mono(path):
    out=path+".m.wav"
    subprocess.run([FF,"-y","-i",path,"-ac","1","-ar",str(SR),out],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    w=wave.open(out,"rb");n=w.getnframes();x=np.frombuffer(w.readframes(n),dtype=np.int16).astype(np.float32)/32768.0;w.close();os.remove(out);return x
def best_window(x):
    W=int(WIN*SR)
    if len(x)<=W: return x,float(np.sqrt(np.mean(x**2)+1e-9))
    e=x*x;c=np.concatenate([[0],np.cumsum(e)]);s=c[W:]-c[:-W];i=int(np.argmax(s));return x[i:i+W],float(np.sqrt(s[i]/W))
def finish(seg):
    seg=seg.astype(np.float32)
    thr=0.02*np.max(np.abs(seg)+1e-9);idx=np.where(np.abs(seg)>thr)[0]
    if len(idx)>0: seg=seg[max(0,idx[0]-int(0.03*SR)):min(len(seg),idx[-1]+int(0.06*SR))]
    seg=seg/(np.max(np.abs(seg))+1e-9)*0.92
    fi=int(0.012*SR);fo=int(0.07*SR)
    if len(seg)>fi+fo: seg[:fi]*=np.linspace(0,1,fi); seg[-fo:]*=np.linspace(1,0,fo)
    return seg
def lowpass(x,a):
    y=np.empty_like(x);y[0]=x[0]
    for i in range(1,len(x)): y[i]=y[i-1]+a*(x[i]-y[i-1])
    return y
def write_wav(seg,p):
    d=(np.clip(seg,-1,1)*32767).astype(np.int16);w=wave.open(p,"wb");w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(d.tobytes());w.close()
def to_mp3(p):
    m=p[:-4]+".mp3";r=subprocess.run([FF,"-y","-i",p,"-ac","1","-ar",str(SR),"-b:a","80k",m],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    return m if r.returncode==0 and os.path.exists(m) else None
def synth_owl():
    dur=1.8;N=int(dur*SR);t=np.arange(N)/SR;out=np.zeros(N)
    def hoot(t0,f0=340):
        tt=t-t0;m=(tt>=0)&(tt<0.8)
        fc=f0*(1-0.10*np.clip(tt/0.6,0,1))
        ph=2*np.pi*np.cumsum(np.where(m,fc,0.0))/SR
        body=np.sin(ph)+0.28*np.sin(2*ph)
        env=np.where(m,np.exp(-((tt-0.20)**2)/(2*0.13**2)),0.0)
        return body*env
    out=hoot(0.0)+0.95*hoot(0.9)
    out=lowpass(out+0.02*np.random.randn(N),0.22)
    return finish(out)

wild={}; cred={}
for key,(tmpl,idxs) in CLASSES.items():
    best=None
    for i in idxs:
        url=tmpl.format(i); dst=os.path.join("wild","%s_%d.wav"%(key,i))
        if not dl(url,dst): print("  miss",key,i,file=sys.stderr); continue
        try:
            x=to_mono(dst); seg,rms=best_window(x)
            if best is None or rms>best[0]: best=(rms,seg,os.path.basename(dst))
        except Exception as e: print("  err",key,i,e,file=sys.stderr)
    if not best: print("  XX geen bron voor",key); continue
    rms,seg,fn=best; seg=finish(seg); wp="seg/%s.wav"%key; write_wav(seg,wp); mp3=to_mp3(wp)
    b=open(mp3,"rb").read(); wild[key]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
    cred[key]={"file":fn,"bytes":len(b),"dur":round(len(seg)/SR,2)}
    print("  OK %-8s <- %-16s %dB %.2fs"%(key,fn,len(b),len(seg)/SR))

# uil synth
seg=synth_owl(); wp="seg/uil.wav"; write_wav(seg,wp); mp3=to_mp3(wp)
b=open(mp3,"rb").read(); wild["uil"]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
cred["uil"]={"file":"(gesynthetiseerd)","bytes":len(b),"dur":round(len(seg)/SR,2)}
print("  OK uil      <- synth")

# split: ezel hoort bij boerderij (dieren)
ezel=wild.pop("ezel",None); ezel_c=cred.pop("ezel",None)
json.dump(wild,open("sounds_wild.json","w")); json.dump(cred,open("credits_wild.json","w"),indent=2)
if ezel:
    d=json.load(open("sounds_dieren.json")); d["ezel"]=ezel; json.dump(d,open("sounds_dieren.json","w"))
    dc=json.load(open("credits.json")); dc["ezel"]=ezel_c; json.dump(dc,open("credits.json","w"),indent=2)
    print("  ezel toegevoegd aan boerderij")
print("wild keys:",list(wild.keys()))
