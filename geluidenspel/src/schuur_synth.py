"""Schuurmachine (gesynthetiseerd: geen vrije echte opname bereikbaar).

Een handschuurmachine draait ~11.000 slagen/min (~190 Hz): brommende motor met
boventonen, het schuurplateau dat met die frequentie trilt, en het schurende geruis
van schuurpapier op hout dat aanzwelt met de heen-en-weer-bewegingen van de hand.
Aanloop en uitloop: de toon klimt aan het begin en zakt op het eind.
Schrijft 'schuurmachine' in sounds_klus.json en credits_klus.json.
"""
import json, base64, subprocess, wave, os, numpy as np
SR = 22050; DUR = 2.7
rng = np.random.default_rng(7)
t = np.arange(int(DUR * SR)) / SR

def band(x, lo, hi):
    F = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    F[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(F, len(x))

# toerental: aanlopen (0-0.3 s), draaien met lichte schommeling, uitlopen (laatste 0.35 s)
up = np.clip(t / 0.3, 0, 1) ** 0.6
down = np.clip((DUR - t) / 0.35, 0, 1)
speed = np.minimum(up, 0.35 + 0.65 * down) * (1 + 0.012 * np.sin(2 * np.pi * 3.1 * t))
f0 = 190 * speed
ph = 2 * np.pi * np.cumsum(f0) / SR
motor = sum(a * np.sin(k * ph) for k, a in [(1, 1.0), (2, 0.55), (3, 0.35), (4, 0.2), (6, 0.12), (9, 0.06)])
motor = motor / np.max(np.abs(motor))

# trillend plateau: ruis die met de slagfrequentie open en dicht gaat ("zzzz")
buzz = band(rng.standard_normal(len(t)), 300, 3500) * (0.55 + 0.45 * np.sin(ph) ** 2)
buzz /= np.max(np.abs(buzz))

# schuurpapier op hout: helder geruis, aanzwellend met de handbeweging (~0.55 s heen en weer)
stroke = 0.55 + 0.45 * np.abs(np.sin(np.pi * t / 0.55))
grain = band(rng.standard_normal(len(t)), 1500, 8000)
crackle = band((rng.random(len(t)) < 0.004) * rng.standard_normal(len(t)) * 6, 1000, 9000)
grit = (grain + crackle) * stroke * (0.6 + 0.4 * np.sin(ph * 0.5) ** 2)
grit /= np.max(np.abs(grit))

load = np.clip((t - 0.25) / 0.2, 0, 1) * np.clip((DUR - 0.3 - t) / 0.2, 0, 1)  # papier raakt het hout
env = np.maximum(up, 0) * down ** 0.7
y = (0.42 * motor + 0.30 * buzz) * env + 0.55 * grit * load * env
y[:int(.01 * SR)] *= np.linspace(0, 1, int(.01 * SR))
y = y / np.max(np.abs(y)) * 0.92

w = wave.open("seg_schuur.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((y * 32767).astype(np.int16).tobytes()); w.close()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "seg_schuur.wav", "-ac", "1", "-ar", str(SR), "-b:a", "80k", "seg_schuur.mp3"], check=True)
b = open("seg_schuur.mp3", "rb").read(); os.remove("seg_schuur.wav"); os.remove("seg_schuur.mp3")
snd = json.load(open("sounds_klus.json")); snd["schuurmachine"] = "data:audio/mpeg;base64," + base64.b64encode(b).decode()
cred = json.load(open("credits_klus.json")); cred["schuurmachine"] = {"file": "(gesynthetiseerd, zie schuur_synth.py)", "bytes": len(b)}
json.dump(snd, open("sounds_klus.json", "w")); json.dump(cred, open("credits_klus.json", "w"), indent=2)
print("schuurmachine: %.2fs, %d bytes" % (DUR, len(b)))
