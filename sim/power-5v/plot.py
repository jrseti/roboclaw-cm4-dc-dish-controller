"""Plot the 5 V buck simulation results (run.sh first). Needs matplotlib."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def load(name):
    with open(os.path.join(R, name)) as f:
        cols = f.readline().split()
    d = np.loadtxt(os.path.join(R, name), skiprows=1)
    return {c.lower(): d[:, i] for i, c in enumerate(cols)}


def thr(ax, y, text, c="r"):
    ax.axhline(y, ls=":", c=c, lw=1)
    ax.annotate(text, (1, y), xycoords=("axes fraction", "data"), ha="right", va="bottom",
                fontsize=8, color=c)


def finish(ax, title, ylabel, xlabel):
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(alpha=.3)
    ax.legend(fontsize=8, loc="best")


# Start-up
d = load("startup.dat")
t = d["time"] * 1e3
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(t, d["v(vout)"], label="5V output")
ax[0].plot(t, d["v(ss)"], label="SS pin")
ax[0].plot(t, d["v(comp)"], label="COMP")
thr(ax[0], 4.75, "CM4 min 4.75 V")
finish(ax[0], "Soft-start into 3 A", "V", "ms")
ax[1].plot(t, d["i(l2)"], label="inductor (average)")
ax[1].plot(t, d["i(vs12)"], label="12V input")
finish(ax[1], "Currents", "A", "ms")
fig.tight_layout()
fig.savefig(os.path.join(R, "startup.png"), dpi=110)

# Load steps
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for k, lab in (("2.5A_built", "0.5 → 3 A, as built"), ("1A_built", "0.5 → 1.5 A, as built"),
               ("2.5A_c46", "0.5 → 3 A, C46 470 pF fitted")):
    d = load(f"loadstep_{k}.dat")
    t = d["time"] * 1e3
    for a, t0 in ((ax[0], 2.0), (ax[1], 4.0)):
        m = (t > t0 - 0.05) & (t < t0 + 0.4)
        a.plot((t[m] - t0) * 1e3, d["v(vout)"][m], label=lab)
for a, title in ((ax[0], "Load applied"), (ax[1], "Load removed")):
    thr(a, 5.25, "CM4 max 5.25 V")
    thr(a, 4.75, "CM4 min 4.75 V")
    finish(a, title, "V", "µs")
fig.suptitle("5V load steps (12.6 V in)")
fig.tight_layout()
fig.savefig(os.path.join(R, "loadstep.png"), dpi=110)

# Loop gain
fig, ax = plt.subplots(2, 1, figsize=(8, 6.5), sharex=True)
for k, lab in (("0.5A_built", "0.5 A, as built"), ("3A_built", "3 A, as built"), ("3A_c46", "3 A, C46 470 pF")):
    d = load(f"loop_{k}.dat")
    f = d["frequency"]
    i0 = np.argmin(np.abs(d["tdb"]))
    pm = 180 + d["tph"][i0]
    ax[0].semilogx(f, d["tdb"], label=f"{lab}: fc {f[i0]/1e3:.1f} kHz, PM {pm:.0f}°")
    ax[1].semilogx(f, d["tph"], label=lab)
ax[0].axhline(0, c="k", lw=.8)
ax[1].axhline(-180, c="r", ls=":", lw=1)
finish(ax[0], "Loop gain (averaged model, injected at FB)", "dB", "")
finish(ax[1], "", "phase (°)", "Hz")
fig.tight_layout()
fig.savefig(os.path.join(R, "loop.png"), dpi=110)

# Ripple
fig, ax = plt.subplots(2, 2, figsize=(11, 6.5))
for v in ("10", "12.6", "17"):
    d = load(f"ripple_{v}.dat")
    t = d["time"] * 1e6
    m = t > t[-1] - 4 / 0.57
    tt = t[m] - t[m][0]
    ax[0, 0].plot(tt, d["v(lx)"][m], label=f"{v} V in")
    ax[0, 1].plot(tt, d["i(l2)"][m], label=f"{v} V in")
    ax[1, 0].plot(tt, (d["v(vout)"][m] - d["v(vout)"][m].mean()) * 1e3, label=f"{v} V in")
    ax[1, 1].plot(tt, (d["v(v12)"][m] - d["v(v12)"][m].mean()) * 1e3, label=f"{v} V in")
finish(ax[0, 0], "Switch node", "V", "µs")
finish(ax[0, 1], "Inductor current (3 A load)", "A", "µs")
finish(ax[1, 0], "5V ripple (AC)", "mV", "µs")
finish(ax[1, 1], "12V rail ripple (AC)", "mV", "µs")
fig.suptitle("Switching ripple at 3 A, 570 kHz (ESL not modelled)")
fig.tight_layout()
fig.savefig(os.path.join(R, "ripple.png"), dpi=110)
print("wrote", R)
