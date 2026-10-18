"""Plot the battery-input simulation results (run.sh first). Needs matplotlib."""
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


# Hot-plug
cases = [("470u", "RoboClaw 470 µF"), ("47u", "RoboClaw 47 µF"), ("1p", "no RoboClaw caps")]
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for key, label in cases:
    d = load(f"hotplug_{key}.dat")
    t = d["time"] * 1e6
    m = t < 100
    ax[0, 0].plot(t[m], d["v(vm)"][m], label=label)
    ax[0, 1].plot(t[m], d["v(vbf)"][m], label=label)
    ax[1, 0].plot(t[m], d["i(lcab)"][m], label=label)
    ax[1, 1].plot(t / 1e3, d["vsg"], label=label)
ax[0, 0].axhline(20.0, ls=":", c="r", lw=1, label="D1 VBR min 20 V")
ax[0, 1].axhline(17.96, ls=":", c="r", lw=1, label="U11 OVP 18.0 V")
ax[1, 1].axhline(15, ls=":", c="r", lw=1, label="D2 15 V clamp")
for a, t_, y in [(ax[0, 0], "V_MOTOR", "V"), (ax[0, 1], "V_BAT_F (U11 input)", "V"),
                 (ax[1, 0], "Battery cable current", "A"), (ax[1, 1], "Q1 V(source-gate)", "V")]:
    a.set_title(t_); a.set_ylabel(y); a.grid(alpha=.3); a.legend(fontsize=8)
for a in ax[:, 0].tolist() + [ax[0, 1]]:
    a.set_xlabel("µs")
ax[1, 1].set_xlabel("ms")
fig.suptitle("Hot-plug: 14.6 V battery, 1 µH / 42 mΩ cable+cell, plug at 10 µs")
fig.tight_layout(); fig.savefig(os.path.join(R, "hotplug.png"), dpi=110)

# Regen with BMS opening at 4 ms
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
for i in ("5", "10"):
    d = load(f"regen_{i}A.dat")
    t = d["time"] * 1e3
    ax[0].plot(t, d["v(vm)"], label=f"{i} A regen: V_MOTOR")
    ax[0].plot(t, d["v(vbf)"], "--", label=f"{i} A regen: V_BAT_F")
    ax[1].plot(t, d["v(vm)"] * (d["i(vsd1)"] + d["i(vsd3)"]), label=f"{i} A regen")
ax[0].axhline(17.96, ls=":", c="r", lw=1, label="U11 OVP 18.0 V")
ax[0].axvline(4, ls=":", c="k", lw=1)
ax[0].set_title("Voltage (BMS opens at 4 ms)"); ax[0].set_ylabel("V")
ax[1].set_title("Power in D1 + D3"); ax[1].set_ylabel("W")
for a in ax:
    a.set_xlabel("ms"); a.grid(alpha=.3); a.legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(R, "regen.png"), dpi=110)

# Reverse polarity, Q1 failed short
d = load("reverse_q1short1.dat")
t = d["time"] * 1e3
fig, ax = plt.subplots(figsize=(6, 3.6))
ax.plot(t, -d["if1"], label="F1 (15 A)")
ax.plot(t, -d["if2"], label="F2 (5 A)")
ax.set_title("Reversed battery, Q1 failed short: fuse current")
ax.set_xlabel("ms"); ax.set_ylabel("A"); ax.grid(alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(R, "reverse.png"), dpi=110)
print("wrote", R)
