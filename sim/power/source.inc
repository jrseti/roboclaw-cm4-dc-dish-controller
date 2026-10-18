* Battery and battery-input stage feeding V_BAT_F (see sim/battery-input).
* Battery VB with 25 mOhm (cell + BMS) and 1 m of cable (17 mOhm, 1 uH),
* Q1 5 mOhm, then F1 to V_MOTOR (RoboClaw) and F2 + FB1 to V_BAT_F.
* IMOT is the RoboClaw's motor current, drawn from V_MOTOR.
VBAT bat 0 {VB}
RBAT bat b1 25m
SPLUG b1 b2 plug 0 SWM
LCAB b2 b3 1u
RCAB b3 jp 17m
RQ1 jp vs 5m
RF1 vs vm 4.5m
CRC vm crc 470u
RCRC crc 0 40m
RF2 vs vb 17m
RFB vb nfb 9m
LFB nfb vbatf 0.2u
RFBP vb vbatf 120
