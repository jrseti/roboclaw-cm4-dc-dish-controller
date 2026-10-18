# Power-sheet simulations (ngspice)

Test circuits for the logic power path on the power sheet (`kicad/power.kicad_sch`):
- the U11 eFuse (MX26631DL) with its UVLO, OVP and PGOOD dividers;
- the Q3/Q4 reverse-current blocking FETs;
- the SW1/Q2 power switch and the 12V rail.

The battery and battery-input stage feed it. The U15 buck is modelled as a
load; [../power-5v](../power-5v) covers it in detail. The write-up is
[../power.md](../power.md).

```sh
brew install ngspice
./run.sh                 # writes results/*.log and results/*.dat
python3 plot.py          # needs matplotlib; writes results/*.png
python3 circuit.py       # needs schemdraw; writes results/circuit.png
```

![Test circuit](results/circuit.png)

| File | Contents |
|---|---|
| `models.lib` | MOSFET and TVS models, a behavioural U11 eFuse (`MX26631`) and the buck-as-a-load (`BUCKLOAD`) |
| `board.inc` | The power-sheet netlist, shared by every test. `QSOFT=1` swaps in the proposed slow Q2 turn-on. |
| `source.inc` | Battery, cable and battery-input stage feeding V_BAT_F, plus the RoboClaw motor current |
| `startup.cir` | A full battery plugged in with SW1 already on |
| `sw1.cir` | SW1 switched on with U11 already up, as built and with the slow Q2 turn-on |
| `brownout.cir` | A 15 A, 300 ms motor surge at battery voltages of 12.8, 12.0 and 11.4 V |
| `ovp.cir` | The battery rail held at 21.5 V for 100 ms (braking with the BMS open), then released |
| `circuit.py` | Draws the circuit above |

**Assumptions:**
- Battery: 25 mΩ. Cable: 17 mΩ and 1 µH. Q1: 5 mΩ. F2: 17 mΩ. FB1: 9 mΩ.
- C26 is derated to 5 µF. C48–C53 are derated to 5 µF each.
- C28 is 220 µF with 0.3 Ω ESR (assumed; the datasheet gives no ESR).
- The buck load is 5.16 V at 3 A, 90 % efficient, with a 20 ms soft-start.
- RoboClaw input capacitance: 470 µF.

**The U11 model** reproduces the datasheet's thresholds, delays, dV/dt
ramp, current limit (3.08 A), PGOOD deglitch and reverse blocking.

It doesn't model:
- thermal shutdown;
- the 1.5 × IOL fast trip. The model clamps the current at IOL instead, and
  reports what the load is asking for as `xu11.idem`.

## Results

| Test | Result |
|---|---|
| Start-up | UVLO trips 50 ms after plug-in (C30 filter). U11 turns on 9 ms later and EFUSE_OUT ramps at 0.53 V/ms. PGOOD goes high at 81 ms, 5V is in regulation at 84 ms. The eFuse current never exceeds the 1.4 A load. |
| SW1 on, as built | Q2 surges to 63 A (above its 50 A pulse rating), EFUSE_OUT dips to 4.3 V and is below the PGOOD threshold for 17 µs, so PGOOD drops for 2 ms. The load asks U11 for far more than 1.5 × IOL, so a real U11 would fast-trip. |
| SW1 on, slow Q2 turn-on | With R22 33k, 33k in series with SW1 and 47 nF gate-to-drain, the surge is 1.4 A, EFUSE_OUT doesn't move, and PGOOD stays high. The 12V rail rises in 2.6 ms. |
| Brownout | During a 15 A surge, EFUSE_OUT falls about 0.9 V. PGOOD stays high at 12.8 V and 12.0 V. At 11.4 V it never comes up, because EFUSE_OUT (11.2 V) is below the 11.41 V rising threshold. |
| OVP | U11 cuts off within microseconds of the rail passing 17.96 V. The 5V rail falls below 4.75 V 1.8 ms later, so the CM4 resets. It's back 33 ms after the rail drops below 16.78 V. |
