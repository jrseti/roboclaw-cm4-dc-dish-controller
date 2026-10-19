# USB port-power simulations (ngspice)

Test circuits for USB port power on the USB sheet (`kicad/usb.kicad_sch`).
U4 (AP22653) is a current-limited switch from the 5V rail to VBUS, which
feeds both USB-A ports (USB1) and the two expansion ports (J2).

The 5V rail is the averaged buck model from [../power-5v](../power-5v), so
U4's load steps load the CM4's real supply. The write-up is
[../usb-power.md](../usb-power.md).

```sh
brew install ngspice
./run.sh                 # writes results/*.log and results/*.dat
python3 plot.py          # needs matplotlib; writes results/*.png
python3 circuit.py       # needs schemdraw; writes results/circuit.png
```

![Test circuit](results/circuit.png)

| File | Contents |
|---|---|
| `models.lib` | Behavioural U4 (`AP22653`) and the SMF6.0A VBUS TVS |
| `board.inc` | 5V buck (from `../power-5v/board.inc`), the CM4 load, U4 and the VBUS capacitors |
| `hotplug.cir` | A device plugged into a port while another draws 0.5 A. Device capacitance 10 µF (the USB maximum) or 47 µF, U4 at typical or maximum on-resistance. |
| `short.cir` | A dead short on a port for 5 ms |
| `dcload.cir` | VBUS against total port load, 0–1.7 A |
| `circuit.py` | Draws the circuit above |

**U4 model**, from the datasheet:
- on-resistance 65 mΩ typical, 135 mΩ maximum;
- current limit 1.735 A (R17 15k), held at constant current while
  overloaded;
- folds back to 0.47 A into a dead short;
- settles to the limit about 5 µs after an overload starts.

It doesn't model thermal shutdown or the 6 ms fault-flag blanking.

**Other assumptions:**
- CM4, hub and Ethernet load: 1.4 A on 5V.
- C7: 100 µF tantalum with 0.1 Ω ESR.
- C9–C12 and C22: derated to 6 µF each.
- 20 mΩ of copper from U4 to the connectors.
- Device cable: 0.2 Ω and 1 µH.

## Results

| Test | Result |
|---|---|
| Hot-plug, 10 µF, U4 typical | VBUS on the other ports droops **120 mV** (to 5.00 V). 5V dips to 5.12 V. U4 peaks at 1.5 A. |
| Hot-plug, 47 µF, U4 typical | VBUS droops 219 mV (to 4.90 V). 5V dips to 5.05 V. U4 briefly reaches 2.1 A before its limit takes hold. |
| Hot-plug, 47 µF, U4 135 mΩ | VBUS droops 248 mV (to 4.83 V). 5V dips to 5.07 V. |
| Port short | U4 spikes to 11.4 A for about 3 µs, then holds 0.49 A. 5V dips to 4.94 V, touches 5.251 V for 8 µs as U4 cuts back, and peaks at 5.24 V when the short is removed. VBUS is back above 4.75 V 0.5 ms after the short is removed. |
| DC load | VBUS at 1.7 A: 5.02 V with U4 typical, 4.90 V with U4 at 135 mΩ. The 5V rail holds at 5.16 V. |
