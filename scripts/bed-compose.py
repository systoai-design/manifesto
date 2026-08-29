"""An original music bed for the Systo 26s cut.

Written from scratch: every sound here is synthesised from oscillators and
noise, so the result is an original work with no third-party rights in it.

It is composed to OUR picture edit, not to the reference's music. The grid
(150 BPM, 12 frames/beat at 30fps) was fitted to our own cut list, and the
harmony and arrangement are chosen here, not copied.

Its one hard engineering constraint: keep energy out of 300-4000 Hz so the
voice sits in a hole rather than fighting the music.
"""
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, sosfiltfilt

SR   = 44100
FPS  = 30.0
NF   = 776
N    = int(round(NF / FPS * SR))
FPB  = 12.0                      # frames per beat, fitted to the cut list
SPB  = FPB / FPS                 # seconds per beat  (0.4 s -> 150 BPM)
BAR  = 4 * FPB                   # 48 frames

rng = np.random.default_rng(20260829)

def f2s(fr):   return int(round(fr / FPS * SR))
def nsamp(sec): return int(round(sec * SR))

# ---------------------------------------------------------------- oscillators
def _ph(freq, n):
    return 2*np.pi*freq*np.arange(n)/SR

def sine(freq, n, phase=0.0):  return np.sin(_ph(freq, n) + phase)
def tri(freq, n):
    p = (_ph(freq, n)/(2*np.pi)) % 1.0
    return 4*np.abs(p-0.5)-1
def saw(freq, n):
    p = (_ph(freq, n)/(2*np.pi)) % 1.0
    return 2*p-1
def noise(n): return rng.standard_normal(n)

def adsr(n, a, d, s, r):
    a, d, r = max(1,nsamp(a)), max(1,nsamp(d)), max(1,nsamp(r))
    sus = max(0, n-a-d-r)
    return np.concatenate([np.linspace(0,1,a),
                           np.linspace(1,s,d),
                           np.full(sus, s),
                           np.linspace(s,0,r)])[:n]

def lp(x, fc, order=2):
    fc = min(fc, SR/2*0.98)
    return sosfilt(butter(order, fc/(SR/2), "low", output="sos"), x)
def hp(x, fc, order=2):
    return sosfilt(butter(order, max(20,fc)/(SR/2), "high", output="sos"), x)
def bp(x, lo_, hi_, order=2):
    return sosfilt(butter(order, [max(20,lo_)/(SR/2), min(hi_,SR/2*0.98)/(SR/2)],
                          "band", output="sos"), x)

def reverb(x, tail=1.4, mix=0.32):
    """Exponentially decaying noise impulse - cheap, and it sounds like a room."""
    L = nsamp(tail)
    ir = rng.standard_normal(L) * np.exp(-np.linspace(0, 6.5, L))
    ir[:nsamp(0.006)] = 0
    ir /= np.abs(ir).sum()/12
    wet = np.convolve(x, ir)[:len(x)]
    return (1-mix)*x + mix*wet

# ---------------------------------------------------------------------- notes
A4 = 440.0
NAME = {"C":0,"C#":1,"D":2,"D#":3,"E":4,"F":5,"F#":6,"G":7,"G#":8,"A":9,"A#":10,"B":11}
def nf(name, octv):
    return A4 * 2 ** ((NAME[name] + 12*(octv-4) - 9) / 12)

