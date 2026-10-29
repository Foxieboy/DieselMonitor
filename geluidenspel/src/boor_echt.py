"""Spectaculair boorgeluid uit twee echte opnames (vervangt de synthetische boor).

Bronnen (via git, uit github.com/mikesmales/Udacity-ML-Capstone):
  - "Evaluation audio/drilling_1.wav"                     boor slaat aan en toert op (motor giert)
  - "UrbanSound Dataset sample/audio/103199-4-0-0.wav"    UrbanSound8K, klasse drilling,
                                                          Freesound 103199 (CC BY-NC)
Opbouw: aanslaan + optoeren -> vol in de muur -> uitlopen (toon zakt naar de helft).
Gebruik: python3 boor_echt.py <drilling_1.wav> <103199-4-0-0.wav>
"""
import sys, subprocess, base64, json, wave, numpy as np
SR = 22050
def load(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768
def cut(x, a, b): return x[int(a * SR):int(b * SR)].copy()
def rms(x): return np.sqrt(np.mean(x ** 2)) + 1e-9
def xf(a, b, d):
    k = int(d * SR); w = np.linspace(0, 1, k)
    return np.concatenate([a[:-k], a[-k:] * np.cos(w * np.pi / 2) + b[:k] * np.sin(w * np.pi / 2), b[k:]])

rev, bite = load(sys.argv[1]), load(sys.argv[2])
A = cut(rev, 0.62, 1.80)                                   # aanslaan + optoeren
B = cut(bite, 1.70, 3.30)                                  # vol in de muur
B *= rms(A[-int(.3 * SR):]) / rms(B[:int(.3 * SR)]) * 1.15
T = cut(rev, 1.85, 2.40); n = len(T)                       # uitlopen: toon zakt 1.0 -> 0.45
pos = np.cumsum(np.linspace(1.0, 0.45, n)); pos = pos[pos < n - 1]
tail = np.interp(pos, np.arange(n), T)
F = np.fft.rfft(tail); F[np.fft.rfftfreq(len(tail), 1 / SR) > 4500] *= 0.05; tail = np.fft.irfft(F, len(tail))
tail *= np.linspace(1, 0, len(tail)) ** 1.5
tail *= rms(B[-int(.2 * SR):]) / rms(tail[:int(.1 * SR)])
y = xf(xf(A, B, 0.12), tail, 0.10)
y[:int(.01 * SR)] *= np.linspace(0, 1, int(.01 * SR))
y = y / np.max(np.abs(y)) * 0.92

w = wave.open("seg_boor.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((y * 32767).astype(np.int16).tobytes()); w.close()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "seg_boor.wav", "-ac", "1", "-ar", str(SR), "-b:a", "80k", "seg_boor.mp3"], check=True)
b = open("seg_boor.mp3", "rb").read()
snd = json.load(open("sounds_klus.json")); snd["boor"] = "data:audio/mpeg;base64," + base64.b64encode(b).decode()
json.dump(snd, open("sounds_klus.json", "w"))
cred = json.load(open("credits_klus.json"))
cred["boor"] = {"file": "drilling_1.wav + 103199-4-0-0.wav (samengesteld, zie boor_echt.py)",
                "bron": "UrbanSound8K / Freesound 103199 (CC BY-NC) + voorbeeldopname mikesmales/Udacity-ML-Capstone",
                "bytes": len(b)}
json.dump(cred, open("credits_klus.json", "w"), indent=2)
import os; os.remove("seg_boor.wav"); os.remove("seg_boor.mp3")
print("boor: %.2fs, %d bytes" % (len(y) / SR, len(b)))
