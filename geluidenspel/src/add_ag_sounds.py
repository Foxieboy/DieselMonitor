import os, json, wave, base64, subprocess
import numpy as np, imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe(); SR=22050; WIN=1.6
SRC="https://github.com/raimonvibe/animalguesses-web (MIT)"

def to_mono(p):
    o=p+".m.wav"
    subprocess.run([FF,"-y","-i",p,"-ac","1","-ar",str(SR),o],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    w=wave.open(o,"rb");x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0;w.close();os.remove(o);return x
def best_window(x):
    W=int(WIN*SR)
    if len(x)<=W: return x
    e=x*x;c=np.concatenate([[0],np.cumsum(e)]);s=c[W:]-c[:-W];i=int(np.argmax(s));return x[i:i+W]
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

JOBS=[("eend","ag/Ente_quackt.wav","dieren"),("paard","ag/pferd_whinnert.wav","dieren"),
      ("tijger","ag/tiger.wav","wild"),("uil","ag/owl.wav","wild")]
snd={"dieren":json.load(open("sounds_dieren.json")),"wild":json.load(open("sounds_wild.json"))}
cred={"dieren":json.load(open("credits.json")),"wild":json.load(open("credits_wild.json"))}
os.makedirs("seg",exist_ok=True)
for key,src,theme in JOBS:
    seg=finish(best_window(to_mono(src)))
    wp="seg/%s.wav"%key; write_wav(seg,wp); b=open(to_mp3(wp),"rb").read()
    snd[theme][key]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
    cred[theme][key]={"file":os.path.basename(src),"source":SRC,"bytes":len(b),"dur":round(len(seg)/SR,2)}
    print(f"  OK {key:8} <- {os.path.basename(src):22} {len(b)}B {len(seg)/SR:.2f}s")
json.dump(snd["dieren"],open("sounds_dieren.json","w")); json.dump(snd["wild"],open("sounds_wild.json","w"))
json.dump(cred["dieren"],open("credits.json","w"),indent=2); json.dump(cred["wild"],open("credits_wild.json","w"),indent=2)
print("boerderij:",sorted(snd["dieren"])); print("wild:",sorted(snd["wild"]))
