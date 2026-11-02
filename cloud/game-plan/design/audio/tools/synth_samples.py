#!/usr/bin/env python3
"""Synthesised reference sounds for Shardfall's key signatures.
These are design sketches made with code (no recordings, no libraries): they
show the layering in sfx_recipes.csv so the team hears the intent. Final
sounds are recorded and designed by the audio team.
Run from game-plan/: python3 design/audio/tools/synth_samples.py"""
import os
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
OUT = os.path.join(os.path.dirname(__file__), '..', 'samples')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)
D3 = 146.83  # Cinderreach root (D Phrygian), the slice region

def t(sec): return np.arange(int(sec * SR)) / SR
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def adsr(n, a, r):
    e = np.ones(n); ai = int(a * SR); ri = int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e
def bp(x, lo, hi, order=4): return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, order=4): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=4): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)
def noise(sec): return rng.standard_normal(int(sec * SR))
def sweep(f0, f1, sec, curve='exp'):
    n = int(sec * SR)
    f = np.geomspace(f0, f1, n) if curve == 'exp' else np.linspace(f0, f1, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def place(buf, x, at):
    i = int(at * SR); j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i]; return buf
def sat(x, drive=2.0): return np.tanh(drive * x) / np.tanh(drive)
def glass(freq, sec, tau, partials=(1, 2.76, 5.40, 8.93), amps=(1, .6, .35, .2), det=0.0):
    tt = t(sec); y = np.zeros_like(tt)
    for p, a in zip(partials, amps):
        if freq * p > 18000: continue  # no aliasing above Nyquist
        y += a * np.sin(2 * np.pi * freq * p * (1 + det * rng.uniform(-1, 1)) * tt) * env_exp(len(tt), tau / p ** 0.5)
    return y
def reverb(x, sec=2.5, wet=0.3, bright=4500):
    n = int(sec * SR); ir = []
    for _ in range(2):
        r = rng.standard_normal(n) * env_exp(n, sec / 6.9); ir.append(lp(r, bright, 2))
    dry = np.stack([x, x], 1)
    w = np.zeros((len(x) + n, 2))
    for c in range(2):
        y = fftconvolve(x, ir[c]); w[:len(y), c] = y[:len(x) + n]
    w /= np.max(np.abs(w)) + 1e-9
    out = np.zeros((len(x) + n, 2)); out[:len(x)] += dry * (1 - wet); out += w * wet * np.max(np.abs(x))
    return out
def stereo(x, width=0.0):
    if x.ndim == 2: return x
    d = int(0.011 * SR); r = np.concatenate([np.zeros(d), x])[:len(x)]
    return np.stack([x, x * (1 - width) + r * width], 1)
def save(name, x, peak_db=-1.0):
    x = stereo(x); x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)
    fade = int(0.01 * SR); x[-fade:] *= np.linspace(1, 0, fade)[:, None]
    wavfile.write(os.path.join(OUT, name), SR, (x * 32767).astype(np.int16)); print(name, f'{len(x) / SR:.2f}s')
    return x

def mixdown(sec, *layers):
    buf = np.zeros(int(sec * SR))
    for x, at, g in layers: place(buf, x * g, at)
    return buf

# ---------------------------------------------------------------- Shard Lance
def shard_lance():
    # charge 0.7 s: rising crystal whine + accelerating glass ticks
    ch = 0.7; tt = t(ch)
    whine = sweep(D3 * 4, D3 * 16, ch) * np.linspace(0.05, 0.5, len(tt)) ** 1.5
    whine += 0.3 * sweep(D3 * 6, D3 * 24, ch) * np.linspace(0, 0.4, len(tt)) ** 2
    ticks = np.zeros(len(tt)); tp = 0.0; gap = 0.12
    while tp < ch - 0.02:
        place(ticks, glass(rng.uniform(3000, 5200), 0.05, 0.01) * 0.4, tp); tp += gap; gap *= 0.8; gap = max(gap, 0.018)
    charge = whine + ticks
    # fire: glass crack + electric snap + capacitor thoom
    crack = hp(noise(0.06), 2500) * env_exp(int(0.06 * SR), 0.008) * 1.5
    snap = bp(noise(0.03), 4000, 12000) * env_exp(int(0.03 * SR), 0.004) * 1.2
    thoom = sweep(110, 38, 0.6) * env_exp(int(0.6 * SR), 0.18) * 1.3
    # beam body 1.1 s: choir formant + ring mod at root
    bb = 1.1; tb = t(bb)
    saw = sum(np.sin(2 * np.pi * D3 * 2 * k * tb) / k for k in range(1, 30))
    choir = sum(bp(saw, f * 0.85, f * 1.15, 2) * a for f, a in ((700, 1), (1220, .6), (2600, .3)))
    ring = np.sin(2 * np.pi * D3 * tb) * bp(noise(bb), 1500, 6000, 2) * 0.25
    beam = (choir * 0.6 + ring) * adsr(len(tb), 0.02, 0.35) * (1 + 0.15 * np.sin(2 * np.pi * 9 * tb))
    # tail: glass shimmer shatter
    tail = np.zeros(int(1.4 * SR))
    for i in range(40):
        place(tail, glass(rng.uniform(1500, 5500), 0.6, rng.uniform(0.05, 0.25)) * rng.uniform(.05, .2), rng.uniform(0, 0.6))
    x = mixdown(3.3, (charge, 0, 1), (crack, ch, 1), (snap, ch, 1), (thoom, ch, 1), (beam, ch + 0.01, 0.8), (tail, ch + 1.0, 0.8))
    return save('shard_lance.wav', reverb(sat(x, 1.5), 2.2, 0.25))

