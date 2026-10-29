"""Spectaculair boorgeluid uit twee echte opnames (vervangt de synthetische boor).

Bronnen (via git, uit github.com/mikesmales/Udacity-ML-Capstone):
  - "Evaluation audio/drilling_1.wav"                     boor slaat aan en toert op (motor giert)
  - "UrbanSound Dataset sample/audio/103199-4-0-0.wav"    UrbanSound8K, klasse drilling,
                                                          Freesound 103199 (CC BY-NC)
Opbouw: aanslaan + optoeren -> vol in de muur -> uitlopen (toon zakt naar de helft).
  - "UrbanSound Dataset sample/audio/103074-7-0-0.wav"    UrbanSound8K, klasse jackhammer,
                                                          Freesound 103074 (CC BY-NC)
Daarnaast elk als eigen tegel: accuboor (optoeren), klopboor (in de muur), drilboor (breekhamer).
Gebruik: python3 boor_echt.py <drilling_1.wav> <103199-4-0-0.wav> <103074-7-0-0.wav>
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

def finish(seg):
    seg = seg / (np.max(np.abs(seg)) + 1e-9) * 0.92
    fi, fo = int(.012 * SR), int(.12 * SR)
    seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.linspace(1, 0, fo)
    return seg

import os
snd = json.load(open("sounds_klus.json")); cred = json.load(open("credits_klus.json"))
def store(key, seg, file, bron):
    w = wave.open("seg_%s.wav" % key, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(seg, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "seg_%s.wav" % key, "-ac", "1", "-ar", str(SR), "-b:a", "80k", "seg_%s.mp3" % key], check=True)
    b = open("seg_%s.mp3" % key, "rb").read()
    snd[key] = "data:audio/mpeg;base64," + base64.b64encode(b).decode()
    cred[key] = {"file": file, "bron": bron, "bytes": len(b)}
    os.remove("seg_%s.wav" % key); os.remove("seg_%s.mp3" % key)
    print("%-9s %.2fs, %d bytes" % (key, len(seg) / SR, len(b)))

US = "UrbanSound8K / Freesound %s (CC BY-NC)"
store("boor", y, "drilling_1.wav + 103199-4-0-0.wav (samengesteld, zie boor_echt.py)",
      US % 103199 + " + voorbeeldopname mikesmales/Udacity-ML-Capstone")
store("accuboor", finish(cut(rev, 0.55, 2.55)), "drilling_1.wav", "voorbeeldopname mikesmales/Udacity-ML-Capstone")
store("klopboor", finish(cut(bite, 0.30, 3.60)), "103199-4-0-0.wav", US % 103199)
store("drilboor", finish(cut(load(sys.argv[3]), 0.12, 2.40)), "103074-7-0-0.wav", US % 103074)
json.dump(snd, open("sounds_klus.json", "w")); json.dump(cred, open("credits_klus.json", "w"), indent=2)
