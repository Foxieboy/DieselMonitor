import json, os, wave, base64, subprocess
import numpy as np
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe(); SR=22050

def finish(seg):
    seg=seg.astype(np.float32); seg=seg/(np.max(np.abs(seg))+1e-9)*0.92
    fi=int(0.010*SR); fo=int(0.070*SR)
    if len(seg)>fi+fo: seg[:fi]*=np.linspace(0,1,fi); seg[-fo:]*=np.linspace(1,0,fo)
    return seg
def write_wav(seg,path):
    d=(np.clip(seg,-1,1)*32767).astype(np.int16); w=wave.open(path,"wb")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes()); w.close()
def to_mp3(wavp):
    mp3=wavp[:-4]+".mp3"
    subprocess.run([FF,"-y","-i",wavp,"-ac","1","-ar",str(SR),"-b:a","72k",mp3],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    return mp3
def lowpass(x,a):
    y=np.empty_like(x); y[0]=x[0]
    for i in range(1,len(x)): y[i]=y[i-1]+a*(x[i]-y[i-1])
    return y

def synth_motor():
    dur=1.7; N=int(dur*SR); t=np.arange(N)/SR
    # rev: two little revs then rise
    f0=95+55*np.clip((t-0.15)/1.3,0,1)              # 95 -> 150 Hz
    f0+=8*np.sin(2*np.pi*3*t)                         # wobble
    ph=2*np.pi*np.cumsum(f0)/SR
    saw=2*((ph/(2*np.pi))%1.0)-1.0                    # buzzy engine tone
    fire=2*np.pi*np.cumsum(f0*0.5)/SR                 # 4-stroke firing ~ f0/2
    am=0.5+0.5*np.abs(np.sin(fire))                   # "brap brap" texture
    sig=saw*am + 0.18*np.random.randn(N)*am
    sig=lowpass(sig,0.28)                             # tame harshness
    env=np.clip(t/0.08,0,1)                           # quick fade-in
    return finish(sig*env)

def synth_boothoorn():
    dur=1.6; N=int(dur*SR); t=np.arange(N)/SR
    f0=112*(1+0.006*np.sin(2*np.pi*5*t))             # low, slight vibrato
    tone=(np.sin(2*np.pi*f0*t)
          +0.55*np.sin(2*np.pi*2*f0*t)
          +0.30*np.sin(2*np.pi*3*f0*t)
          +0.16*np.sin(2*np.pi*4*f0*t))
    # envelope: short blast, gap, long blast (typisch "toet... tuuuut")
    env=np.zeros(N)
    def blast(a,b,at=0.06,rl=0.15):
        i0,i1=int(a*SR),int(b*SR); seg=np.ones(i1-i0)
        fi=int(at*SR); fo=int(rl*SR)
        seg[:fi]*=np.linspace(0,1,fi); seg[-fo:]*=np.linspace(1,0,fo)
        env[i0:i1]=np.maximum(env[i0:i1],seg)
    blast(0.02,0.42); blast(0.55,1.55,rl=0.30)
    return finish(tone*env)

snd=json.load(open("sounds_voertuigen.json"))
cred=json.load(open("credits_voertuigen.json"))
for key,fn in [("motor",synth_motor),("boot",synth_boothoorn)]:
    seg=fn(); wp="seg/%s.wav"%key
    os.makedirs("seg",exist_ok=True); write_wav(seg,wp); mp3=to_mp3(wp)
    b=open(mp3,"rb").read(); snd[key]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
    cred[key]={"file":"(gesynthetiseerd)","bytes":len(b),"dur":round(len(seg)/SR,2)}
    print("OK %-8s %dB %.2fs"%(key,len(b),len(seg)/SR))
json.dump(snd,open("sounds_voertuigen.json","w")); json.dump(cred,open("credits_voertuigen.json","w"),indent=2)
print("voertuigen sounds nu:", list(snd.keys()))
