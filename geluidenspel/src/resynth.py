import json, os, wave, base64, subprocess
import numpy as np
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe(); SR=22050

def finish(seg):
    seg=seg.astype(np.float32); seg=seg/(np.max(np.abs(seg))+1e-9)*0.92
    fi=int(0.012*SR); fo=int(0.08*SR)
    if len(seg)>fi+fo: seg[:fi]*=np.linspace(0,1,fi); seg[-fo:]*=np.linspace(1,0,fo)
    return seg
def lowpass(x,a):
    y=np.empty_like(x); y[0]=x[0]
    for i in range(1,len(x)): y[i]=y[i-1]+a*(x[i]-y[i-1])
    return y
def write_wav(seg,path):
    d=(np.clip(seg,-1,1)*32767).astype(np.int16); w=wave.open(path,"wb")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes()); w.close()
def to_mp3(wavp):
    mp3=wavp[:-4]+".mp3"
    subprocess.run([FF,"-y","-i",wavp,"-ac","1","-ar",str(SR),"-b:a","80k",mp3],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    return mp3

def synth_boat():
    dur=2.0; N=int(dur*SR); t=np.arange(N)/SR
    def horn(f0):
        bend=1+0.03*np.clip(t/0.18,0,1)-0.09*np.clip((t-1.35)/0.55,0,1)
        ph=2*np.pi*np.cumsum(f0*bend)/SR
        s=np.zeros(N)
        for n in range(1,11): s+=(1.0/n)*np.sin(n*ph)   # warme zaagtand
        return s
    sig=horn(116)+0.75*horn(87)                          # tweetonige hoorn (kwart)
    sig*=(1+0.04*np.sin(2*np.pi*5.5*t))                  # licht zweven
    nb=lowpass(np.random.randn(N),0.05)*0.05             # beetje "adem"
    sig=lowpass(sig+nb,0.22)                             # warm filteren
    env=np.ones(N); a=int(0.16*SR); r=int(0.55*SR)
    env[:a]=np.linspace(0,1,a)**1.6; env[-r:]=np.linspace(1,0,r)**1.5
    return finish(sig*env)

def synth_motor():
    dur=2.0; N=int(dur*SR); t=np.arange(N)/SR
    ff=20+34*np.clip((t-0.25)/1.5,0,1)                   # ontsteking 20->54 Hz (optrekken)
    ph=2*np.pi*np.cumsum(ff)/SR; cyc=np.floor(ph/(2*np.pi))
    train=np.zeros(N); idx=np.where(np.diff(cyc)>0)[0]+1; train[idx]=1.0
    L=int(0.06*SR); tt=np.arange(L)/SR
    ir=(np.sin(2*np.pi*130*tt)+0.5*np.sin(2*np.pi*260*tt))*np.exp(-tt/0.018)
    eng=np.convolve(train,ir)[:N]
    gate=np.convolve(train,np.ones(int(0.03*SR)))[:N]; gate/=(gate.max()+1e-9)
    eng=eng+0.5*np.random.randn(N)*gate
    eng=lowpass(eng,0.45)
    return finish(eng*np.clip(t/0.12,0,1))

snd=json.load(open("sounds_voertuigen.json")); cred=json.load(open("credits_voertuigen.json"))
os.makedirs("seg",exist_ok=True)
for key,fn,desc in [("boot",synth_boat,"gesynthetiseerd (tweetonige scheepshoorn)"),
                    ("motor",synth_motor,"gesynthetiseerd (motor met ontstekingspulsen)")]:
    seg=fn(); wp="seg/%s.wav"%key; write_wav(seg,wp); mp3=to_mp3(wp)
    b=open(mp3,"rb").read(); snd[key]="data:audio/mpeg;base64,"+base64.b64encode(b).decode()
    cred[key]={"file":desc,"bytes":len(b),"dur":round(len(seg)/SR,2)}
    print("OK %-6s %dB %.2fs"%(key,len(b),len(seg)/SR))
json.dump(snd,open("sounds_voertuigen.json","w")); json.dump(cred,open("credits_voertuigen.json","w"),indent=2)
