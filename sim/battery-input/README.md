# Battery-input simulations (ngspice)

Test circuits for the battery input stage (`kicad/battery-input.kicad_sch`):
Q1 reverse-polarity P-MOSFET, D2/R1 gate network, F1/F2, TVS diodes D1/D3,
and the first parts on each output (RoboClaw input capacitance on V_MOTOR;
FB1, C25/C26 and D10 on V_BAT_F ahead of the U11 eFuse).

```sh
brew install ngspice
./run.sh                 # writes results/*.log and results/*.dat
python3 plot.py          # needs matplotlib; writes results/*.png
python3 circuit.py       # needs schemdraw; writes results/circuit.png
```

![Test circuit](results/circuit.png)

| File | Contents |
|---|---|
| `models.lib` | Behavioural models fitted to datasheet numbers (no vendor models exist for these LCSC parts) |
| `board.inc` | The input stage netlist, shared by every test |
| `hotplug.cir` | Fully charged battery (14.6 V) plugged in through 1 µH of cable |
| `regen.cir` | Braking current returned to V_MOTOR, then the battery BMS opens |
| `reverse.cir` | Battery reversed, with Q1 healthy and with Q1 failed short |
| `circuit.py` | Draws the circuit above (black: board parts, grey: test-bench parts) |

Assumptions: battery + BMS 25 mΩ; 1 m of 14 AWG pair (1 µH, 17 mΩ);
ATO fuse cold resistance 4.5 mΩ (15 A) and 17 mΩ (5 A); C26 derated to 5 µF.
The RoboClaw's input capacitance is not published, so `hotplug` runs
470 µF, 47 µF and none. The results show trends, not exact values.

## Results

**Hot-plug** (`results/hotplug.png`)

| RoboClaw input caps | V_MOTOR peak | V_BAT_F peak | Cable peak | TVS current |
|---|---|---|---|---|
| 470 µF | 14.6 V (no overshoot) | 14.6 V | 113 A | none |
| 47 µF | 17.3 V | 17.4 V | 61 A | none |
| none | 21.8 V | 23.7 V | 37 A | 4.6 A (D1), 3 A (D10), brief |

- Every case stays far below Q1's 40 V and the RoboClaw's 34 V rating.
- U11 is still held off when the battery is first connected, so the 23.7 V
  spike does not trip its OVP.
- Q1's source-gate voltage rises through R1 over about 1 ms and settles at
  14.4 V, under D2's 15 V clamp. Until the channel turns on, Q1's body diode
  carries the inrush current.
- The 113 A peak lasts tens of µs, a tiny I²t compared with an ATO fuse. It
  will make a spark at the connector.

**Regen with the BMS opening** (`results/regen.png`)

| Braking current | V_MOTOR before | V_MOTOR after BMS opens | D1 + D3 power |
|---|---|---|---|
| 5 A | 14.9 V | 21.4 V | 107 W |
| 10 A | 15.1 V | 21.9 V | 217 W |

- With the battery connected, Q1 returns the braking current and the rail
  rises by only about 0.5 V.
- If the BMS opens, D1 and D3 clamp the rail at about 21–22 V. That is safe
  for the RoboClaw, but at 100–200 W the TVS diodes can only absorb it for
  milliseconds. Sustained regen into an open battery will destroy them.
- V_BAT_F follows the rail above U11's OVP threshold
  (1.21 V × 193k/13k ≈ 18.0 V), so U11 disconnects the 5 V supply and the
  CM4 loses power.

**Reverse polarity** (`results/reverse.png`)

- Q1 healthy: no current flows (nA).
- Q1 failed short: about 273 A flows through D1, D3 and the RoboClaw's
  bridge diodes. That is 203 A in F1 and 70 A in F2, more than 13× their
  ratings, so both fuses blow quickly. The battery BMS's short-circuit
  protection will probably open first.