# ---------------------------------------------------------------- Ward break
def ward_break():
    # glass shatter: many inharmonic shards
    sh = np.zeros(int(1.2 * SR))
    for i in range(70):
        place(sh, glass(rng.uniform(1200, 6500), 0.5, rng.uniform(0.02, 0.18), det=0.02) * rng.uniform(.1, .5), abs(rng.normal(0, 0.06)))
    burst = lp(hp(noise(0.12), 1800), 11000) * env_exp(int(0.12 * SR), 0.02) * 1.2
    sub = sweep(120, 35, 0.7) * env_exp(int(0.7 * SR), 0.25) * 1.6
    whump = lp(noise(0.3), 180) * env_exp(int(0.3 * SR), 0.06) * 6
    crack = np.zeros(int(0.5 * SR))
    for i in range(25): place(crack, bp(noise(0.006), 3000, 9000) * rng.uniform(.3, 1), rng.uniform(0.02, 0.45) ** 1.6)
    zap = sweep(2400, 300, 0.25) * env_exp(int(0.25 * SR), 0.06) * 0.25
    x = mixdown(1.8, (burst, 0, 1), (sh, 0, 0.7), (sub, 0, 1), (whump, 0, 0.8), (crack, 0.05, 0.4), (zap, 0, 1))
    return save('ward_break.wav', reverb(sat(x, 2.0), 1.4, 0.2))

# ---------------------------------------------------------------- Ward recharge
def ward_recharge():
    click = bp(noise(0.01), 2000, 8000) * env_exp(int(0.01 * SR), 0.002)
    sw = 1.2; tt = t(sw); f = np.geomspace(300, 3200, len(tt))
    saw = np.zeros(len(tt)); ph = np.cumsum(f) / SR
    for k in range(1, 8): saw += np.sin(2 * np.pi * k * ph) / k
    nz = noise(sw)
    rise = np.zeros(len(tt)); seg = len(tt) // 24
    for s in range(24):  # moving band-pass
        c = 400 * (8 ** (s / 23)); a = s * seg; b = a + seg
        rise[a:b] = bp(nz[a:b] + 0.3 * saw[a:b], c * 0.7, min(c * 1.4, 20000), 2)
    rise *= np.linspace(0.1, 1, len(tt)) ** 2 * adsr(len(tt), 0.05, 0.02)
    whine = sweep(1200, 4800, sw) * np.linspace(0, 0.08, len(tt))
    bell = glass(D3 * 8, 1.6, 0.6, partials=(1, 2, 3.01, 4.2, 5.4), amps=(1, .5, .3, .2, .1))
    x = mixdown(3.2, (click, 0, 0.6), (rise, 0.05, 0.6), (whine, 0.05, 1), (bell, 1.25, 0.5))
    return save('ward_recharge.wav', reverb(x, 2.0, 0.3))

# ---------------------------------------------------------------- Ember pickup chain
def ember_pickup():
    penta = [0, 3, 5, 7, 10, 12, 15]  # D minor pentatonic steps over D5
    x = np.zeros(int(2.6 * SR))
    for i, st in enumerate(penta[:5]):
        f = D3 * 4 * 2 ** (st / 12); at = i * 0.22
        cel = glass(f, 1.0, 0.35, partials=(1, 2, 3, 4.01), amps=(1, .25, .1, .05))
        tick = glass(f * 6, 0.05, 0.008) * 0.3
        thum = np.sin(2 * np.pi * 62 * t(0.12)) * env_exp(int(0.12 * SR), 0.03) * 1.2
        crk = np.zeros(int(0.3 * SR))
        for k in range(10): place(crk, bp(noise(0.003), 2500, 7000) * rng.uniform(.05, .2), rng.uniform(0, 0.28))
        for s, g in ((cel, 0.5), (tick, 1), (thum, 0.8), (crk, 1)): place(x, s * g, at)
    return save('ember_pickup.wav', reverb(x, 1.8, 0.25))

