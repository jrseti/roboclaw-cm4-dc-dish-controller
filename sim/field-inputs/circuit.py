"""Draw the field-input test circuit used by the ngspice runs.

Writes results/circuit.png. Needs schemdraw (pip install schemdraw).
One channel is drawn; all six field inputs (Hall A/B, E-stop, two limits)
use the same circuit. Grey parts are test-bench parts.
"""
import os
import schemdraw
import schemdraw.elements as elm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "circuit.png")
TB = "#808080"
NET = "#1f4e9c"


def net(d, xy, text, ha="left", va="bottom", dx=0.15, dy=0.15):
    d.add(elm.Label().at((xy[0] + dx, xy[1] + dy)).label(text, halign=ha, valign=va, color=NET))


with schemdraw.Drawing(show=False) as d:
    d.config(fontsize=10, unit=2.5)
    d.add(elm.Label().at((0, 3.6)).label("Field-input test circuit (sim/field-inputs), one channel", fontsize=14,
                                         halign="left"))
    Y = 0

    # sensor end (test bench): open-collector Hall output or NC switch
    d.add(elm.Switch().down().at((0, Y)).length(2.5).color(TB)
          .label("Hall output\n(open collector)\nor NC switch", loc="top"))
    d.add(elm.Ground().color(TB))
    # 2 m cable (test bench)
    d.add(elm.Line().right().at((0, Y)).to((0.5, Y)).color(TB))
    d.add(elm.Inductor2(loops=2).right().at((0.5, Y)).to((2.5, Y)).color(TB))
    d.add(elm.Resistor().right().at((2.5, Y)).to((4.5, Y)).color(TB))
    d.add(elm.Label().at((2.5, 1.1)).label("2 m cable: 0.2 Ω, 1.2 µH", color=TB, fontsize=9))
    d.add(elm.Line().right().at((4.5, Y)).to((10, Y)).color(TB))
    d.add(elm.Dot().at((5.4, Y)))
    d.add(elm.Capacitor().down().at((5.4, Y)).length(2).color(TB).label("120 pF", loc="top"))
    d.add(elm.Ground().color(TB))
    # motor lead coupling (test bench)
    d.add(elm.Dot().at((7.0, Y)))
    d.add(elm.Capacitor().down().at((7.0, Y)).length(2).color(TB).label("CC\n100 / 400 pF", loc="bottom"))
    d.add(elm.Line().right().at((7.0, -2)).to((8.6, -2)).color(TB))
    d.add(elm.SourcePulse().down().at((8.6, -2)).length(2.5).color(TB).label("motor lead\nPWM 14.6 V,\n20 kHz", loc="bottom"))
    d.add(elm.Ground().color(TB))

    # board: connector, pull-up, ESD part, 100 ohm + 10 nF filter
    xc = 10
    d.add(elm.Dot(open=True).at((xc, Y)))
    net(d, (xc, Y), "J8-2", ha="center", dx=0, dy=0.35)
    d.add(elm.Line().right().at((xc, Y)).to((xc + 2.6, Y)))
    xp = xc + 1.3
    d.add(elm.Dot().at((xp, Y)))
    d.add(elm.Resistor().up().at((xp, Y)).length(2).label("R47\n5.1k", loc="bottom"))
    net(d, (xp, Y + 2), "RC_5V", ha="center", dx=0, dy=0.1)
    xe = xc + 2.6
    d.add(elm.Dot().at((xe, Y)))
    d.add(elm.DiodeTVS(bidirectional=True).down().at((xe, Y)).length(2.5)
          .label("D16 polymer ESD\n(450 V trigger,\n40 V clamp)", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Resistor().right().at((xe, Y)).to((xe + 3.4, Y)).label("R49 100 Ω"))
    xf = xe + 3.4
    d.add(elm.Dot().at((xf, Y)))
    d.add(elm.Capacitor().down().at((xf, Y)).length(2.5).label("C57\n10 nF", loc="bottom"))
    d.add(elm.Ground())
    d.add(elm.Line().right().at((xf, Y)).to((xf + 2.4, Y)))
    net(d, (xf + 0.3, Y), "EN1_A")
    # RoboClaw pin (test bench)
    xr = xf + 2.4
    d.add(elm.Line().at((xr, Y)).to((xr + 0.6, Y)).color(TB))
    for a, b in (((xr + 0.6, 1.2), (xr + 4.6, 1.2)), ((xr + 4.6, 1.2), (xr + 4.6, -2.6)),
                 ((xr + 4.6, -2.6), (xr + 0.6, -2.6)), ((xr + 0.6, -2.6), (xr + 0.6, 1.2))):
        d.add(elm.Line().at(a).to(b).color(TB))
    d.add(elm.Label().at((xr + 2.6, -0.7)).label("RoboClaw input\n3.3 V CMOS, 5 V tolerant\nVIH 2.3 V, VIL 1.0 V\n"
                                                "10 pF, clamps 0 / 5.5 V", fontsize=9, color=TB))

    d.add(elm.Label().at((0, -6.2)).label(
        "Black: board parts (kicad/robo.kicad_sch).  Grey: test bench.  The same circuit is used for J8-3 (EN1_B), "
        "J10-1 (S3, E-stop), J12-1 (S4) and J13-1 (S5).\nThe esd.cir test drives J8-2 from an IEC 61000-4-2 gun "
        "(150 pF, 330 Ω, ±8 kV) with the cable unplugged; TVS=1 replaces D16 with a 5 V TVS diode.",
        halign="left", fontsize=9))
    d.save(OUT, dpi=120)
print("wrote", OUT)
