import csv, os, json, wave, base64, subprocess, sys, urllib.request, urllib.parse
import numpy as np, imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe(); SR=22050; WIN=1.6
UA={"User-Agent":"ToddlerGame/1.0"}
AG="https://raw.githubusercontent.com/raimonvibe/animalguesses-web/main/assets/assets/"
ESC="https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/"

# key -> (bestandsnaam in de MIT-dierenset, doel-thema)
AG_JOBS={
 "geit":("Ziege.wav","dieren"), "gans":("Gaense.wav","dieren"), "kalkoen":("truthahn.wav","dieren"),
 "duif":("pigeons.wav","dieren"), "muis":("mouse.wav","dieren"),
 "wolf":("wolf.wav","wild"), "vos":("fox.wav","wild"), "nijlpaard":("hippo.wav","wild"),
 "neushoorn":("Rhinozerus.wav","wild"), "gorilla":("gorilla.wav","wild"),
 "papegaai":("parrot.wav","wild"), "adelaar":("eagle.wav","wild"),
}
# key -> (ESC-50 categorie, doel-thema)
ESC_JOBS={
 "kloppen":("door_wood_knock","huis"), "wekker":("clock_alarm","huis"), "klok":("clock_tick","huis"),
 "stofzuiger":("vacuum_cleaner","huis"), "wasmachine":("washing_machine","huis"),
 "tandenborstel":("brushing_teeth","huis"), "wc":("toilet_flush","huis"),
 "water":("pouring_water","huis"), "blikje":("can_opening","huis"),
 "lachen":("laughing","mensen"), "niezen":("sneezing","mensen"), "hoesten":("coughing","mensen"),
 "klappen":("clapping","mensen"), "baby":("crying_baby","mensen"), "voetstappen":("footsteps","mensen"),
 "snurken":("snoring","mensen"), "drinken":("drinking_sipping","mensen"),
}
os.makedirs("more",exist_ok=True); os.makedirs("seg",exist_ok=True)

def dl(url,dst):
    if os.path.exists(dst) and os.path.getsize(dst)>2000: return True
    try:
        req=urllib.request.Request(url,headers=UA)
        with urllib.request.urlopen(req,timeout=60) as r,open(dst,"wb") as f: f.write(r.read())
        return os.path.getsize(dst)>2000
    except Exception: return False
def to_mono(p):
    o=p+".m.wav"
    subprocess.run([FF,"-y","-i",p,"-ac","1","-ar",str(SR),o],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    w=wave.open(o,"rb");x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0;w.close();os.remove(o);return x
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
def write_wav(seg,p):
    d=(np.clip(seg,-1,1)*32767).astype(np.int16);w=wave.open(p,"wb")
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(d.tobytes());w.close()
def to_mp3(p):
    m=p[:-4]+".mp3"
    subprocess.run([FF,"-y","-i",p,"-ac","1","-ar",str(SR),"-b:a","80k",m],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    return m
def emit(key,seg,theme,srcname,out,cred):
    seg=finish(seg); wp="seg/%s.wav"%key; write_wav(seg,wp); b=open(to_mp3(wp),"rb").read()
    out.setdefault(theme,{})[key]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
    cred.setdefault(theme,{})[key]={"file":srcname,"bytes":len(b),"dur":round(len(seg)/SR,2)}
    print(f"  OK {key:14} <- {srcname:26} {len(b)}B")

out={}; cred={}
print("=== MIT-dierenset ===")
for key,(fn,theme) in AG_JOBS.items():
    dst=os.path.join("more",fn)
    if not dl(AG+urllib.parse.quote(fn),dst): print("  XX",key,fn); continue
    emit(key,best_window(to_mono(dst))[0],theme,fn,out,cred)

print("=== ESC-50 ===")
bycat={}
for r in csv.DictReader(open("esc50.csv")): bycat.setdefault(r["category"],[]).append(r["filename"])
for key,(cat,theme) in ESC_JOBS.items():
    best=None
    for fn in bycat.get(cat,[])[:4]:
        dst=os.path.join("more",fn)
        if not dl(ESC+fn,dst): continue
        try:
            seg,rms=best_window(to_mono(dst))
            if best is None or rms>best[0]: best=(rms,seg,fn)
        except Exception as e: print("  !",key,fn,e,file=sys.stderr)
    if not best: print("  XX",key,cat); continue
    emit(key,best[1],theme,best[2],out,cred)

# wegschrijven
for theme in ("dieren","wild"):
    f="sounds_%s.json"%("dieren" if theme=="dieren" else "wild")
    d=json.load(open(f)); d.update(out.get(theme,{})); json.dump(d,open(f,"w"))
    cf="credits.json" if theme=="dieren" else "credits_wild.json"
    c=json.load(open(cf)); c.update(cred.get(theme,{})); json.dump(c,open(cf,"w"),indent=2)
for theme in ("huis","mensen"):
    json.dump(out.get(theme,{}),open("sounds_%s.json"%theme,"w"))
    json.dump(cred.get(theme,{}),open("credits_%s.json"%theme,"w"),indent=2)
print()
for f in ("sounds_dieren.json","sounds_wild.json","sounds_huis.json","sounds_mensen.json"):
    print(f"{f:22}", len(json.load(open(f))), "geluiden:", ", ".join(sorted(json.load(open(f)))))
