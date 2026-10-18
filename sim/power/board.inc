* Power sheet (kicad/power.kicad_sch) from V_BAT_F to the 12V rail.
* Nodes: vbatf = V_BAT_F (U11 IN_SYS), in = U11 IN, efo = EFUSE_OUT,
*        v12 = 12V rail, q2g = Q2 gate, vo5 = 5V output of the buck model.
* VSEF and VSQ2 are 0 V sense sources for the U11 and Q2 currents.
* The source feeding vbatf (battery, cable, Q1, fuses, FB1) is in each test.

* V_BAT_F input: C26 10 uF/50 V derated, C25 100 nF, D10 SMBJ18CA
C26 vbatf c26 5u
RC26 c26 0 5m
C25 vbatf 0 100n
XD10 0 vbatf SMBJ18CA

* UVLO divider R29/R32 with C30 filter: on at 8.34 V, off at 7.79 V
R29 vbatf uvlo 330k
R32 uvlo 0 56k
C30 uvlo 0 1u
* OVP divider R27/R30: off at 17.96 V, back on at 16.78 V
R27 vbatf ovp 180k
R30 ovp 0 13k

* Q3 reverse-current blocking FET (S = V_BAT_F, D = U11 IN), Q4 its gate pull-down
MQ3 in bgate vbatf NCE6008AS
MQ4 bgate drv vbatf BSS138
C24 in 0 100n

* U11 eFuse: RILIM R26 13k gives IOL = 3.08 A; C29 100 nF on dVdT
XU11 vbatf in efu uvlo ovp pgth dvdt bgate drv pg MX26631 IOL=3.08
C29 dvdt 0 100n
VSEF efu efo 0

* EFUSE_OUT: C27 100 nF, C28 220 uF/35 V electrolytic, D11 SMAJ20A, PGTH divider
C27 efo 0 100n
C28 efo c28 220u
RC28 c28 0 0.3
XD11 0 efo SMAJ20A
R28 efo pgth 82k
R31 pgth 0 10k

* Power switch: Q2 P-FET (S = EFUSE_OUT, D = 12V), R22 gate pull-up, SW1 to GND
MQ2 v12q q2g efo DMP6023LE
VSQ2 v12q v12 0
R22 efo q2g {QSOFT > 0.5 ? 33k : 100k}
SSW1 q2s 0 sw1 0 SWM
* QSOFT=1 tries a slower Q2 turn-on (not on the board; QSOFT=0 is the board
* as drawn): R22 33k, 33k in series with SW1, 47 nF gate-to-drain
RSWS q2g q2s {QSOFT > 0.5 ? 33k : 1m}
CQ2GD q2g v12 {QSOFT > 0.5 ? 47n : 1p}

* 12V rail: LED3 + R23, C47 100 nF, C48-C53 6 x 10 uF/35 V (derated to ~5 uF each)
R23 v12 led 3k
DLED3 led 0 DLED
C47 v12 0 100n
C48 v12 cb 30u
RCB cb 0 1m
* U15 buck (5.16 V, IOUT set by each test)
XU15 v12 vo5 BUCKLOAD IOUT={IOUT}
