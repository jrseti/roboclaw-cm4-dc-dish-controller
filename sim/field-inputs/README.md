# Field-input simulations (ngspice)

Test circuits for the six field-wired RoboClaw inputs on the Robo sheet
(`kicad/robo.kicad_sch`). Each has a 5.1k pull-up to RC_5V, a polymer ESD
suppressor, and a 100 Ω + 10 nF filter:

| Inputs | Connector | RoboClaw pin | Parts |
|---|---|---|---|
| Elevation Hall A, B | J8-2, J8-3 | EN1_A, EN1_B | R47/D16/R49/C57, R51/D18/R53/C59 |
| E-stop | J10-1 | S3 | R48/D17/R50/C58 |
| Elevation and azimuth limits | J12-1, J13-1 | S4, S5 | R52/D19/R54/C60, R55/D20/R56/C61 |

The write-up is [../field-inputs.md](../field-inputs.md).

```sh
brew install ngspice
./run.sh                 # writes results/*.log and results/*.dat
python3 plot.py          # needs matplotlib; writes results/*.png and results/hall_timing.txt
python3 circuit.py       # needs schemdraw; writes results/circuit.png
```

![Test circuit](results/circuit.png)

| File | Contents |
|---|---|
| `models.lib` | Polymer ESD suppressor, a 5 V TVS diode for comparison, RoboClaw input pin, open-collector output, cable section |
| `board.inc` | One input channel (`FIELDIN`), used for every input. `TVS=1` swaps the polymer part for a 5 V TVS diode. |
| `hall.cir` | Open-collector Hall quadrature through 2 m of cable, at 300 Hz, 1, 3 and 10 kHz per channel |
| `noise.cir` | Motor PWM coupled into the signal wire (100 and 400 pF), with the line high and low |
| `switch.cir` | A normally-closed limit switch opening, with contact bounce |
| `esd.cir` | IEC 61000-4-2 ±8 kV contact discharge on the terminal, with the polymer part and with a 5 V TVS diode |
| `circuit.py` | Draws the circuit above |

**Assumptions:**
- **RoboClaw inputs:** 3.3 V CMOS, 5 V tolerant. Switching thresholds taken
  as 2.3 V (high) and 1.0 V (low). The manual doesn't give thresholds or
  clamp ratings.
- **Pin model:** 10 pF, with clamps to 0 V and 5.5 V.
- **Hall outputs:** open-collector, 20 Ω when on.
- **Cable:** 2 m, 0.1 Ω/m, 0.6 µH/m, 60 pF/m.
- **Motor PWM:** 20 kHz, 14.6 V, 50 ns edges. The RoboClaw manual doesn't
  give its PWM frequency, but only the edges matter here.
- **ESD gun:** simplified as 150 pF and 330 Ω, without the sub-nanosecond
  first peak.
- **Polymer suppressor (TPESD0402G12V):** triggers at 450 V, clamps at
  40 V, both from its datasheet.

## Results

| Test | Result |
|---|---|
| Hall edges | Rising edges arrive 32 µs late; the 5.1k pull-up charges the 10 nF (51 µs time constant). Falling edges arrive 2 µs late. The quadrature edge spacing keeps 96 %, 88 %, 63 % and 23 % of its nominal value at 300 Hz, 1 kHz, 3 kHz and 10 kHz per channel (1,200 to 40,000 counts/s). |
| Motor PWM noise | Line high: the pin stays between 4.72 and 5.54 V. Line low: it stays between −0.20 and +0.24 V. That's with 400 pF of coupling; the thresholds are 2.3 V and 1.0 V. |
| Limit switch | The input reads tripped 32 µs after the contact opens. It follows contact bounce: a re-close at 1.15 ms clears it, and it trips again at 1.33 ms. |
| ESD, as built | The terminal reaches 450 V, then clamps at about 63 V. The RoboClaw pin reaches 7.3 V (+8 kV) or −1.75 V (−8 kV), and the pin's own clamp takes about 0.4 A for about 250 ns. |
| ESD, 5 V TVS diode | The terminal clamps at 17 V (+8 kV) or −11 V (−8 kV). The pin stays between 2.7 and 6.0 V, and essentially no current goes into its clamp. |
