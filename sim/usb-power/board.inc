* USB port power (kicad/usb.kicad_sch): the 5V rail -> U4 AP22653 -> VBUS,
* which feeds both USB-A ports (USB1) and the two expansion ports (J2).
* The 5V rail itself is the buck from ../power-5v (averaged model) with
* its output capacitors, so U4's load steps load the real 5V supply.
* Nodes: vout = 5V rail (CM4 supply), vbus = VBUS.
.param C46=1f C55=1f ACINJ=0
V12 v12 0 12.6
.include ../power-5v/board.inc

* CM4 (and hub, Ethernet, GPS) load on 5V: 1.4 A
RCM4 vout 0 3.7

* U4, R17 15k: 1.735 A limit. RDS set by each test (65 m typ, 135 m max)
XU4 vout vbusu AP22653 RDS={RDS}
* U4 output current sense, then about 20 mOhm of copper to the connectors
VSU4 vbusu vbusi 0
RTR vbusi vbus 20m

* VBUS capacitors: C7 100 uF tantalum (about 0.1 ohm ESR), C9-C12 and C22
* 5 x 10 uF ceramic (derated to ~6 uF each), C8 100 nF; D8, D9 SMF6.0A
C7 vbus c7 100u
RC7 c7 0 0.1
CVC vbus cvc 30u
RCVC cvc 0 1m
C8 vbus 0 100n
XD8 vbus 0 SMF6A
