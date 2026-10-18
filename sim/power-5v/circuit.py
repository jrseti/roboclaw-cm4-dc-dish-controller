"""Draw the 5 V buck test circuit used by the ngspice runs.

Writes results/circuit.png. Needs schemdraw (pip install schemdraw).
Values match board.inc. Grey parts are test-bench parts, dashed parts are
DNP on the board, blue names are net labels (same name = same net).
"""
import os
import schemdraw
import schemdraw.elements as elm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "circuit.png")
TB = "#808080"
NET = "#1f4e9c"


def net(d, xy, text, ha="left", va="bottom", dx=0.15, dy=0.15):
    d.add(elm.Label().at((xy[0] + dx, xy[1] + dy)).label(text, halign=ha, valign=va, color=NET))


def text(d, xy, s, ha="left", size=10, color="black"):
    d.add(elm.Label().at(xy).label(s, halign=ha, valign="center", fontsize=size, color=color))


def shunt(d, x, y, el, label, length=2.5, color="black", ls="-"):
    d.add(el.down().at((x, y)).length(length).color(color).linestyle(ls).label(label, loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Dot().at((x, y)))


with schemdraw.Drawing(show=False) as d:
    d.config(fontsize=10, unit=2.5)
    d.add(elm.Label().at((0, 3.0)).label("5 V buck test circuit (sim/power-5v)", fontsize=14, halign="left"))
    Y = 0

    # input (test bench): 12V rail from the power sheet through 0.12 ohm
    d.add(elm.SourceV().up().at((0, -2.5)).to((0, Y)).color(TB))
    d.add(elm.Ground().at((0, -2.5)))
    text(d, (-0.3, -4.0), "12V rail\n(10-17 V,\n0.12 Ω source)", color=TB, size=9)
    d.add(elm.Line().right().at((0, Y)).to((6.5, Y)))
    net(d, (0.2, Y), "12V")
    shunt(d, 2.2, Y, elm.Capacitor(), "C47 100 nF\nC48-C53\n6 × 10 µF")

    # U15 box
    bx0, bx1, by0, by1 = 7.0, 11.0, 1.0, -5.0
    for a, b in (((bx0, by0), (bx1, by0)), ((bx1, by0), (bx1, by1)), ((bx1, by1), (bx0, by1)), ((bx0, by1), (bx0, by0))):
        d.add(elm.Line().at(a).to(b))
    text(d, ((bx0 + bx1) / 2, by0 + 0.9), "U15 AP64501 (570 kHz)", ha="center")
    d.add(elm.Line().at((bx0 - 0.5, Y)).to((bx0, Y)))
    d.add(elm.Line().at((6.5, Y)).to((bx0 - 0.5, Y)))
    text(d, (bx0 + 0.15, Y), "VIN", size=9)
    right = {"SW": Y, "FB": -2.5, "COMP": -4.0}
    for n, y in right.items():
        d.add(elm.Line().at((bx1, y)).to((bx1 + 0.5, y)))
        text(d, (bx1 - 0.15, y), n, ha="right", size=9)
    bottom = {"EN": 8.0, "SS": 10.0}
    for n, x in bottom.items():
        d.add(elm.Line().at((x, by1)).to((x, by1 - 0.5)))
        text(d, (x, by1 + 0.35), n, ha="center", size=9)
    d.add(elm.Resistor().down().at((8.0, by1 - 0.5)).length(2).label("R65\n100k", loc="bottom"))
    net(d, (8.0, by1 - 2.5), "12V", ha="center", va="top", dx=0, dy=-0.1)
    d.add(elm.Capacitor().down().at((10.0, by1 - 0.5)).length(2).label("C54 100 nF\n(20 ms)", loc="bottom"))
    d.add(elm.Ground())

    # FB and COMP pins to their nets; compensation R43 + C56 (C55 DNP)
    net(d, (bx1 + 0.5, right["FB"]), "FB", va="center", dx=0.1, dy=0)
    xc = bx1 + 1.5
    d.add(elm.Line().at((bx1 + 0.5, right["COMP"])).to((xc + 2.0, right["COMP"])))
    d.add(elm.Dot().at((xc, right["COMP"])))
    d.add(elm.Resistor().down().at((xc, right["COMP"])).length(2).label("R43\n20k", loc="bottom"))
    d.add(elm.Capacitor().down().length(2).label("C56\n1.2 nF", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Capacitor().down().at((xc + 2.0, right["COMP"])).length(2).linestyle("--")
          .label("C55 33 pF\n(DNP)", loc="bottom"))
    d.add(elm.Ground())

    # L2 and the 5V rail
    d.add(elm.Inductor2(loops=3).right().at((bx1 + 0.5, Y)).length(3).label("L2 3.3 µH\n30 mΩ"))
    x0 = bx1 + 3.5
    d.add(elm.Line().right().at((x0, Y)).to((x0 + 16.2, Y)))
    net(d, (x0 + 0.2, Y), "5V")
    shunt(d, x0 + 1.6, Y, elm.Capacitor(), "C41-C44\n4 × 10 µF")
    shunt(d, x0 + 3.8, Y, elm.Capacitor(), "C45 100 µF\npolymer\n15 mΩ")
    shunt(d, x0 + 6.0, Y, elm.Capacitor(), "C5 10 µF\nC6 100 nF\n(CM4 sheet)")
    # feedback divider with C46 (DNP)
    xr = x0 + 8.6
    d.add(elm.Dot().at((xr, Y)))
    d.add(elm.Resistor().down().at((xr, Y)).length(2.5).label("R42\n12k", loc="bottom"))
    d.add(elm.Dot().at((xr, -2.5)))
    net(d, (xr, -2.5), "FB", ha="right", dx=-0.15, dy=-0.55)
    d.add(elm.Resistor().down().at((xr, -2.5)).length(2.5).label("R44\n2.2k", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Capacitor().down().at((xr + 2.4, Y)).length(2.5).linestyle("--").label("C46\n470 pF\n(DNP)", loc="bottom"))
    d.add(elm.Line().at((xr + 2.4, -2.5)).to((xr, -2.5)))
    d.add(elm.Dot().at((xr + 2.4, Y)))
    # load (test bench)
    shunt(d, x0 + 13.6, Y, elm.Resistor(), "load\n0.5 / 3 A", color=TB)
    d.add(elm.SourceI().down().at((x0 + 16.2, Y)).length(2.5).color(TB).label("step\n1 / 2.5 A", loc="bottom"))
    d.add(elm.Ground())

    d.add(elm.Label().at((0, -9.8)).label(
        "Black: board parts (kicad/power_5v.kicad_sch; C5/C6 are on the CM4 sheet).  Grey: test-bench parts.  "
        "Dashed: DNP.  Blue: net labels.  Vout = 0.8 V × (1 + 12k/2.2k) = 5.16 V.",
        halign="left", fontsize=9))
    d.save(OUT, dpi=120)
print("wrote", OUT)
