"""Draw the power-sheet test circuit used by the ngspice runs.

Writes results/circuit.png. Needs schemdraw (pip install schemdraw).
Values match board.inc. Grey parts are test-bench parts; blue names are
net labels (same name = same net).
"""
import os
import schemdraw
import schemdraw.elements as elm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "circuit.png")
TB = "#808080"
NET = "#1f4e9c"


def net(d, xy, text, ha="left", va="bottom", dx=0.15, dy=0.15):
    d.add(elm.Label().at((xy[0] + dx, xy[1] + dy)).label(text, halign=ha, valign=va, color=NET))


def shunt(d, x, y, el, label, length=2.5, color="black", up=False):
    if up:   # diodes: anode at ground, cathode on the rail
        d.add(el.up().at((x, y - length)).to((x, y)).color(color).label(label, loc="bottom"))
        d.add(elm.Ground().at((x, y - length)))
    else:
        d.add(el.down().at((x, y)).length(length).color(color).label(label, loc="bottom"))
        d.add(elm.Ground())
    d.add(elm.Dot().at((x, y)))


def text(d, xy, s, ha="left", size=10):
    d.add(elm.Label().at(xy).label(s, halign=ha, valign="center", fontsize=size))


with schemdraw.Drawing(show=False) as d:
    d.config(fontsize=10, unit=2.5)
    d.add(elm.Label().at((0, 3.5)).label("Power sheet test circuit (sim/power)", fontsize=14, halign="left"))
    Y = 0

    # ---- source (test bench) and V_BAT_F input parts ----
    d.add(elm.SourceV().up().at((0, -2.5)).to((0, Y)).color(TB))
    d.add(elm.Ground().at((0, -2.5)))
    d.add(elm.Label().at((-0.4, -4.2)).label("battery + battery-input stage\n(VB, 74 mΩ, 1.2 µH;\n15 A motor surge on V_MOTOR)",
                                             halign="left", color=TB, fontsize=9))
    d.add(elm.Line().right().at((0, Y)).to((14.5, Y)))
    net(d, (0.2, Y), "V_BAT_F")
    shunt(d, 2.6, Y, elm.Capacitor(), "C26\n10 µF")
    shunt(d, 4.6, Y, elm.Capacitor(), "C25\n100 nF")
    shunt(d, 6.6, Y, elm.DiodeTVS(bidirectional=True), "D10\nSMBJ18CA")
    # UVLO divider + C30, OVP divider
    d.add(elm.Dot().at((8.8, Y)))
    d.add(elm.Resistor().down().at((8.8, Y)).length(2.5).label("R29\n330k", loc="bottom"))
    d.add(elm.Dot().at((8.8, -2.5)))
    d.add(elm.Resistor().down().at((8.8, -2.5)).length(2.5).label("R32\n56k", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Line().right().at((8.8, -2.5)).to((10.4, -2.5)))
    d.add(elm.Capacitor().down().at((10.4, -2.5)).length(2.5).label("C30\n1 µF", loc="bottom"))
    d.add(elm.Ground())
    net(d, (8.8, -2.5), "UVLO", ha="right", dx=-0.15)
    d.add(elm.Dot().at((12.3, Y)))
    d.add(elm.Resistor().down().at((12.3, Y)).length(2.5).label("R27\n180k", loc="bottom"))
    d.add(elm.Dot().at((12.3, -2.5)))
    d.add(elm.Resistor().down().at((12.3, -2.5)).length(2.5).label("R30\n13k", loc="bottom"))
    d.add(elm.Ground())
    net(d, (12.3, -2.5), "OVP", ha="right", dx=-0.15)

    # ---- Q3 blocking FET: source V_BAT_F (left), drain IN (right), gate BGATE ----
    q3 = d.add(elm.NFet(bulk=True).down().anchor("drain").at((16, Y)))
    text(d, (15.25, 1.4), "Q3 NCE6008AS", ha="center")
    gx = q3.gate[0]
    d.add(elm.Line().down().at(q3.gate).to((gx, -3.6)))
    d.add(elm.Dot().at((gx, -3.6)))
    net(d, (gx, -3.6), "BGATE", dx=0.15, dy=0.1)
    # Q4: drain BGATE (right), source V_BAT_F (left), gate DRV
    q4 = d.add(elm.NFet().down().anchor("drain").at((gx, -3.6)))
    d.add(elm.Line().up().at(q4.source).to((q4.source[0], Y)))
    d.add(elm.Dot().at((q4.source[0], Y)))
    d.add(elm.Line().down().at(q4.gate).length(0.5))
    net(d, (q4.gate[0], q4.gate[1] - 0.5), "DRV", ha="left", va="top", dx=0.15, dy=0.05)
    text(d, (gx - 0.75, -6.9), "Q4 BSS138", ha="center", size=9)

    # IN node, C24
    d.add(elm.Line().right().at((16, Y)).to((19.5, Y)))
    net(d, (17.6, Y), "IN")
    shunt(d, 17.2, Y, elm.Capacitor(), "C24\n100 nF", length=1.8)

    # ---- U11 box ----
    bx0, bx1, by0, by1 = 20.0, 25.0, 1.0, -6.6
    for a, b in (((bx0, by0), (bx1, by0)), ((bx1, by0), (bx1, by1)), ((bx1, by1), (bx0, by1)), ((bx0, by1), (bx0, by0))):
        d.add(elm.Line().at(a).to(b))
    text(d, ((bx0 + bx1) / 2, by0 + 0.9), "U11 MX26631DL eFuse", ha="center")
    left = {"IN": Y, "IN_SYS": -3.0, "UVLO": -4.2, "OVP": -5.4}
    right = {"OUT": Y, "PGTH": -1.8, "PGOOD": -3.0, "BGATE": -4.2, "DRV": -5.4}
    bottom = {"dVdT": 21.3, "ILIM": 23.3}
    for n, y in left.items():
        d.add(elm.Line().at((bx0 - 0.5, y)).to((bx0, y)))
        text(d, (bx0 + 0.15, y), n, size=9)
    for n, y in right.items():
        d.add(elm.Line().at((bx1, y)).to((bx1 + 0.5, y)))
        text(d, (bx1 - 0.15, y), n, ha="right", size=9)
    for n, x in bottom.items():
        d.add(elm.Line().at((x, by1)).to((x, by1 - 0.5)))
        text(d, (x, by1 + 0.35), n, ha="center", size=9)
    for n, lab in (("IN_SYS", "V_BAT_F"), ("UVLO", "UVLO"), ("OVP", "OVP")):
        net(d, (bx0 - 0.5, left[n]), lab, ha="right", va="center", dx=-0.1, dy=0)
    for n, lab in (("PGTH", "PGTH"), ("PGOOD", "PGOOD_12V (to CM4)"), ("BGATE", "BGATE"), ("DRV", "DRV")):
        net(d, (bx1 + 0.5, right[n]), lab, va="center", dx=0.1, dy=0)
    d.add(elm.Capacitor().down().at((bottom["dVdT"], by1 - 0.5)).length(2).label("C29\n100 nF", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Resistor().down().at((bottom["ILIM"], by1 - 0.5)).length(2).label("R26 13k\n(3.08 A)", loc="bottom"))
    d.add(elm.Ground())

    # ---- EFUSE_OUT ----
    xo = bx1 + 0.5
    d.add(elm.Line().right().at((xo, Y)).to((xo + 14.5, Y)))
    net(d, (xo + 0.2, Y), "EFUSE_OUT")
    shunt(d, xo + 4.6, Y, elm.Capacitor(), "C27\n100 nF")
    shunt(d, xo + 6.6, Y, elm.Capacitor(), "C28 220 µF\n0.3 Ω ESR")
    shunt(d, xo + 9.0, Y, elm.DiodeTVS(), "D11\nSMAJ20A", up=True)
    d.add(elm.Dot().at((xo + 11.0, Y)))
    d.add(elm.Resistor().down().at((xo + 11.0, Y)).length(2.5).label("R28\n82k", loc="bottom"))
    d.add(elm.Dot().at((xo + 11.0, -2.5)))
    d.add(elm.Resistor().down().at((xo + 11.0, -2.5)).length(2.5).label("R31\n10k", loc="bottom"))
    d.add(elm.Ground())
    net(d, (xo + 11.0, -2.5), "PGTH", ha="right", dx=-0.15)

    # ---- Q2 power switch: source EFUSE_OUT (left), drain 12V (right) ----
    xs = xo + 15
    d.add(elm.Line().right().at((xo + 14.5, Y)).to((xs, Y)))
    q2 = d.add(elm.PFet(bulk=True).down().flip().anchor("source").at((xs, Y)))
    text(d, (xs + 0.75, 1.4), "Q2 DMP6023LE", ha="center")
    qg = q2.gate[0]
    d.add(elm.Line().down().at(q2.gate).to((qg, -2.6)))
    d.add(elm.Dot().at((qg, -2.6)))
    d.add(elm.Resistor().left().at((qg, -2.6)).to((xs - 2.0, -2.6)).label("R22 33k", loc="bottom"))
    d.add(elm.Line().up().at((xs - 2.0, -2.6)).to((xs - 2.0, Y)))
    d.add(elm.Dot().at((xs - 2.0, Y)))
    # slow turn-on: R91 in series with SW1, C82 gate-to-drain (12V)
    d.add(elm.Resistor().down().at((qg, -2.6)).length(2.0).label("R91\n33k", loc="bottom"))
    d.add(elm.Switch().down().length(2.0).label("SW1", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Line().right().at((qg, -2.6)).to((qg + 1.6, -2.6)))
    d.add(elm.Capacitor().up().at((qg + 1.6, -2.6)).to((qg + 1.6, Y)).label("C82\n47 nF", loc="top"))
    d.add(elm.Dot().at((qg + 1.6, Y)))

    # ---- 12V rail ----
    x12 = q2.drain[0]
    d.add(elm.Line().right().at(q2.drain).to((x12 + 8.0, Y)))
    net(d, (x12 + 0.2, Y), "12V")
    shunt(d, x12 + 2.6, Y, elm.Capacitor(), "C47 100 nF\nC48-C53\n6 × 10 µF")
    d.add(elm.Dot().at((x12 + 5.0, Y)))
    d.add(elm.Resistor().down().at((x12 + 5.0, Y)).length(2).label("R23\n3k", loc="bottom"))
    d.add(elm.LED().down().length(1.8).label("LED3", loc="bottom"))
    d.add(elm.Ground())
    bx = x12 + 8.0
    for a, b in (((bx, 1.0), (bx + 2.5, 1.0)), ((bx + 2.5, 1.0), (bx + 2.5, -1.4)),
                 ((bx + 2.5, -1.4), (bx, -1.4)), ((bx, -1.4), (bx, 1.0))):
        d.add(elm.Line().at(a).to(b).color(TB))
    text(d, (bx + 1.25, -0.2), "U15", ha="center")
    d.add(elm.Label().at((bx, -2.4)).label("buck as a load:\n5.16 V, 3 A, 90 %,\n20 ms soft-start\n(detail: sim/power-5v)",
                                           halign="left", valign="top", color=TB, fontsize=9))

    d.add(elm.Label().at((0, -10.4)).label(
        "Black: board parts (kicad/power.kicad_sch).  Grey: test-bench parts.  Blue: net labels (same name = same net).  "
        "Q3/Q4 block reverse current; U11 cuts off below UVLO (7.8 V) and above OVP (18.0 V); PGOOD_12V is high above 11.4 V.\nR22/R91 halve Q2's gate drive and C82 ramps the 12V rail in ~2.6 ms when SW1 closes.",
        halign="left", fontsize=9))
    d.save(OUT, dpi=120)
print("wrote", OUT)