# ---------------------------------------------------------------- Hush whisper crowd
def whisper_voice(sec, seed):
    r = np.random.default_rng(seed); n = int(sec * SR)
    src = r.standard_normal(n)
    # syllable envelope ~5 Hz with gaps
    env = np.zeros(n); p = int(r.uniform(0, 0.05) * SR)
    while p < n:
        L = int(r.uniform(0.09, 0.22) * SR); e = np.hanning(L)
        env[p:p + L] += e[:max(0, min(L, n - p))]; p += L + int(r.uniform(0.02, 0.12) * SR)
    # vowel formant pairs cycling, unvoiced (whisper)
    V = [(300, 2300), (600, 1700), (750, 1150), (450, 900), (350, 2000)]
    y = np.zeros(n); seg = int(0.16 * SR)
    for a in range(0, n, seg):
        f1, f2 = V[r.integers(len(V))]; s = src[a:a + seg]
        y[a:a + seg] = bp(s, f1 * 0.8, f1 * 1.25, 2) * 0.8 + bp(s, f2 * 0.85, f2 * 1.2, 2) + 0.6 * hp(s, 4500, 2)
    return lp(y * env, 9000)

def hush_whisper():
    sec = 4.5; x = np.zeros((int(sec * SR), 2))
    for v in range(16):  # the crowd that agrees with itself: same rhythm seed, tiny offsets
        w = whisper_voice(2.6, 100 + (v % 3)) * rng.uniform(.4, 1)
        d = 0.9 + rng.uniform(0.005, 0.04); pan = rng.uniform(0, 1)
        i = int(d * SR); x[i:i + len(w), 0] += w * (1 - pan); x[i:i + len(w), 1] += w * pan
    tt = t(sec)
    pressure = np.sin(2 * np.pi * 22 * tt) * adsr(len(tt), 1.0, 1.5) * 0.35
    G = 196.0; pad = sum(np.sin(2 * np.pi * G * 2 ** (k * 2 / 12) * tt + k) for k in range(6)) / 6
    pad = lp(pad, 2500) * adsr(len(tt), 1.2, 1.5) * 0.12
    inhale = noise(0.6) * np.linspace(0, 1, int(0.6 * SR)) ** 3; inhale = bp(inhale, 800, 8000) * 0.5
    mono = np.zeros(len(tt)); place(mono, inhale, 0.3); mono += pressure + pad
    x += np.stack([mono, mono], 1)
    wet = reverb(x.mean(1), 3.5, 0.45, bright=7000)[:len(tt)]
    return save('hush_whisper.wav', x * 0.7 + wet * 0.6)

# ---------------------------------------------------------------- others
def stance_break():
    duck = np.zeros(int(0.1 * SR))
    crunch = lp(noise(0.25), 900) * env_exp(int(0.25 * SR), 0.05) * 3
    crack = np.zeros(int(0.6 * SR))
    for i in range(30): place(crack, glass(rng.uniform(1200, 5000), 0.4, rng.uniform(.03, .12)) * rng.uniform(.1, .4), abs(rng.normal(0, .03)))
    ring = glass(D3 * 2, 1.2, 0.4, partials=(1, 2.4, 3.9), amps=(1, .4, .2)) * 0.5
    x = mixdown(1.6, (duck, 0, 0), (crunch, 0.1, 1), (crack, 0.1, 0.8), (ring, 0.12, 1))
    return save('stance_break.wav', reverb(sat(x, 1.8), 1.2, 0.2))

def parry():
    ting = glass(D3 * 16, 1.2, 0.25, partials=(1, 2.32, 4.25, 6.63), amps=(1, .6, .4, .2), det=.005)
    chime = glass(D3 * 8 * 2 ** (7 / 12), 1.5, 0.5, partials=(1, 2, 3), amps=(1, .3, .1)) * 0.5
    clang = bp(noise(0.05), 1500, 6000) * env_exp(int(0.05 * SR), 0.01)
    return save('parry.wav', reverb(mixdown(1.8, (clang, 0, 1), (ting, 0, 0.7), (chime, 0.02, 1)), 1.6, 0.3))

