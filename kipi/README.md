# KiPI power integrity analysis

This directory holds a KiPI analysis of the board layout. KiPI is a power integrity
simulator that runs as a KiCad plugin or on its own. It meshes the copper of each
power and ground net, solves the DC voltage drop and current density, checks via
currents, and estimates copper temperature. It works from the routed PCB, so it
complements the [Tomachie review](../tomachie/README.md), which sees only the
schematic.

| | |
|---|---|
| Report | [cm4-robo-controller_kipi_report.pdf](cm4-robo-controller_kipi_report.pdf), 57 pages |
| Tool | KiPI 1.0.1+tomachie.7, the Tomachie fork of [drewsum/KiPI](https://github.com/drewsum/KiPI) |
| Run | 2026-11-13, worst-case currents and resistances, 60 °C ambient, no airflow |
| Board | `kicad/cm4-robo-controller.kicad_pcb`, 4 layers, 1 oz copper |
| Power tree | Imported from [tomachie/cm4-robo-controller.pdn.json](../tomachie/), Tomachie 5.209 |

The report is a snapshot of the board and power tree at the time of the run. Re-run
it after layout changes that touch power or ground copper.

## Worst case solved

The worst case assumes everything at its maximum at once, with the battery at its
10 V minimum:

- Both motors running at full load: 5.5 A on the elevation actuator and 0.6 A on the
  azimuth motor.
- The 5 V rail at 3.8 A: the CM4 at 1.8 A, 1 A on the USB-A ports and 1 A drawn
  from the J4 header.

## Results

| Check | Result |
|---|---|
| Loads with a voltage window | All 14 in range |
| CM4 5 V supply | 4.996 V, 246 mV inside its tolerance |
| USB-A port supply at 1 A | 4.851 V, 100 mV above the USB minimum of 4.75 V |
| 3.3 V loads | All in range. The GPS receiver is lowest at 3.275 V. |
| RoboClaw supply | 9.88 V with the battery at 10 V |
| Series parts with a rating | All 7 within rating. F1 carries 6.1 A of 15 A and F2 2.12 A of 5 A. |
| Ground copper | 8.4 mV largest difference, 52 mW loss |
| Copper temperature | In1.Cu, In2.Cu and B.Cu pass |

The ground planes show high current density next to F1 and F2. That is the whole
battery return funnelling into J1 pin 2 between the fuse-holder holes. It is about
23 A/mm² on a 10 mm wide strip of In1.Cu, with negligible voltage drop and heating.

## The two FAIL lines

Both are artifacts of the model, not faults in the board.

**Via current, two vias at (142.60, 77.93) and (145.67, 75.52).** The imported power
tree models the U11 eFuse as taking its input on pin 5. Pin 5 is IN_SYS, a
supply-sense pin that draws about 1 mA through thin tracks and those two vias. The
real power path runs from V_BAT_F through Q3, the reverse-blocking FET, into U11's
IN pins 1 and 2, with no vias. To correct the model in KiPI:

1. Tick the net `Net-(C24-Pad1)`.
2. Add Q3 as a DC connection from its pins 1–3 to its pins 5–8.
3. Change U11's input to pins 1 and 2.

**F.Cu temperature, 142 °C at U15 pin 8.** KiPI puts the buck converter's whole
1.39 W loss onto the small switch-node pad. In the part, most of that heat leaves
through the exposed pad and its thermal vias into the ground planes. The real limit
is U15's junction temperature. With θJA = 45 °C/W from the AP64500 datasheet, the
worst case gives about 110–122 °C at 60 °C ambient, near the recommended 125 °C. A
realistic 5 V load of about 2.5 A gives about 87 °C. Keep the enclosure ventilated
if a HAT on J4 will draw close to 1 A.

## Model simplifications

- Q2 and the NT1 net tie are modelled as shorts, since no resistance is given for
  them. Their real drops are a few millivolts.
- The RoboClaw's 5 V output is modelled as lossless. It feeds only about 50 µA on
  this board.
- U18 and the GPS backup supply have no stated voltage window, so KiPI does not
  judge them.

## Reproducing the run

1. Install the KiPI plugin from the [Tomachie fork](https://github.com/Tomachie/KiPI)
   into KiCad's plugins folder. On macOS that is `~/Documents/KiCad/10.0/plugins/KiPI`.
2. In KiCad's PCB Editor, fill all zones (**B**) and save. KiPI uses the saved fills.
3. Start KiPI from its toolbar button. Its setup is stored in
   `kicad/cm4-robo-controller.kipi-setup.yml`.
4. To refresh the power tree, use **Import…** with `tomachie/cm4-robo-controller.pdn.json`.
   An import replaces the whole power tree, so re-apply the U11 and Q3 corrections
   above afterwards.
5. Choose **Worst case (max)** beside **Solve all**, solve, and export the report.

The report links to a separate interactive 3D view in HTML. That file is not kept
here because of its size. Re-run KiPI to regenerate it.
