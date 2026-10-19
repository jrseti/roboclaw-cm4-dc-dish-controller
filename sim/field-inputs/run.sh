#!/bin/sh
# Runs the field-input simulations with ngspice (brew install ngspice).
# Results go to results/*.dat and *.log; plot.py turns them into PNGs and
# prints the Hall edge timing.
set -e
cd "$(dirname "$0")"
mkdir -p results
for f in 300 1k 3k 10k; do
  printf '.param F=%s\n' "$f" > case.inc
  ngspice -b hall.cir > results/hall_$f.log 2>&1
  mv out.dat results/hall_$f.dat
done
for c in "off 0 100p" "on 1 100p" "off_400p 0 400p" "on_400p 1 400p"; do
  set -- $c
  printf '.param HALLON=%s CC=%s\n' "$2" "$3" > case.inc
  ngspice -b noise.cir > results/noise_$1.log 2>&1
  mv out.dat results/noise_$1.dat
done
ngspice -b switch.cir > results/switch.log 2>&1
mv out.dat results/switch.dat
# 8 kV contact discharge, both polarities, with the polymer part (as built)
# and with a 5 V TVS diode in its place (alternative)
for c in "pos 8k 0" "neg -8k 0" "pos_tvs 8k 1" "neg_tvs -8k 1"; do
  set -- $c
  printf '.param VESD=%s TVS=%s\n' "$2" "$3" > case.inc
  ngspice -b esd.cir > results/esd_$1.log 2>&1
  mv out.dat results/esd_$1.dat
done
rm -f case.inc
grep -H -E '^[a-z0-9_]+ +=' results/*.log
grep -l -i -E 'too small|abort' results/*.log && echo "^^ check these logs" || true