# Our own progression, in A minor, turning warm and resolving to C at the
# payoff. One chord per bar; the film's turn at "That's where we come in"
# (f578) is where it leaves the minor for good.
CHORDS = [
    ("Am", ["A","C","E"], 2),   ("Am", ["A","C","E"], 2),   ("F",  ["F","A","C"], 2),
    ("C",  ["C","E","G"], 3),   ("G",  ["G","B","D"], 2),   ("Am", ["A","C","E"], 2),
    ("F",  ["F","A","C"], 2),   ("C",  ["C","E","G"], 3),   ("G",  ["G","B","D"], 2),
    ("Am", ["A","C","E"], 2),   ("F",  ["F","A","C"], 2),   ("G",  ["G","B","D"], 2),
    ("F",  ["F","A","C"], 2),   ("C",  ["C","E","G"], 3),   ("C",  ["C","E","G"], 3),
    ("C",  ["C","E","G"], 3),   ("C",  ["C","E","G"], 3),
]
def chord_at(fr):
    return CHORDS[min(int(fr // BAR), len(CHORDS)-1)]

# ------------------------------------------------------------- arrangement
def ramp(fr, a, b):
    if fr <= a: return 0.0
    if fr >= b: return 1.0
    t = (fr-a)/(b-a)
    return t*t*(3-2*t)

def gate(fr, on, off, fade_in=18, fade_out=18):
    return ramp(fr, on, on+fade_in) * (1.0 - ramp(fr, off-fade_out, off))

# The film's dynamic shape, in dB relative to the loudest passage. Breakpoints
# are our own section boundaries: quiet open, verse, the paper section peaking,
# a pull-back, the "for you." slam, warm sustain, then the bed steps aside for
# the logo.
ARC = [(0,-60),(30,-60),(46,-13),(130,-10),(300,-8),(340,-3),(400,-0.5),
       (433,-1),(470,-7),(520,-5),(560,-0.5),(578,-1.5),(600,-5),(650,-6),
       (662,-13),(690,-15),(720,-17),(760,-34),(776,-60)]
def arc_db(fr):
    for i in range(len(ARC)-1):
        a,(b) = ARC[i], ARC[i+1]
        if a[0] <= fr <= b[0]:
            t = 0 if b[0]==a[0] else (fr-a[0])/(b[0]-a[0])
            t = t*t*(3-2*t)
            return a[1] + t*(b[1]-a[1])
    return ARC[-1][1]
ARC_ENV = 10**(np.array([arc_db(f) for f in np.arange(N)/SR*FPS])/20.0)

L = np.zeros(N); R = np.zeros(N)
def add(sig, fr, gain=1.0, pan=0.0):
    a = f2s(fr)
    if a >= N: return
    s = sig[:N-a] * gain
    gl, gr = np.sqrt((1-pan)/2)*np.sqrt(2), np.sqrt((1+pan)/2)*np.sqrt(2)
    L[a:a+len(s)] += s*gl; R[a:a+len(s)] += s*gr

# ---- 1. sub: the root of each bar, one long note, soft attack ---------------
sub = np.zeros(N)
for bi in range(len(CHORDS)):
    fr = bi*BAR
    if fr >= NF: break
    name, notes, _ = CHORDS[bi]
    root = nf(notes[0], 1 if notes[0] in ("A","B") else 2)
    n = f2s(BAR) + nsamp(0.20)
    body = sine(root, n) * adsr(n, 0.05, 0.12, 0.85, 0.30)
    body += 0.18*sine(root*2, n) * adsr(n, 0.05, 0.10, 0.6, 0.30)
    a = f2s(fr); e = min(N, a+n)
    sub[a:e] += body[:e-a]
sub = lp(np.tanh(sub*1.25), 130, 3)
env_sub = np.array([gate(f, 30, 776, 40, 30) for f in np.arange(N)/SR*FPS])
sub *= env_sub
L += sub*0.115; R += sub*0.115

# ---- 2. pad: detuned saws, heavily filtered, sitting under the voice --------
pad = np.zeros(N)
for bi in range(len(CHORDS)):
    fr = bi*BAR
    if fr >= NF: break
    _, notes, octv = CHORDS[bi]
    n = f2s(BAR) + nsamp(0.55)
    voice = np.zeros(n)
    for j, nm in enumerate(notes):
        base = nf(nm, octv + (1 if j == 2 else 0))
        for det in (-7.0, 0.0, 6.0):
            voice += saw(base*2**(det/1200.0), n) * 0.33
    voice *= adsr(n, 0.34, 0.5, 0.72, 0.55)
    a = f2s(fr); e = min(N, a+n)
    pad[a:e] += voice[:e-a]
pad = lp(pad, 980, 4)                       # everything above the voice, gone
pad = hp(pad, 150, 2)                       # and out of the sub's way
env_pad = np.array([gate(f, 140, 776, 55, 40)*0.85 + 0.15*ramp(f,300,430)
                    for f in np.arange(N)/SR*FPS])
pad *= env_pad
padw = reverb(pad, 1.6, 0.34)
L += padw*0.30; R += np.roll(padw, 220)*0.30      # a little width

# ---- 3. pulse: eighth-note pluck, the kinetic engine ------------------------
for k in range(int(NF/(FPB/2))+1):
    fr = k*FPB/2
    if fr >= NF: break
    g = gate(fr, 48, 668, 40, 26)
    if fr > 560: g *= 0.55
    if g <= 0.001: continue
    _, notes, octv = chord_at(fr)
    nm = notes[0] if k % 4 in (0,1) else notes[2]
    freq = nf(nm, octv+1)
    n = nsamp(0.19)
    v = (tri(freq, n)*0.7 + saw(freq, n)*0.3) * adsr(n, 0.004, 0.07, 0.16, 0.10)
    v = lp(v, 1800 + 1100*ramp(fr, 240, 430), 2)
    accent = 1.0 if k % 4 == 0 else 0.62
    add(v, fr, 0.105*g*accent, pan=-0.25 if k % 2 else 0.25)

# ---- 4. kick on 1 and 3 -----------------------------------------------------
for k in range(int(NF/(FPB*2))+1):
    fr = k*FPB*2
    if fr >= NF: break
    g = gate(fr, 96, 664, 40, 22)
    if g <= 0.001: continue
    n = nsamp(0.16)
    t = np.arange(n)/SR
    swp = 44 + 58*np.exp(-t*38)
    v = np.sin(2*np.pi*np.cumsum(swp)/SR) * np.exp(-t*17)
    v += 0.10*lp(noise(n), 240)*np.exp(-t*90)
    add(np.tanh(v*1.4), fr, 0.17*g)

# ---- 5. tick + shaker: high, well clear of the voice ------------------------
for k in range(int(NF/(FPB/2))+1):
    fr = k*FPB/2
    if fr >= NF: break
    g = gate(fr, 130, 666, 46, 26)
    if g <= 0.001: continue
    n = nsamp(0.035)
    v = bp(noise(n), 6500, 13000, 2) * np.exp(-np.arange(n)/SR*135)
    add(v, fr, 0.105*g*(1.0 if k % 2 == 0 else 0.55), pan=0.35 if k % 2 else -0.35)
for k in range(int(NF/(FPB/4))+1):
    fr = k*FPB/4 + FPB/8
    if fr >= NF: break
    g = gate(fr, 300, 600, 60, 40)
    if g <= 0.001: continue
    n = nsamp(0.022)
    v = bp(noise(n), 8000, 15000, 2) * np.exp(-np.arange(n)/SR*190)
    add(v, fr, 0.062*g, pan=-0.4 if k % 2 else 0.4)

# ---- 6. impacts on the structural beats -------------------------------------
def impact(fr, gain, bright=1.0):
    n = nsamp(1.5)
    t = np.arange(n)/SR
    boom = np.sin(2*np.pi*np.cumsum(38+30*np.exp(-t*22))/SR)*np.exp(-t*3.4)
    air  = bp(noise(n), 1800, 11000, 2)*np.exp(-t*7.5)*0.20*bright
    add(lp(boom, 200, 2) + air, fr, gain)
impact(108, 0.40, 1.2)      # the word wall
impact(347, 0.26, 0.7)      # into the paper section
impact(534, 0.30, 0.9)      # "for you."
impact(576, 0.46, 1.3)      # the slam zoom
impact(661, 0.34, 0.6)      # the lockup

# ---- 7. risers into the big moments -----------------------------------------
def riser(end_fr, length_fr, gain):
    n = f2s(length_fr)
    t = np.linspace(0, 1, n)
    v = noise(n) * (t**2.2)
    sw = np.zeros(n)
    step = 2048
    for i in range(0, n, step):
        seg = v[i:i+step]
        fc = 380 + 7200*(i/n)**1.7
        sw[i:i+len(seg)] = bp(seg, fc*0.55, min(fc*1.9, 17000), 2)
    add(sw*np.linspace(0,1,n)**1.5, end_fr-length_fr, gain)
riser(108, 30, 0.055)
riser(347, 40, 0.038)
riser(576, 44, 0.060)

# ---- 8. the lockup: everything drops to a held warm chord + sparkle ---------
n = f2s(140)
hold = np.zeros(n)
for j, nm in enumerate(["C","E","G"]):
    fq = nf(nm, 3 + (1 if j == 2 else 0))
    for det in (-5.0, 5.0):
        hold += saw(fq*2**(det/1200.0), n)*0.4
hold = lp(hold, 700, 4)*adsr(n, 0.55, 1.0, 0.62, 1.6)
add(reverb(hold, 2.0, 0.42), 655, 0.085)
for i, (nm, octv, fr) in enumerate([("C",6,668),("E",6,681),("G",6,694),("C",7,707)]):
    n2 = nsamp(1.5)
    v = sine(nf(nm, octv), n2)*np.exp(-np.arange(n2)/SR*3.1)
    v += 0.35*sine(nf(nm, octv)*2.01, n2)*np.exp(-np.arange(n2)/SR*5.0)
    add(reverb(v, 1.8, 0.45), fr, 0.030, pan=(-0.3, 0.3, -0.2, 0.15)[i])

# ---- 9. tail --------------------------------------------------------------
L *= ARC_ENV; R *= ARC_ENV
tailenv = np.array([1.0 - ramp(f, 742, 776) for f in np.arange(N)/SR*FPS])
L *= tailenv; R *= tailenv
# hold the first 30 frames silent - the film opens on nothing
open_env = np.array([ramp(f, 24, 44) for f in np.arange(N)/SR*FPS])
L *= open_env; R *= open_env

mix = np.stack([L, R], 1)
mix = np.tanh(mix*1.06)
mix *= 0.72/np.abs(mix).max()
sf.write(".analysis/bed-original.wav", mix, SR)

# ------------------------------------------------------------------ report
m = mix.mean(1)
mag = np.abs(np.fft.rfft(m*np.hanning(len(m))))
frq = np.fft.rfftfreq(len(m), 1/SR)
def band(lo_, hi_):
    s = (frq>=lo_)&(frq<hi_)
    return 10*np.log10((mag[s]**2).mean()+1e-12)
ref = band(500,800)
print(f"wrote .analysis/bed-original.wav   {len(m)/SR:.3f}s, {NF} frames at {FPS:g}fps")
print(f"150 BPM, {FPB:g} frames/beat, {len(CHORDS)} bars, key A minor resolving to C\n")
print("spectral shape, relative to its own 500-800 Hz band:")
print(f"{'band':>14s} {'ours':>7s} {'reference bed':>14s}")
REFSHAPE = {(30,80):27.4,(80,150):22.3,(150,300):12.5,(300,500):5.0,(500,800):0.0,
            (800,1500):-1.8,(1500,3000):-9.9,(3000,6000):-10.4,(6000,12000):-12.6}
for b, rv in REFSHAPE.items():
    print(f"{b[0]:6d}-{b[1]:5d} {band(*b)-ref:+7.1f} {rv:+14.1f}")
lv = np.array([20*np.log10(np.sqrt((m[i:i+SR]**2).mean())+1e-12)
               for i in range(0, len(m)-SR, SR)])
print(f"\nenergy arc, 1 s buckets (dBFS):")
print("  " + " ".join(f"{v:.0f}" for v in lv))
