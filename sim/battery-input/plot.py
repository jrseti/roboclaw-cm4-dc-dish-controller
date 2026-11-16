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

# Regen with F1 open: D29 returns the braking current until the BMS opens
fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
for i in ("5", "10"):
    d = load(f"regen_{i}A_f1open.dat")
    d0 = load(f"regen_{i}A.dat")
    t = d["time"] * 1e3
    ax[0].plot(t, d["v(vm)"], label=f"{i} A regen, F1 open")
    ax[0].plot(d0["time"] * 1e3, d0["v(vm)"], ":", c=ax[0].lines[-1].get_color(), label=f"{i} A regen, F1 intact")
    ax[1].plot(t, d["i(vsd29)"], label=f"{i} A regen")
    ax[2].plot(t, d["p_d29"], label=f"{i} A regen")
ax[0].axhline(17.96, ls=":", c="r", lw=1, label="U11 OVP 18.0 V")
ax[1].axhline(5, ls=":", c="r", lw=1, label="SS54 IF(AV) 5 A")
for a in ax:
    a.axvline(4, ls=":", c="k", lw=1)
ax[0].set_title("V_MOTOR (BMS opens at 4 ms)"); ax[0].set_ylabel("V")
ax[1].set_title("D29 current"); ax[1].set_ylabel("A")
ax[2].set_title("D29 power"); ax[2].set_ylabel("W")
for a in ax:
    a.set_xlabel("ms"); a.grid(alpha=.3); a.legend(fontsize=8)
fig.suptitle("Regen with F1 open: D29 is the only return path")
fig.tight_layout(); fig.savefig(os.path.join(R, "regen_f1open.png"), dpi=110)

# Reverse polarity, Q1 failed short: F1 intact, and F1 open
fig, ax = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True)
for a, key, title in [(ax[0], "reverse_q1short1", "F1 intact"), (ax[1], "reverse_q1short1_f1open", "F1 open")]:
    d = load(f"{key}.dat")
    t = d["time"] * 1e3
    if title == "F1 intact":
        a.plot(t, -d["if1"], label="F1 (15 A)")
    a.plot(t, -d["if2"], label="F2 (5 A)")
    a.plot(t, d["id29"], label="D29 (SS54, 5 A)")
    a.set_title(f"Reversed battery, Q1 failed short, {title}")
    a.set_xlabel("ms"); a.grid(alpha=.3); a.legend()
ax[0].set_ylabel("A")
fig.tight_layout(); fig.savefig(os.path.join(R, "reverse.png"), dpi=110)
print("wrote", R)
