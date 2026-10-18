"""Draw the battery-input test circuit used by the ngspice runs.

Writes results/circuit.png. Needs schemdraw (pip install schemdraw).
Values match board.inc and the test decks. Grey parts are test-bench
additions (battery, cable, sources, RoboClaw internals), not PCB parts.
"""
import os
import schemdraw
import schemdraw.elements as elm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "circuit.png")
TB = "#808080"
Y0 = 0      # V_MOTOR rail
YB = -9     # V_BAT rail


def net(d, xy, text, dx=0.15, dy=0.25):
    d.add(elm.Label().at((xy[0] + dx, xy[1] + dy)).label(text, halign="left", valign="bottom", color="#1f4e9c"))


with schemdraw.Drawing(show=False) as d:
    d.config(fontsize=11, unit=3)

    d.add(elm.Label().at((0, 3.2)).label("Battery-input test circuit (sim/battery-input)", fontsize=14,
                                         halign="left"))

    # battery, plug/BMS switch, cable: test bench
    d.add(elm.Battery().up().at((0, -3)).to((0, Y0)).color(TB)
          .label("LiFePO4 14.6 V\n(reversed in\nreverse.cir)", loc="bottom", ofst=0.3))
    d.add(elm.Ground().at((0, -3)))
    d.add(elm.Label().at((-0.4, -1.0)).label("+", fontsize=13))
    d.add(elm.Resistor().right().at((0, Y0)).color(TB).label("Rbat 25 mΩ"))
    d.add(elm.Switch().right().color(TB).label("plug / BMS"))
    d.add(elm.Inductor2(loops=3).right().color(TB).label("cable 1 µH"))
    d.add(elm.Resistor().right().color(TB).label("cable 17 mΩ"))
    d.add(elm.Dot())
    net(d, (12, Y0), "J1+", dx=-0.45, dy=-0.85)

    # Q1: drain on J1+, source to vs, gate down
    d.add(elm.Line().right().at((12, Y0)).to((13.5, Y0)))
    q1 = d.add(elm.PFet(bulk=True).down().anchor("drain").at((13.5, Y0)))
    d.add(elm.Label().at((14.25, 1.1)).label("Q1 SP40P04NK", halign="center"))
    d.add(elm.Line().right().at(q1.source).to((17, Y0)))
    d.add(elm.Dot().at((16, Y0)))
    d.add(elm.Dot().at((17, Y0)))
    net(d, (17, Y0), "vs", dx=-0.7)

    # gate network: R1 to ground, D2 anode on gate, cathode on source
    gx, gy = q1.gate[0], -2.6
    d.add(elm.Line().down().at(q1.gate).to((gx, gy)))
    d.add(elm.Dot().at((gx, gy)))
    d.add(elm.Resistor().down().at((gx, gy)).label("R1\n47 kΩ", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Line().right().at((gx, gy)).to((16, gy)))
    d.add(elm.Zener().up().at((16, gy)).to((16, Y0)).label("D2\nBZT52C15", loc="bottom"))

    # V_MOTOR branch
    d.add(elm.Fuse().right().at((17, Y0)).to((20, Y0)).label("F1 15 A, 4.5 mΩ"))
    d.add(elm.Line().right().at((20, Y0)).to((33, Y0)))
    net(d, (20, Y0), "V_MOTOR")
    for x in (20, 23, 26, 29):
        d.add(elm.Dot().at((x, Y0)))
    d.add(elm.DiodeTVS().up().at((20, -3)).to((20, Y0)).label("D1\nSMCJ18A", loc="bottom"))
    d.add(elm.Ground().at((20, -3)))
    d.add(elm.Capacitor().down().at((23, Y0)).color(TB).label("RoboClaw bulk\n470 / 47 / 0 µF", loc="bottom"))
    d.add(elm.Resistor().down().color(TB).label("ESR\n40-100 mΩ", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Capacitor().down().at((26, Y0)).color(TB).label("4.7 µF\nceramic", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.SourceI().up().at((29, -3)).to((29, Y0)).color(TB).label("IREG regen\n5 / 10 A\n(regen.cir)", loc="bottom"))
    d.add(elm.Ground().at((29, -3)))
    d.add(elm.Diode().up().at((33, -6)).to((33, -3)).color(TB))
    d.add(elm.Diode().up().at((33, -3)).to((33, Y0)).color(TB)
          .label("RoboClaw bridge\nbody diodes ×4\n(reverse.cir)", loc="bottom"))
    d.add(elm.Ground().at((33, -6)))

    # V_BAT branch
    d.add(elm.Line().down().at((17, Y0)).to((17, YB)))
    d.add(elm.Fuse().right().at((17, YB)).to((20, YB)).label("F2 5 A, 17 mΩ"))
    d.add(elm.Dot().at((20, YB)))
    net(d, (20, YB), "V_BAT")
    d.add(elm.DiodeTVS().up().at((20, YB - 3)).to((20, YB)).label("D3\nSMCJ18A", loc="bottom"))
    d.add(elm.Ground().at((20, YB - 3)))
    d.add(elm.Line().right().at((20, YB)).to((22.5, YB)))
    d.add(elm.Resistor().right().at((22.5, YB)).to((25.5, YB)).label("FB1 bead").label("10 mΩ + 0.2 µH\n∥ 120 Ω", loc="bottom"))
    d.add(elm.Line().right().at((25.5, YB)).to((33.5, YB)))
    for x in (25.5, 28.5, 31.5):
        d.add(elm.Dot().at((x, YB)))
    net(d, (25.5, YB), "V_BAT_F")
    d.add(elm.Capacitor().down().at((25.5, YB)).label("C26 10 µF\n(5 µF derated)", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Capacitor().down().at((28.5, YB)).label("C25\n100 nF", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.DiodeTVS(bidirectional=True).down().at((31.5, YB)).label("D10\nSMBJ18CA", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Label().at((33.7, YB)).label("to U11 eFuse\n(off at plug-in;\nOVP 18.0 V)", halign="left"))

    d.add(elm.Label().at((0, YB - 5.5)).label(
        "Black: board parts (kicad/battery-input.kicad_sch, first parts of the power sheet).   "
        "Grey: test-bench parts.", halign="left", fontsize=10))

    d.save(OUT, dpi=130)
print("wrote", OUT)
