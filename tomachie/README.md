# Tomachie design review

This directory holds the output of a Tomachie review of the `kicad/` project.
Tomachie is an automated schematic review service. It reads the KiCad schematic,
applies part datasheet limits, and reports power, connectivity, EMC/ESD and
test coverage findings.

These files are a snapshot of one review run. They describe the schematic as it
was when it was uploaded, not as it is now. Re-run the review after schematic
changes and replace the whole directory.

| | |
|---|---|
| Tool | Tomachie 5.208 |
| Run | Job 17953055, 2026-11-12 |
| Input | KiCad 10 project `kicad/cm4-robo-controller.kicad_pro`, 13 sheets |
| Scope | Schematic only. Tomachie does not see the PCB layout, routing or thermal data. |

## Files

| File | What it is | Open with |
|---|---|---|
| `TomachieReview.pdf` | The full review report, about 530 pages. Start here. | Any PDF viewer |
| `cm4-robo-controller_bom.csv` | Bill of materials grouped by part number, as Tomachie read it from the schematic | Spreadsheet |
| `cm4-robo-controller.edif` | Netlist in EDIF 2.0.0 format, 183 nets | EDA tools that import EDIF |
| `cm4-robo-controller.pdn.json` | Power delivery network model: rails, sources, loads, grounds and the values entered for the review | Text editor, JSON viewer |
| `cm4-robo-controller.power_tree.drawio` | Power tree diagram, from the battery input to every rail | draw.io / diagrams.net |
| `cm4-robo-controller.dtso` | Generated Linux devicetree overlay source for the buses the CM4 masters. This run holds only SPI0. | Text editor, `dtc` |
| `cm4-robo-controller-markup.zip` | Copies of the schematic sheets with Tomachie's test coverage markup drawn on | KiCad 10 |

### TomachieReview.pdf

The report's main sections:

1. **Design summary.** Overall score, part and net counts, and footprint naming.
2. **Component value properties.** Value fields that are not a value, and
   capacitor voltage derating.
3. **Pin connectivity.** Hidden net connections, open-collector pull-ups, and diode
   and capacitor polarity.
4. **Power.** Rail voltages and currents, regulator enables, DC voltage drop,
   short-circuit protection and the power tree.
5. **Connector pinouts**, 6. **Indicators** and 7. **Switches.**
8. **Low-speed serial interfaces**, 9. **High-speed serial interfaces** and
   10. **Memory interface.**
11. **Functional analysis.** Reset straps and circuit-level findings.
12. **Designer annotated nets.**
13. **EMC and ESD protection.** Connector shell grounding and the ESD/TVS audit.
14. **Design for test.** Test point coverage, flying probe access and inspection.
15. **Component properties.** Symbol and footprint library checks.

Sections marked "AI-Assisted" are generated observations to investigate. They are
not pass or fail results. Some findings are false positives. For example, the
report flags VBUS_USBC as unprotected, but F5 is the fuse right after USBC1.
Check each finding against the schematic before changing anything.

The rail voltages and motor currents in section 4 come from values typed into
the Tomachie web form, not from the schematic. Section 4.1 lists them.

### cm4-robo-controller-markup.zip

The zip holds a copy of every schematic sheet and the project file. Tomachie adds
a "testability confidence" percentage beside each pin it scored, in traffic-light
colours. A low figure marks a joint whose solder defects test is unlikely to
catch. Report section 14 explains the scoring and the defect rates it assumed.

Extract the zip into a new, empty folder and open the `.kicad_pro` there. Never
extract it into `kicad/`. The copies would overwrite the working schematic.

### cm4-robo-controller.dtso

The overlay is a starting point, not a finished file. Tomachie marks every
place it could not decide from the schematic with `NEEDS REVIEW` or `NOT TRACED`.
This run produced only an SPI0 block with no devices. The I2C buses are not in it.

The file warns that `&spi0` is not declared by the SoC devicetree. On Raspberry
Pi OS the label exists, and the stock SPI overlays use it, so the warning does not
apply there. Nothing on the board uses SPI0. It only goes out to header J4, so
any device on J4 belongs in its own overlay.

### cm4-robo-controller_bom.csv

This BOM is Tomachie's reading of the schematic, used to check its results. For
ordering, export the BOM from KiCad, which carries the MPN, Manufacturer and
LCSC Part fields.

## Notes

- The zip is about 17 MB and the PDF about 6 MB. Consider Git LFS or keeping
  only the latest run if the repository grows.
- The online version of the report is linked from the Tomachie job page. It can
  show newer results than these files.
