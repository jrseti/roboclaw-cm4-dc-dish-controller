"""Plot the field-input results (run.sh first) and print the Hall timing.

Needs matplotlib. Writes results/*.png and results/hall_timing.txt.
RoboClaw inputs are taken as 3.3 V CMOS: high above 2.3 V, low below 1.0 V.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
VIH, VIL = 2.3, 1.0
FREQS = (("300", 300), ("1k", 1e3), ("3k", 3e3), ("10k", 10e3))


def load(name):
    with open(os.path.join(R, name)) as f:
        cols = f.readline().split()
    d = np.loadtxt(os.path.join(R, name), skiprows=1)
    return {c.lower(): d[:, i] for i, c in enumerate(cols)}


def logic(v):
    """Digital level seen by a CMOS input with VIH/VIL thresholds."""
    out = np.zeros(len(v), dtype=int)
    s = 1 if v[0] > VIH else 0
    for i, x in enumerate(v):
        if s == 0 and x > VIH:
            s = 1
        elif s == 1 and x < VIL:
            s = 0
        out[i] = s
    return out


def edges(t, x):
    i = np.nonzero(np.diff(x))[0]
    return t[i + 1], x[i + 1]


def thr(ax, y, text, c="r"):
    ax.axhline(y, ls=":", c=c, lw=1)
    ax.annotate(text, (1, y), xycoords=("axes fraction", "data"), ha="right", va="bottom", fontsize=8, color=c)


# ---- Hall timing ----
lines = ["Hall timing (open-collector Hall, 2 m cable, RoboClaw VIH 2.3 V / VIL 1.0 V)",
         f"{'F/channel':>10} {'counts/s':>9} {'rise delay':>11} {'fall delay':>11} "
         f"{'min A/B edge gap':>17} {'nominal gap':>12} {'gap kept':>9}"]
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for (key, f), a in zip(FREQS, ax.flat):
    d = load(f"hall_{key}.dat")
    t = d["time"]
    la, lb = logic(d["v(pina)"]), logic(d["v(pinb)"])
    # Hall line is low while ctl = 1
    ia, ib = 1 - (d["v(ctla)"] > 0.5), 1 - (d["v(ctlb)"] > 0.5)
    ta, va = edges(t, la)
    tia, via = edges(t, ia)
    rise, fall = [], []
    for tt, vv in zip(tia, via):
        k = np.nonzero((ta >= tt) & (va == vv))[0]
        if len(k):
            (rise if vv == 1 else fall).append(ta[k[0]] - tt)
    tb, _ = edges(t, lb)
    allt = np.sort(np.concatenate([ta, tb]))
    allt = allt[allt > 0.6 / f]
    gap = np.diff(allt).min() if len(allt) > 1 else np.nan
    nom = 1 / (4 * f)
    lines.append(f"{key + ' Hz':>10} {4 * f:9.0f} {np.mean(rise) * 1e6:9.1f} µs {np.mean(fall) * 1e6:9.2f} µs "
                 f"{gap * 1e6:15.1f} µs {nom * 1e6:10.1f} µs {gap / nom * 100:8.0f} %")
    m = t > 0.4 / f
    a.plot(t[m] * 1e3, d["v(pina)"][m], label="EN1_A")
    a.plot(t[m] * 1e3, d["v(pinb)"][m], label="EN1_B")
    a.plot(t[m] * 1e3, 5.5 - 0.5 * (d["v(ctla)"][m] > 0.5), "k", lw=.6, label="Hall A drive (low = on)")
    thr(a, VIH, "VIH 2.3 V")
    thr(a, VIL, "VIL 1.0 V", c="m")
    a.set_title(f"{key} Hz per channel ({4 * f:.0f} counts/s)")
    a.set_xlabel("ms")
    a.set_ylabel("V")
    a.grid(alpha=.3)
    a.legend(fontsize=7, loc="lower right")
fig.suptitle("Hall quadrature at the RoboClaw EN1 pins (open-collector, 5.1k pull-up, 100 Ω + 10 nF)")
fig.tight_layout()
fig.savefig(os.path.join(R, "hall.png"), dpi=110)
txt = "\n".join(lines)
open(os.path.join(R, "hall_timing.txt"), "w").write(txt + "\n")
print(txt)

# ---- Noise ----
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for k, lab, a in (("off", "line high (Hall off / switch open)", ax[0]), ("on", "line low (Hall on / switch closed)", ax[1])):
    for cc in ("", "_400p"):
        d = load(f"noise_{k}{cc}.dat")
        t = d["time"] * 1e6
        a.plot(t, d["v(conna)"], lw=.8, label=f"connector, CC {'400' if cc else '100'} pF")
        a.plot(t, d["v(pina)"], lw=1.6, label=f"RoboClaw pin, CC {'400' if cc else '100'} pF")
    thr(a, VIH, "VIH 2.3 V")
    thr(a, VIL, "VIL 1.0 V", c="m")
    a.set_title(lab)
    a.set_xlabel("µs")
    a.set_ylabel("V")
    a.grid(alpha=.3)
    a.legend(fontsize=7)
fig.suptitle("Motor PWM (14.6 V, 50 ns edges) coupled into a 2 m signal wire")
fig.tight_layout()
fig.savefig(os.path.join(R, "noise.png"), dpi=110)

# ---- Switch ----
d = load("switch.dat")
t = d["time"] * 1e3
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot(t, d["v(conn)"], label="J12-1 (connector)")
ax.plot(t, d["v(pin)"], label="S4 (RoboClaw pin)")
ax.plot(t, 5.5 - 0.5 * (d["v(ctl)"] > 0.5), "k", lw=.6, label="switch (low step = closed)")
thr(ax, VIH, "VIH 2.3 V")
thr(ax, VIL, "VIL 1.0 V", c="m")
ax.set_xlim(0.9, 1.6)
ax.set_title("NC limit switch opening with bounce (high = tripped)")
ax.set_xlabel("ms")
ax.set_ylabel("V")
ax.grid(alpha=.3)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(R, "switch.png"), dpi=110)

# ---- ESD ----
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for k, lab in (("pos", "+8 kV, polymer (as built)"), ("pos_tvs", "+8 kV, 5 V TVS"),
               ("neg", "−8 kV, polymer (as built)"), ("neg_tvs", "−8 kV, 5 V TVS")):
    d = load(f"esd_{k}.dat")
    t = d["time"] * 1e9
    ls = "-" if "tvs" not in k else "--"
    ax[0].plot(t, d["v(pin)"], ls, label=lab)
    ax[1].plot(t, d["icl"] * 1e3, ls, label=lab)
ax[0].axhline(5.5, ls=":", c="r", lw=1)
ax[0].set_title("RoboClaw pin voltage")
ax[0].set_ylabel("V")
ax[1].set_title("Current into the RoboClaw pin's clamp")
ax[1].set_ylabel("mA")
for a in ax:
    a.set_xlabel("ns")
    a.set_xlim(0, 1000)
    a.grid(alpha=.3)
    a.legend(fontsize=8)
fig.suptitle("IEC 61000-4-2 contact discharge on a field-input terminal")
fig.tight_layout()
fig.savefig(os.path.join(R, "esd.png"), dpi=110)
print("wrote", R)
