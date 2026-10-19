* One field input channel from the Robo sheet (kicad/robo.kicad_sch).
* All six channels are the same circuit:
*   Hall A: J8-2 -> R47 5.1k pull-up, D16, R49 100R + C57 10n -> EN1_A
*   Hall B: J8-3 -> R51, D18, R53 + C59 -> EN1_B
*   E-stop: J10-1 -> R48, D17, R50 + C58 -> S3
*   Limits: J12-1 -> R52, D19, R54 + C60 -> S4;  J13-1 -> R55, D20, R56 + C61 -> S5
* Pins: CONN (terminal block pin), PIN (RoboClaw input), V5 (RC_5V)
.subckt FIELDIN CONN PIN V5 params: TVS=0
RPU V5 CONN 5.1k
* ESD part: TPESD0402G12V polymer as built; TVS=1 swaps in a 5 V TVS diode
RSE1 CONN e1 {TVS > 0.5 ? 1e9 : 1m}
XESD e1 0 POLYESD
RSE2 CONN e2 {TVS > 0.5 ? 1m : 1e9}
XTVS e2 0 TVS5V
RS CONN f 100
CF f 0 10n
* PCB trace from the filter to the RoboClaw socket pin
LTR f PIN 10n
XPIN PIN RCPIN
.ends
