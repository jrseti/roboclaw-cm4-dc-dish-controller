"""Draw the USB port-power test circuit used by the ngspice runs.

Writes results/circuit.png. Needs schemdraw (pip install schemdraw).
Values match board.inc. Grey parts are test-bench parts; blue names are
net labels.
"""
import os
import schemdraw
import schemdraw.elements as elm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "circuit.png")
TB = "#808080"
NET = "#1f4e9c"


def net(d, xy, text, ha="left", va="bottom", dx=0.15, dy=0.15):
    d.add(elm.Label().at((xy[0] + dx, xy[1] + dy)).label(text, halign=ha, valign=va, color=NET))


def box(d, x0, y0, x1, y1, color="black"):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        d.add(elm.Line().at(a).to(b).color(color))


def shunt(d, x, y, el, label, length=2.5, color="black"):
    d.add(el.down().at((x, y)).length(length).color(color).label(label, loc="bottom"))
    d.add(elm.Ground().color(color))
    d.add(elm.Dot().at((x, y)))


with schemdraw.Drawing(show=False) as d:
    d.config(fontsize=10, unit=2.5)
    d.add(elm.Label().at((0, 3.4)).label("USB port-power test circuit (sim/usb-power)", fontsize=14, halign="left"))
    Y = 0

    # 5V supply (the buck model from sim/power-5v) and CM4 load
    box(d, 0, 1.2, 3.2, -1.6, TB)
    d.add(elm.Label().at((1.6, -0.2)).label("U15 buck\n+ 5V caps\n(power-5v\nmodel)", fontsize=9, color=TB))
    d.add(elm.Line().right().at((3.2, Y)).to((8, Y)))
    net(d, (3.4, Y), "5V")
    shunt(d, 5.0, Y, elm.Resistor(), "CM4, hub,\nEthernet\n1.4 A", color=TB)

    # U4 box
    bx0, bx1, by0, by1 = 8.5, 12.0, 1.0, -2.6
    box(d, bx0, by0, bx1, by1)
    d.add(elm.Label().at(((bx0 + bx1) / 2, by0 + 0.6)).label("U4 AP22653", halign="center"))
    d.add(elm.Line().at((8, Y)).to((bx0, Y)))
    d.add(elm.Label().at((bx0 + 0.15, Y)).label("IN", halign="left", valign="center", fontsize=9))
    d.add(elm.Label().at((bx1 - 0.15, Y)).label("OUT", halign="right", valign="center", fontsize=9))
    d.add(elm.Label().at((bx0 + 0.9, by1 + 0.35)).label("ILIM", halign="center", valign="center", fontsize=9))
    d.add(elm.Label().at((bx1 - 0.9, by1 + 0.35)).label("EN", halign="center", valign="center", fontsize=9))
    d.add(elm.Label().at(((bx0 + bx1) / 2, -0.9)).label("65 / 135 mΩ\n1.735 A limit", fontsize=9, halign="center"))
    d.add(elm.Line().down().at((bx0 + 0.9, by1)).length(0.4))
    d.add(elm.Resistor().down().length(2).label("R17\n15k", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Line().down().at((bx1 - 0.9, by1)).length(0.6))
    net(d, (bx1 - 0.9, by1 - 0.6), "hub PRTPWR\n(D6/D7, R11)", ha="left", va="top", dx=0.2, dy=0.1)

    # VBUS
    d.add(elm.Resistor().right().at((bx1, Y)).to((bx1 + 2.5, Y)).label("trace 20 mΩ"))
    xv = bx1 + 2.5
    d.add(elm.Line().right().at((xv, Y)).to((xv + 14.5, Y)))
    net(d, (xv + 0.2, Y), "VBUS")
    shunt(d, xv + 1.5, Y, elm.Capacitor(), "C7 100 µF\ntantalum\n0.1 Ω ESR")
    shunt(d, xv + 3.8, Y, elm.Capacitor(), "C9-C12, C22\n5 × 10 µF\nC8 100 nF")
    d.add(elm.DiodeTVS().up().at((xv + 6.4, Y - 2.5)).to((xv + 6.4, Y)).label("D8, D9\nSMF6.0A", loc="bottom"))
    d.add(elm.Ground().at((xv + 6.4, Y - 2.5)))
    d.add(elm.Dot().at((xv + 6.4, Y)))
    d.add(elm.Label().at((xv + 8.4, 1.3)).label("USB1 (2 ports), J2 (2 ports)", color=TB, fontsize=9))

    # test loads
    shunt(d, xv + 8.6, Y, elm.Resistor(), "device on\nanother port\n0.5 A", color=TB)
    x = xv + 11.0
    d.add(elm.Dot().at((x, Y)))
    d.add(elm.Switch().down().at((x, Y)).length(1.4).color(TB))
    d.add(elm.Resistor().down().length(1.4).color(TB).label("cable\n0.2 Ω, 1 µH", loc="bottom"))
    d.add(elm.Capacitor().down().length(1.6).color(TB).label("new device\n10 / 47 µF", loc="bottom"))
    d.add(elm.Ground().color(TB))
    x = xv + 14.5
    d.add(elm.Switch().down().at((x, Y)).length(1.4).color(TB))
    d.add(elm.Resistor().down().length(1.6).color(TB).label("short\n50 mΩ", loc="bottom"))
    d.add(elm.Ground().color(TB))

    d.add(elm.Label().at((0, -7.6)).label(
        "Black: board parts (kicad/usb.kicad_sch).  Grey: test bench.  The hot-plug, short and DC-load tests each use "
        "one of the grey loads.", halign="left", fontsize=9))
    d.save(OUT, dpi=120)
print("wrote", OUT)
