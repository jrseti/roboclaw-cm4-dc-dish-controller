* Battery input stage as drawn in kicad/battery-input.kicad_sch,
* plus the parts each output feeds on the first stage of the
* power and Robo sheets.
* VSDx are 0 V sense sources for the TVS currents.
* Nodes: jp = J1 pin 1 (battery +), 0 = PGND/J1 pin 2,
*        vs = Q1 source (fuse common), vm = V_MOTOR, vb = V_BAT,
*        vbf = V_BAT_F (U11 eFuse input), g = Q1 gate.

* Q1: drain on J1+, source to fuses (pins D=5-9, G=4, S=1-3)
MQ1 jp g vs SP40P04NK
R1 g 0 47k
DD2 g vs BZT52C15

* Fuses (cold resistance of Littelfuse 0287 ATO plus holder)
RF1 vs vm {RF1}
RF2 vs vb 17m

* V_MOTOR: D1 TVS and the RoboClaw's own input capacitance (unknown,
* parametrised; ESR in series)
VSD1 vm vmd 0
XD1 0 vmd SMCJ18A
CRC vm crc {CRC}
RCRC crc 0 {ESRRC}
CRCER vm 0 4.7u

* V_BAT: D3 TVS, FB1 bead (BLM31KN121SN1L) into V_BAT_F
VSD3 vb vbd 0
XD3 0 vbd SMCJ18A
RFB vb nfb 10m
LFB nfb vbf 0.2u
RFBP vb vbf 120
* C26 10 uF/50 V derated for DC bias, C25 100 nF, D10 SMBJ18CA.
* U11 is held off by UVLO/dV/dt at plug-in, so its 220 uF output is not seen.
C26 vbf c26 5u
RC26 c26 0 5m
C25 vbf 0 100n
VSD10 vbf vbfd 0
XD10 0 vbfd SMBJ18CA
