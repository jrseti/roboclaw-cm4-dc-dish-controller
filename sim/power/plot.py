"""Plot the power-sheet simulation results (run.sh first). Needs matplotlib."""
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


def finish(ax, title, ylabel, xlabel="ms"):
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(alpha=.3)
    ax.legend(fontsize=8, loc="best")


# Start-up
d = load("startup.dat")
t = d["time"] * 1e3
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
ax[0, 0].plot(t, d["v(vbatf)"], label="V_BAT_F")
ax[0, 0].plot(t, d["v(efo)"], label="EFUSE_OUT")
ax[0, 0].plot(t, d["v(v12)"], "--", label="12V rail")
ax[0, 0].plot(t, d["v(vo5)"], label="5V (buck output)")
thr(ax[0, 0], 11.41, "PGOOD rises 11.41 V")
finish(ax[0, 0], "Rails", "V")
ax[0, 1].plot(t, d["v(uvlo)"], label="UVLO pin (C30 filtered)")
ax[0, 1].plot(t, d["v(dvdt)"], label="dVdT pin")
thr(ax[0, 1], 1.21, "UVLO 1.21 V")
finish(ax[0, 1], "U11 control pins", "V")
ax[1, 0].plot(t, d["i(vsef)"], label="U11 current")
thr(ax[1, 0], 3.08, "IOL 3.08 A")
finish(ax[1, 0], "eFuse current", "A")
ax[1, 1].plot(t, d["v(pg)"], label="PGOOD_12V (3.3 V logic)")
ax[1, 1].plot(t, d["v(bgate,vbatf)"], label="Q3 gate-source (BGATE)")
finish(ax[1, 1], "PGOOD and blocking FET", "V")
fig.suptitle("Start-up: 12.8 V battery plugged in at 1 ms, SW1 on, 3 A on 5V")
fig.tight_layout()
fig.savefig(os.path.join(R, "startup.png"), dpi=110)

# SW1 switched on
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for q, lab in (("0", "earlier design"), ("1", "as built (R91, C82)")):
    d = load(f"sw1_soft{q}.dat")
    t = d["time"] * 1e3
    m = (t > 149.95) & (t < 150.3)
    ax[0, 0].plot((t[m] - 150) * 1e3, d["v(efo)"][m], label=f"EFUSE_OUT, {lab}")
    ax[0, 1].plot((t[m] - 150) * 1e3, d["i(vsq2)"][m], label=f"Q2 current, {lab}")
    ax[0, 1].plot((t[m] - 150) * 1e3, d["i(vsef)"][m], "--", label=f"U11 current, {lab}")
    m2 = (t > 149) & (t < 180)
    ax[1, 0].plot(t[m2] - 150, d["v(v12)"][m2], label=f"12V rail, {lab}")
    ax[1, 0].plot(t[m2] - 150, d["v(vo5)"][m2], "--", label=f"5V, {lab}")
    ax[1, 1].plot((t[m] - 150) * 1e3, d["v(pg)"][m], label=f"PGOOD, {lab}")
thr(ax[0, 0], 10.58, "PGOOD falls 10.58 V")
thr(ax[0, 1], 4.62, "1.5 x IOL fast trip 4.6 A")
finish(ax[0, 0], "EFUSE_OUT when SW1 closes", "V", "µs after SW1")
finish(ax[0, 1], "Inrush current", "A", "µs after SW1")
finish(ax[1, 0], "12V rail and 5V", "V", "ms after SW1")
finish(ax[1, 1], "PGOOD_12V", "V", "µs after SW1")
fig.suptitle("SW1 switched on with U11 already up (battery 12.8 V)")
fig.tight_layout()
fig.savefig(os.path.join(R, "sw1.png"), dpi=110)

# Brownout
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for v in ("12.8", "12.0", "11.4"):
    d = load(f"brownout_{v}.dat")
    t = d["time"] * 1e3
    m = t > 100
    ax[0].plot(t[m], d["v(efo)"][m], label=f"battery {v} V")
    ax[1].plot(t[m], d["v(pg)"][m], label=f"battery {v} V")
thr(ax[0], 11.41, "PGOOD rises 11.41 V")
thr(ax[0], 10.58, "PGOOD falls 10.58 V")
ax[0].axvspan(150, 450, color="k", alpha=.06)
ax[1].axvspan(150, 450, color="k", alpha=.06)
finish(ax[0], "EFUSE_OUT (15 A motor surge 150-450 ms)", "V")
finish(ax[1], "PGOOD_12V", "V")
fig.tight_layout()
fig.savefig(os.path.join(R, "brownout.png"), dpi=110)

# OVP
d = load("ovp_soft1.dat")
t = d["time"] * 1e3
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
m = (t > 140) & (t < 300)
for k, lab in (("v(vbatf)", "V_BAT_F"), ("v(efo)", "EFUSE_OUT"), ("v(v12)", "12V rail"), ("v(vo5)", "5V")):
    ax[0].plot(t[m], d[k][m], label=lab)
thr(ax[0], 17.96, "OVP 17.96 V")
thr(ax[0], 4.75, "CM4 min 4.75 V")
finish(ax[0], "Battery rail at 21.5 V from 150 to 250 ms", "V")
m = (t > 149.5) & (t < 154)
ax[1].plot(t[m], d["v(vo5)"][m], label="5V")
ax[1].plot(t[m], d["v(v12)"][m], label="12V rail")
ax[1].plot(t[m], d["v(pg)"][m], label="PGOOD_12V")
thr(ax[1], 4.75, "CM4 min 4.75 V")
finish(ax[1], "Hold-up after U11 cuts off (zoom)", "V")
for q, lab in (("0", "earlier design"), ("1", "as built (R22/R91 divider)")):
    d = load(f"ovp_soft{q}.dat")
    t = d["time"] * 1e3
    m = (t > 140) & (t < 160)
    ax[2].plot(t[m], d["vgsq2"][m], label=lab)
thr(ax[2], -20, "Q2 VGS rating -20 V")
ax[2].set_ylim(-22, 0)
finish(ax[2], "Q2 gate-source voltage", "V")
fig.tight_layout()
fig.savefig(os.path.join(R, "ovp.png"), dpi=110)
print("wrote", R)