def anchor_lit():
    strike = glass(D3 * 6, 0.8, 0.2); place(strike, bp(noise(0.03), 2000, 9000) * env_exp(int(0.03 * SR), 0.005), 0)
    tt = t(4.5); chord = np.zeros(len(tt))
    for st in (0, 7, 12, 15, 19):  # D minor add9 voicing
        f = D3 * 2 ** (st / 12)
        chord += sum(np.sin(2 * np.pi * f * k * tt) / k ** 1.5 for k in range(1, 6))
    chord = lp(chord, 3000) * adsr(len(tt), 1.0, 2.5) * (1 + 0.05 * np.sin(2 * np.pi * 0.7 * tt)) * 0.2
    hum = np.sin(2 * np.pi * 55 * tt) * adsr(len(tt), 0.3, 2.0) * 0.3
    clamp = lp(noise(0.08), 1200) * env_exp(int(0.08 * SR), 0.02) * 2
    return save('anchor_lit.wav', reverb(mixdown(5.0, (strike, 0, 0.8), (clamp, 0.05, 0.6), (chord, 0.1, 1), (hum, 0.1, 1)), 3.0, 0.35))

def shard_cast_bloom():
    rub = sweep(D3 * 4, D3 * 4.02, 1.5) * adsr(int(1.5 * SR), 0.6, 0.6) * 0.4
    tb = t(1.5); saw = sum(np.sin(2 * np.pi * D3 * k * tb) / k for k in range(1, 25))
    formant = (bp(saw, 600, 900, 2) + 0.6 * bp(saw, 1000, 1400, 2)) * adsr(len(tb), 0.4, 0.7) * 0.5
    sparkle = np.zeros(len(tb))
    for i in range(30): place(sparkle, glass(rng.uniform(2000, 6000), 0.3, 0.06) * 0.08, rng.uniform(0.3, 1.3))
    return save('shard_cast_bloom.wav', reverb(rub + formant + sparkle, 2.5, 0.4))

def ostra_glitch():
    tt = t(2.2); f0 = 190 + 25 * np.sin(2 * np.pi * 3 * tt)
    buzz = np.zeros(len(tt)); ph = np.cumsum(f0) / SR
    for k in range(1, 30): buzz += np.sin(2 * np.pi * k * ph) / k
    env = np.zeros(len(tt)); p = 0
    while p < len(tt):
        L = int(rng.uniform(0.08, 0.2) * SR); env[p:p + L] = np.hanning(L)[:len(env[p:p + L])]; p += L + int(rng.uniform(0.01, 0.08) * SR)
    v = (bp(buzz, 500, 900, 2) + bp(buzz, 1100, 1700, 2) * 0.6) * env
    v = v / (np.max(np.abs(v)) + 1e-9)
    v = np.repeat(v[::3], 3)[:len(v)]         # sample-rate reduction to 16 kHz
    v = np.round(v * 48) / 48                 # light bit crush
    v = bp(v, 300, 3000)                      # memory state 0 band-limit
    for i in range(6):                        # dropouts
        a = int(rng.uniform(0, 2.0) * SR); v[a:a + int(0.04 * SR)] = 0
    chirp = sweep(2000, 6000, 0.05) * 0.2
    return save('ostra_glitch.wav', mixdown(2.4, (chirp, 0, 1), (v, 0.06, 1)))

def unblockable_tell():
    sec = 1.0; tt = t(sec)
    shriek = sum(np.sin(2 * np.pi * f * np.linspace(1, 1.12, len(tt)) * tt) * a for f, a in ((1174, 1), (1661, .7), (2349, .5)))
    shriek = sat(shriek * adsr(len(tt), 0.3, 0.1) * 0.6, 3)
    choir = sum(bp(sum(np.sin(2 * np.pi * D3 * 2 * k * tt) / k for k in range(1, 20)), f * .85, f * 1.15, 2) for f in (700, 1200))
    return save('unblockable_tell.wav', reverb(shriek * 0.5 + choir * adsr(len(tt), 0.4, 0.1) * 0.6, 1.5, 0.3))

if __name__ == '__main__':
    parts = [shard_lance(), ward_break(), ward_recharge(), ember_pickup(), hush_whisper(),
             stance_break(), parry(), unblockable_tell(), anchor_lit(), shard_cast_bloom(), ostra_glitch()]
    gap = np.zeros((int(0.6 * SR), 2))
    save('shardfall_sound_reel.wav', np.concatenate(sum(([p, gap] for p in parts), [])))
