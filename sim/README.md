# Circuit simulations

ngspice simulations of parts of the controller board. They check behaviour
that depends on timing, parasitics or transients, which is hard to work out
by hand.

## Contents

| Study | Write-up | Files |
|---|---|---|
| Battery input: hot-plug, regen with the BMS opening, reverse polarity | [battery-input.md](battery-input.md) | [battery-input/](battery-input/) |
| Power sheet: U11 eFuse start-up, SW1/Q2 switch-on, low-battery brownout, over-voltage cutoff | [power.md](power.md) | [power/](power/) |
| Power_5V sheet: U15 buck start-up, load steps, loop stability, switching ripple | [power-5v.md](power-5v.md) | [power-5v/](power-5v/) |
| Field inputs: Hall encoder edges, motor PWM noise, limit/E-stop trip, ESD on the terminals | [field-inputs.md](field-inputs.md) | [field-inputs/](field-inputs/) |
| USB port power: device hot-plug droop, port short, VBUS under load | [usb-power.md](usb-power.md) | [usb-power/](usb-power/) |

Each write-up describes the circuit, explains the results plots and gives an
assessment. The study folder holds the netlists, models and scripts. Its own
README lists the files and the assumptions.

## Running

You need:
- [ngspice](https://ngspice.sourceforge.io/) (macOS: `brew install ngspice`);
- Python 3 with `matplotlib` and `schemdraw`, for the plots and the circuit
  diagram (`pip install matplotlib schemdraw`).

Each study runs the same way:

```sh
cd sim/battery-input # or power, power-5v, field-inputs, usb-power
./run.sh             # runs every case; writes results/*.log and results/*.dat
python3 plot.py      # results plots: results/*.png
python3 circuit.py   # circuit diagram: results/circuit.png
```

`run.sh` prints the measured peaks and end values from each run. The `.dat`
and `.log` files are large and are excluded from git; the PNGs are kept.

## How the studies are built

- **Netlists, not KiCad schematics.** Each study is a plain SPICE netlist
  (`.cir`) that copies the relevant part of the KiCad schematic. The
  production schematic needs no simulation models, and its netlist and BOM
  aren't affected.
- **A shared board netlist per study.** In `battery-input`, the board
  circuit is in `board.inc`, and each test (`hotplug.cir`, `regen.cir`,
  `reverse.cir`) adds its own sources and test-bench parts around it.
  `run.sh` passes the varied parameter (capacitance, braking current, Q1
  shorted or not) through a generated `case.inc`. `power` and `power-5v`
  are built the same way.
- **Behavioural ICs.** The eFuse (U11), the buck controller (U15) and the
  USB power switch (U4) have no SPICE models either. Each study's
  `models.lib` models them from their datasheets' thresholds, timings and
  control constants, and lists what is and isn't modelled.
- **Fitted models.** Most parts are LCSC parts with no vendor SPICE model.
  `models.lib` fits behavioural models to each datasheet's headline numbers,
  such as on-resistance, breakdown and clamp voltage, and capacitance. Treat
  the results as trends and margins, not exact values.
- **Keep the drawing in step.** `circuit.py` draws the circuit by hand from
  the same values. If you change a value in `board.inc` or a `.cir` file,
  update `circuit.py` too.

## Adding a study

1. Create `sim/<study>/` with a `board.inc` for the circuit being studied,
   one `.cir` file per test, and a `run.sh`. Copy models from
   `battery-input/models.lib` where they fit.
2. Write `sim/<study>.md` describing the circuit, the results and an
   assessment, and add it to the table above.
