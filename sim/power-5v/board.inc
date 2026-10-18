* Power_5V sheet (kicad/power_5v.kicad_sch): U15 AP64501 12V -> 5.16 V buck.
* Nodes: v12 = 12V rail (U15 VIN), lx = switch node, vout = 5V rail,
*        fbd = R42/R44 divider, fb = U15 FB pin, comp = COMP.
* VINJ (0 V DC) sits between the divider and FB so loop.cir can inject.
* C46 (feedforward) and C55 (HF pole) are DNP on the board; their values
* come from the parameters C46 and C55 (1 fF = not fitted).

* Input: C47 100 nF, C48-C53 6 x 10 uF/35 V derated to ~5 uF each at 12 V
C47 v12 0 100n
CIN v12 cin 30u
RCIN cin 0 1m

* U15, EN pulled up by R65 100k, C54 100 nF soft-start (20 ms)
XU15 v12 lx vout fb comp ss en AP64501AVG
R65 v12 en 100k
C54 ss 0 100n

* L2 SRP7028A-3R3M: 3.3 uH, 30 mOhm DCR
L2 lx nl 3.3u
RDCR nl vout 30m

* Output: C41-C44 4 x 10 uF/10 V derated to ~6 uF each at 5 V,
* C45 100 uF polymer (15 mOhm), C5 10 uF + C6 100 nF at the CM4 (CM4 sheet)
CCER vout cc 24u
RCC cc 0 0.75m
C45 vout c45 100u
RC45 c45 0 15m
C5 vout c5 6u
RC5 c5 0 3m
C6 vout 0 100n

* Feedback: R42 12k / R44 2.2k (0.1 %) -> 0.8 x (1 + 12/2.2) = 5.164 V
R42 vout fbd 12k
R44 fbd 0 2.2k
C46 vout fbd {C46}
VINJ fbd fb DC 0 AC {ACINJ}

* Compensation: R43 20k + C56 1.2 nF from COMP to GND, C55 optional
R43 comp c56 20k
C56 c56 0 1.2n
C55 comp 0 {C55}
