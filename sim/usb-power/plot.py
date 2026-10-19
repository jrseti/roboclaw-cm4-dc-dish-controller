"""Plot the USB port-power results (run.sh first). Needs matplotlib."""
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
    ax.annotate(text, (1, y), xycoords=("axes fraction", "data"), ha="right", va="bottom", fontsize=8, color=c)


def finish(ax, title, ylabel, xlabel):
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(alpha=.3)
    ax.legend(fontsize=8)


# Hot-plug
fig, ax = plt.subplots(1, 3, figsize=(13, 4))
for k, lab in (("10u_typ", "10 µF device (USB max), U4 typ"), ("47u_typ", "47 µF device, U4 typ"),
               ("47u_max", "47 µF device, U4 135 mΩ")):
    d = load(f"hotplug_{k}.dat")
    t = (d["time"] - 5e-3) * 1e6
    m = (t > -20) & (t < 300)
    ax[0].plot(t[m], d["v(vbus)"][m], label=lab)
    ax[1].plot(t[m], d["v(vout)"][m], label=lab)
    ax[2].plot(t[m], d["i(vsu4)"][m], label=lab)
pre = load("hotplug_10u_typ.dat")
thr(ax[0], 4.75, "USB min 4.75 V")
thr(ax[1], 4.75, "CM4 min 4.75 V")
thr(ax[2], 1.735, "U4 limit 1.735 A")
finish(ax[0], "VBUS (other ports)", "V", "µs after plug-in")
finish(ax[1], "5V rail (CM4)", "V", "µs after plug-in")
finish(ax[2], "U4 current", "A", "µs after plug-in")
fig.suptitle("USB device hot-plug with 0.5 A already on VBUS and 1.4 A on 5V")
fig.tight_layout()
fig.savefig(os.path.join(R, "hotplug.png"), dpi=110)

# Short
d = load("short.dat")
t = d["time"] * 1e3
fig, ax = plt.subplots(1, 3, figsize=(13, 4))
m = (t > 4.99) & (t < 5.05)
ax[0].plot((t[m] - 5) * 1e3, d["i(vsu4)"][m], label="U4 current")
thr(ax[0], 1.735, "limit 1.735 A")
finish(ax[0], "Short applied (zoom)", "A", "µs after short")
for k, lab in (("v(vbus)", "VBUS"), ("v(vout)", "5V rail (CM4)")):
    ax[1].plot(t[(t > 4) & (t < 12)], d[k][(t > 4) & (t < 12)], label=lab)
thr(ax[1], 4.75, "4.75 V")
finish(ax[1], "Short from 5 to 10 ms", "V", "ms")
m = (t > 4.98) & (t < 5.1)
ax[2].plot((t[m] - 5) * 1e3, d["v(vout)"][m], label="5V rail, short applied")
m2 = (t > 9.98) & (t < 10.8)
ax[2].plot((t[m2] - 10) * 1e3, d["v(vout)"][m2], label="5V rail, short removed")
thr(ax[2], 4.75, "CM4 min 4.75 V")
thr(ax[2], 5.25, "CM4 max 5.25 V")
finish(ax[2], "5V rail at each edge", "V", "µs after the edge")
fig.suptitle("Dead short on a USB port (50 mΩ, 0.3 µH)")
fig.tight_layout()
fig.savefig(os.path.join(R, "short.png"), dpi=110)

# DC load
fig, ax = plt.subplots(figsize=(7, 4))
for k, lab in (("typ", "U4 65 mΩ (typ)"), ("max", "U4 135 mΩ (max)")):
    d = load(f"dcload_{k}.dat")
    m = d["i-sweep"] <= 1.7 + 1e-9   # beyond U4's limit the forced load is meaningless
    ax.plot(d["i-sweep"][m], d["v(vbus)"][m], label=f"VBUS, {lab}")
ax.plot(d["i-sweep"][m], d["v(vout)"][m], "k--", lw=1, label="5V rail")
thr(ax, 4.75, "USB min 4.75 V")
ax.axvspan(1.561, 1.908, color="r", alpha=.08, label="U4 current-limit range (1.56-1.91 A)")
ax.set_ylim(4.6, 5.3)
ax.set_xlim(0, 1.95)
finish(ax, "VBUS at the ports vs total port load", "V", "A (all four ports)")
fig.tight_layout()
fig.savefig(os.path.join(R, "dcload.png"), dpi=110)
print("wrote", R)
